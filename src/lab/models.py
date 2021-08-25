from datetime import datetime

from django.db import connections, models
from django.urls import reverse

from backend.models import (
    AnalysisForm,
    ENTRY_FORMAT_OPTIONS,
    EntryForm,
    Exam,
    Identification,
    Organ,
    OrganUnit,
    Sample,
    SampleExams,
    Stain,
    Unit,
)
from django.contrib.auth.models import User


class Analysis(AnalysisForm):
    """
    Proxy class for :model:`backend.AnalysisForm` to add
    custom methods for app Lab without modifying the original
    model.
    """

    def lab_progress(self):
        """
        Returns an integer representing the percentage progress
        of an Analysis's processing in a Lab

        The progress is calculated according to how many unit_organs with
        the Analysis' exam already have a slide, if they don't have a slide
        then a Cassette it's looked instead, and if it doesn't have either
        then no progress is added.
        """
        case_samples = self.entryform.sample_set.all()
        case_identifications = self.entryform.identification_set.all()
        case_units = Unit.objects.filter(
            identification_id__in=case_identifications.values_list("id", flat=True)
        )
        analysis_exam = self.exam
        case_samples_exams = SampleExams.objects.filter(
            sample_id__in=case_samples.values_list("id", flat=True), exam=analysis_exam
        )
        exam_units_organs = OrganUnit.objects.filter(
            id__in=case_samples_exams.values_list("unit_organ_id", flat=True)
        )

        slides = Slide.objects.filter(
            unit_id__in=exam_units_organs.values_list("unit_id", flat=True),
        )

        total_progress = 0
        total_organs_count = exam_units_organs.count()
        if total_organs_count > 0:
            progress_value = 1 / exam_units_organs.count()
            for slide in slides:
                total_progress += progress_value / 2

                if slide.released_at is not None:
                    total_progress += progress_value / 2

            return min(total_progress * 100, 100)
        return 0

    class Meta:
        proxy = True


class CaseManager(models.Manager):
    """
    Custom Manager for Case, where it mainly filters all :model:`backend.Entryform`
    according to it's current :model:`workflows.Form` state. Alongside some helper
    functions.
    """

    def get_queryset(self):
        return super().get_queryset().filter(forms__cancelled=0, forms__form_closed=0)

    def identifications(self, kwargs_filter={}, kwargs_identifications={}):
        return (
            self.get_queryset()
            .filter(**kwargs_filter)
            .prefetch_related(
                models.Prefetch(
                    "identification_set",
                    Identification.objects.filter(**kwargs_identifications),
                    to_attr="identifications",
                )
            )
        )

    def units(self, kwargs_filter={}, kwargs_identifications={}, kwargs_units={}):
        return (
            self.get_queryset()
            .filter(**kwargs_filter)
            .prefetch_related(
                models.Prefetch(
                    "identification_set",
                    Identification.objects.filter(**kwargs_identifications),
                    to_attr="identifications",
                ),
                models.Prefetch(
                    "identifications__unit_set",
                    Unit.objects.filter(**kwargs_units),
                    to_attr="units",
                ),
            )
            .filter(identification__unit__isnull=False)
        )


class Case(EntryForm):
    """
    Proxy class for :model:`backend.EntryForm`, it's used in the Lab app to filter
    EntryForms AKA Cases according to their status, and order them by priorities,
    without touching the other app's implementation.
    """

    objects = CaseManager()

    def get_absolute_url(self):
        return reverse("lab:case_detail", kwargs={"pk": self.id})

    def units(self):
        identifications = self.identification_set.values_list("id", flat=True)
        return Unit.objects.filter(
            identification_id__in=identifications
        ).select_related("identification__entryform")

    class Meta:
        proxy = True
        ordering = ["-entryform_type_id", "-created_at"]


class UnitManager(models.Manager):
    """
    Custom manager for :model:`backend.Unit` that allows to
    query exams and simplify view's code.
    """

    def pending_cassettes(self, entry_format_list=[1, 2, 6, 7]):
        """
        Returns a queryset including all Units that are waiting
        for :model:`lab.Cassette`.
        """
        units = (
            super()
            .get_queryset()
            .filter(
                cassettes__isnull=True,
                organs__isnull=False,
                identification__entryform__entry_format__in=entry_format_list,
                identification__entryform__id__gt=2034,  # This is the last case before the unit revamp
            )
            .order_by("identification__correlative")
            .distinct()
        )

        units_organ = OrganUnit.objects.filter(
            unit_id__in=units.values_list("id", flat=True)
        )
        sample_exams = SampleExams.objects.filter(
            unit_organ_id__in=units_organ.values_list("id", flat=True),
            exam__service_id__in=[1, 2, 3],
        )
        units_organ = OrganUnit.objects.filter(
            pk__in=sample_exams.values_list("unit_organ_id", flat=True)
        )
        return (
            UnitProxy.objects.filter(
                pk__in=units_organ.values_list("unit_id", flat=True)
            )
            .select_related("identification__entryform")
            .distinct()
        )


