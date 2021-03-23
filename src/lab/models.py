from django.db import models

from backend.models import EntryForm, Organ


class Cassette(models.Model):
    """
    A Cassette is a plastic unit where organs are put and
    processed in formalin to later be converted to blocks.

    A Cassette is turned into one :models:`lab.Block`.
    """

    correlative = models.PositiveIntegerField(verbose_name="correlative")
    organs = models.ManyToManyField(Organ, related_name="cassettes")
    unit = models.ForeignKey("Unit", on_delete=models.CASCADE)
    build_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    processed_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
