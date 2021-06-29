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

    case = models.ManyToManyField(
        EntryForm, related_name="processes", through="CaseProcess"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "processes"


class Tree(models.Model):
    """Describes a Laboratory's group of process."""

    name = models.CharField(max_length=255)

    process = models.ManyToManyField(
        Process, related_name="process", through="ProcessTree"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class ProcessTree(models.Model):
    """Details the order in which :model:`lab.Process` take place in a :model:`lab.Tree`."""

    process = models.ForeignKey(
        Process, on_delete=models.CASCADE, related_name="process_trees"
    )
    tree = models.ForeignKey(
        Tree, on_delete=models.CASCADE, related_name="process_trees"
    )
    order = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.process} en {self.tree}"


class ExamTree(models.Model):
    """Details the order in which :model:`lab.Tree` take place in a :model:`backend.Exam`"""

    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="exam_trees")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="exam_trees")
    order = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tree} en {self.exam} como paso {self.order}"


class CaseProcess(models.Model):
    """Details the order in which :model:`lab.Process` takes place in a :model:`backend.EntryForm`"""

    case = models.ForeignKey(
        EntryForm, on_delete=models.CASCADE, related_name="case_process"
    )
    process = models.ForeignKey(
        Process, on_delete=models.CASCADE, related_name="case_process"
    )
    order = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)


class ProcessUnit(models.Model):
    """Details a single :model:`lab.CaseProcess`.
    Stores the date in which the operation started, ended, and wether or raise not
    this was the last operation for this particular :model:`lab.Process` for the
    :model:`backend.EntryForm`.
    """

    case_process = models.ForeignKey(
        CaseProcess, on_delete=models.CASCADE, related_name="process_items"
    )

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(verbose_name="finalizado")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