class UnitProxy(Unit):
    """Unit proxy to implement custom manager and methods"""

    objects = UnitManager()

    @property
    def exams(self):
        """
        Returns a queryset of all :model:`backend.SampleExams` related through
        :model:`backend.OrganUnit` to a single Unit.
        """
        unit_organs_pk = self.organunit_set.all().values_list("id", flat=True)
        sample_exams = SampleExams.objects.filter(unit_organ_id__in=unit_organs_pk)

        return Exam.objects.filter(
            pk__in=sample_exams.values_list("exam_id", flat=True)
        )

    class Meta:
        proxy = True


class Cassette(models.Model):
    """
    A Cassette is a plastic unit where organs are put and
    processed in formalin to later be converted to blocks.

    It's related to :model:`backend.Entryform` through :model:`backend.Unit`
    """

    correlative = models.PositiveIntegerField()
    organs = models.ManyToManyField(
        Organ, related_name="cassettes", through="CassetteOrgan"
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="cassettes")

    build_at = models.DateTimeField(null=True)
    processed_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.correlative}"

    @property
    def tag(self):
        """
        String identifier of a Cassette used in-situ.
        """
        return f"{self.unit.identification.entryform.no_caso},{self.unit.identification},{self.unit.correlative},{self.correlative}"


class CassetteOrgan(models.Model):
    """Middle table joining Cassette with multiple Organ.
    As a :model:`lab.Cassette` may have multiple of the same :model:`backend.Organ`
    a middle table is necessary.
    """

    cassette = models.ForeignKey(Cassette, on_delete=models.CASCADE)
    organ = models.ForeignKey(Organ, on_delete=models.CASCADE)

    class Meta:
        db_table = "lab_cassette_organ"


class UnitDifference(models.Model):
    STATUS = ((0, "SIN CORREGIR"), (1, "CORREGIDO"))
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    organ = models.ForeignKey(Organ, on_delete=models.CASCADE)
    difference = models.IntegerField()

    status = models.PositiveSmallIntegerField(choices=STATUS, default=0)
    status_change_log = models.TextField(null=True, blank=True)
    status_changed_at = models.DateTimeField(null=True, blank=True)
    status_changed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Slide(models.Model):
    """
    A Slide contains a cut after it's stained, it can be
    digitalized using a scanner or delivered in a folder to
    pathologists.

    Either way, the system must be able to locate the digital version
    which is located in a different database connection["dsstore"],
    and is search for using the :model:`backend.EntryForm`.no_caso,
    and the Slide's stain and correlative.
    """

    cassette = models.ForeignKey(
        Cassette, on_delete=models.CASCADE, related_name="slides", null=True
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="slides")
    stain = models.ForeignKey(Stain, on_delete=models.CASCADE, related_name="slides")
    correlative = models.PositiveIntegerField()

    build_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.correlative}"

    @property
    def tag(self):
        """
        A Tag is a string identifier used in third party services and
        in-site lab.
        """
        no_caso = self.unit.identification.entryform.no_caso[1::]
        stain = self.stain.abbreviation.replace(" ", ",").replace("+", ",").upper()
        correlative = str(self.correlative).zfill(3)

        return f"{no_caso},{stain},{correlative}"

    @property
    def organs(self):
        if self.cassette:
            return self.cassette.organs.all()

        if self.unit:
            return self.unit.organs.all()

        return Organ.objects.none()

    def get_absolute_url(self):
        """
        Returns a URL string with a `guess` from what a
        Slide view in DsStore is located.
        """
        tag = self.tag

        with connections["dsstore"].cursor() as cursor:
            cursor.execute(
                "SELECT ds.id, ds.ImportTime FROM DSStore_Slide ds WHERE ds.Name LIKE %s",
                [tag],
            )

            row = cursor.fetchone()

        if row:
            slide_id = row[0]
            if not self.released_at:
                release_date = row[1]
                self.released_at = release_date
                self.save()

            return f"http://vehice.net/DSStore/HtmlViewer.aspx?Id={slide_id}"
        return row


class Process(models.Model):
    """Describes a Laboratory's internal jobs."""

    name = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "processes"


class CaseProcessTree(models.Model):
    """
    Describes the process tree which a :model:`lab.Case`
    must fulfill to be considered `done` (In lab terms).
    """

    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


class ProcessUnit(models.Model):
    """Details a single :model:`lab.CaseProcess`.
    Stores the date in which the operation started, ended, and wether or raise not
    this was the last operation for this particular :model:`lab.Process` for the
    :model:`backend.EntryForm`.
    """

    case_process = models.ForeignKey(
        CaseProcessTree, on_delete=models.CASCADE, related_name="process_units"
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="processes")

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


class Tree(models.Model):
    """Groups :model:`lab.Process` for a :model:`backend.Exam` must take."""

    name = models.CharField(max_length=255)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True)
    entry_format = models.IntegerField(
        choices=ENTRY_FORMAT_OPTIONS, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class TreeProcess(models.Model):
    """Details which :model:`lab.Process` belong to which :model:`lab.Tree`"""

    tree = models.ForeignKey(Tree, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.tree.name} - {self.process.name} despues de: {self.parent}"
