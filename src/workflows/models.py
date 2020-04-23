from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from accounts.models import Profile


class State(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class Flow(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    parent = models.ForeignKey(
        'self', null=True, related_name='child', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Permission(models.Model):
    PERMISSION = (('w', 'Write'), ('a', 'Authorize'), ('r', 'Read'))

    name = models.CharField(max_length=250, null=True, blank=True)
    type_permission = models.CharField(max_length=1, choices=PERMISSION)
    from_state = models.ForeignKey(
        State,
        null=True,
        on_delete=models.SET_NULL,
        related_name="permission_from_state")
    to_state = models.ForeignKey(
        State,
        null=True,
        on_delete=models.SET_NULL,
        related_name="permission_to_state")

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    permission = models.ManyToManyField(Permission)
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Step(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    tag = models.CharField(max_length=250, null=True, blank=True)
    state = models.OneToOneField(
        State,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    flow = models.ForeignKey(Flow, null=True, on_delete=models.SET_NULL)
    route = models.CharField(max_length=250, null=True, blank=True)
    order = models.PositiveIntegerField(null=True)
    actors = models.ManyToManyField(Actor)

    class Meta:
        unique_together = ('flow', 'order')
        ordering = ['order']

    def __str__(self):
        return self.name


class Form(models.Model):
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    form_closed = models.BooleanField(default=False)
    form_reopened = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        related_name='children',
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()
    deleted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True)
    closed_at = models.DateTimeField(null=True)


    def __str__(self):
        return str(self.content_type)
