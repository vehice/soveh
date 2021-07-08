from datetime import datetime

from django.db import connections, models
from django.urls import reverse
from numpy import busday_count

from backend.models import (
    ENTRY_FORMAT_OPTIONS,
    EntryForm,
    Exam,
    Identification,
    Organ,
    Sample,
    SampleExams,
    Stain,
    Unit,
)


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
        )


class Case(EntryForm):
    """
    Proxy class for :model:`backend.EntryForm`, it's used in the Lab app to filter
    EntryForms AKA Cases according to their status, and order them by priorities,
    without touching the other app's implementation.
    """

    objects = CaseManager()

    @property
    def delay(self):
        days = 0
        try:
            days = busday_count(
                self.created_at.date(), datetime.now().date(), weekmask="1111110"
            )
        except AttributeError:
            days = 0
        return days

    def get_absolute_url(self):
        return reverse("lab:case_detail", kwargs={"pk": self.id})

    def generate_process_list(self):
        samples = Sample.objects.filter(entryform=self).values_list("id", flat=True)
        sample_exams = (
            SampleExams.objects.filter(sample__in=samples)
            .values_list("exam_id", flat=True)
            .distinct()
        )
        exam_tree = ExamTree.objects.filter(exam_id__in=sample_exams).order_by("order")
        processes = []
        for tree in exam_tree:
            process_tree = (
                ProcessTree.objects.filter(tree_id=tree.id)
                .values_list("process_id", flat=True)
                .order_by("order")
                .distinct()
            )
            processes.extend(process_tree)

        order = 1
        for process in processes:
            CaseProcess.objects.create(case=self, process_id=process, order=order)
            order += 1

        return CaseProcess.objects.filter(case=self).order_by("order")

    class Meta:
        proxy = True
        ordering = ["-entryform_type_id", "-created_at"]


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


class CassetteOrgan(models.Model):
    """Middle table joining Cassette with multiple Organ.
    As a :model:`lab.Cassette` may have multiple of the same :model:`backend.Organ`
    a middle table is necessary.
    """

    cassette = models.ForeignKey(Cassette, on_delete=models.CASCADE)
    organ = models.ForeignKey(Organ, on_delete=models.CASCADE)

    class Meta:
        db_table = "lab_cassette_organ"


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
    build_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.correlative}"

    @property
    def tag(self):
        no_caso = self.unit.identification.entryform.no_caso[1::]
        stain = self.stain.abbreviation.replace(" ", ",").replace("+", ",").upper()
        correlative = str(self.correlative).zfill(3)

        return f"{no_caso},{stain},{correlative}"

    def get_absolute_url(self):
        tag = self.tag

        with connections["dsstore"].cursor() as cursor:
            cursor.execute(
                "SELECT ds.id FROM DSStore_Slide ds WHERE ds.Name LIKE %s", [tag]
            )

            row = cursor.fetchone()

        if row:
            slide_id = row[0]

            return f"http://vehice.net/DSStore/HtmlViewer.aspx?Id=${slide_id}"
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
