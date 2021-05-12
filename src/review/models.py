from django.db import models

from django.contrib.auth.models import User
from backend.models import AnalysisForm


class AnalysisManager(models.Manager):
    """
    Custom Manager for Case, where it mainly filters all :model:`backend.Entryform`
    according to it's current :model:`workflows.Form` state. Alongside some helper
    functions.
    """

    def pre_report_done(self):
        """
        Returns all :model:`backend.AnalysisForm` which a Pathologist
        has finished studying but hasn't being reviewed yet.
        """
        return (
            self.get_queryset()
            .filter(
                exam__pathologists_assignment=True,
                pre_report_started=True,
                pre_report_ended=True,
                forms__form_closed=False,
                forms__cancelled=False,
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
            .filter(stages__state=Stage.STATES[state_index])
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

    STATES = ((0, "FORMATO"), (1, "REVISION"), (2, "ENVIO"), (3, "FINALIZADO"))

    analysis = models.ForeignKey(
        AnalysisForm, on_delete=models.CASCADE, related_name="stages"
    )
    state = models.CharField(max_length=1, choices=STATES, default=0)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="review_stages", null=True
    )
    created_at = models.DateTimeField(auto_now=True)


class Logbook(models.Model):
    """
    Stores detailed information relate to a :model:`review.Stage` changes.
    """

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="logbooks")

    previous = models.CharField(max_length=1, choices=Stage.STATES)
    current = models.CharField(max_length=1, choices=Stage.STATES)

    date = models.DateTimeField()
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="logbooks", null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
