from django.db import models

from django.contrib.auth.models import User
from backend.models import AnalysisForm
from django.db.models import Q

from backend.models import Customer


class AnalysisManager(models.Manager):
    """
    Custom Manager for Case, where it mainly filters all :model:`backend.Entryform`
    according to it's current :model:`workflows.Form` state. Alongside some helper
    functions.
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                forms__form_closed=0,
                forms__cancelled=0,
                manual_cancelled_date__exact=None,
                manual_closing_date__exact=None,
            )
        )

    def waiting(self):
        """
        Returns all :model:`backend.AnalysisForm` which a Pathologist
        has finished studying but hasn't being reviewed yet.
        """
        return (
            self.get_queryset()
            .filter(
                Q(
                    exam__pathologists_assignment=True,
                    pre_report_started=True,
                    pre_report_ended=True,
                    stages__isnull=True,
                )
                | Q(stages__state=0)
            )
            .select_related("entryform", "exam", "stain")
        )

    def stage(self, state_index):
        """
        Returns all :model:`backend.AnalysisForm` according to it's
        :model:`review.Stage`.STATE index.
        """

        return (
            self.get_queryset()
            .filter(stages__state=state_index)
            .select_related("entryform", "exam", "stain")
        )


class Analysis(AnalysisForm):
    """
    Proxy class for :model:`backend.AnalysisForm`, it's used in the Review app to filter
    AnalysisForm according to their status, and order them by priorities,
    without touching the other app's implementation.
    """

    objects = AnalysisManager()

    class Meta:
        proxy = True


class Stage(models.Model):
    """
    Details a single stage in which an :model:`review.Analysis` is currently at.
    """

    STATES = (
        (0, "ESPERA"),
        (1, "FORMATO"),
        (2, "REVISION"),
        (3, "ENVIO"),
        (4, "FINALIZADO"),
    )

    analysis = models.ForeignKey(
        AnalysisForm, on_delete=models.CASCADE, related_name="stages"
    )
    state = models.CharField(max_length=1, choices=STATES, default=0)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="review_stages", null=True
    )
    created_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Logbook.objects.create(stage=self, state=self.state, user=self.created_by)


class Logbook(models.Model):
    """
    Stores detailed information relate to a :model:`review.Stage` changes.
    """

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="logbooks")

    state = models.CharField(max_length=1, choices=Stage.STATES)

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="logbooks", null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class File(models.Model):
    """Stores a single file path in the database alognside it's related :model:`review.Stage`"""

    path = models.FileField("reviews/%Y_%m_%d/")
    analysis = models.ForeignKey(
        Analysis, on_delete=models.CASCADE, related_name="files"
    )
    state = models.CharField(max_length=1, choices=Stage.STATES)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="files", null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Recipient(models.Model):
    """
    Stores a single resource which will receive an email with :model:`review.File` for it's related
    :model:`review.Analysis` whenever this it's moved to a :model:`review.Stage` finished.
    """

    email = models.EmailField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class MailList(models.Model):
    """
    Allows grouping multiple :model:`review.Recipient` under the same :model:`backend.Customer`
    """

    name = models.CharField(max_length=255)
    customer = models.ForeignKey(
        to=Customer, on_delete=models.CASCADE, related_name="mailing_lists"
    )
    recipients = models.ManyToManyField(to=Recipient, related_name="mailing_lists")
    analysis = models.ManyToManyField(
        to=Analysis, related_name="mailing_lists", through="AnalysisMailList"
    )

    def __str__(self):
        return self.name


class AnalysisMailList(models.Model):
    """
    A :model:`review.Analysis` may contain multiple :model:`review.MailList` and vice-versa thus this model works
    as a middle-man to join them.
    """

    analysis = models.ForeignKey(to=Analysis, on_delete=models.CASCADE)
    mail_list = models.ForeignKey(to=MailList, on_delete=models.CASCADE)
