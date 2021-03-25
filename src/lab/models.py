from django.db import models

from backend.models import EntryForm, Organ, Unit


class CaseManager(models.Manager):
    """
    Custom Manager for Case, where it mainly filters all :model:`backend.Entryform`
    according to it's current :model:`workflows.Form` state. Alongside some helper
    functions.
    """

    def get_queryset(self):
        return super().get_queryset().filter(forms__cancelled=0, forms__form_closed=0)

    def identifications(self, **kwargs):
        return (
            self.get_queryset()
            .filter(**kwargs)
            .prefetch_related(
                models.Prefetch("identification_set", to_attr="identifications")
            )
        )

    def units(self, **kwargs):
        return (
            self.get_queryset()
            .filter(**kwargs)
            .prefetch_related(
                models.Prefetch("identification_set", to_attr="identifications"),
                models.Prefetch("identifications__unit_set", to_attr="units"),
            )
        )


class Case(EntryForm):
    """
    Proxy class for :model:`backend.EntryForm`, it's used in the Lab app to filter
    EntryForms AKA Cases according to their status, and order them by priorities,
    without touching the other app's implementation.
    """

    objects = CaseManager()

    class Meta:
        proxy = True


class Cassette(models.Model):
    """
    A Cassette is a plastic unit where organs are put and
    processed in formalin to later be converted to blocks.

    A Cassette is turned into one :models:`lab.Block`.
    It's related to :models:`backend.EntryForm` through :models:`backend.Unit`
    """

    correlative = models.PositiveIntegerField(verbose_name="correlative")
    organs = models.ManyToManyField(Organ, related_name="cassettes")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="cassettes")
    build_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    processed_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)