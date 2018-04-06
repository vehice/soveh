from django.db import models


class Actor(models.Model):  # SE RELACIONA CON USUARIO
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class Flow(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    state = models.OneToOneField(State, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Step(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    actors = models.ForeignKey(
        Actor,
        null=True,
        on_delete=models.SET_NULL,
    )
    state = models.OneToOneField(
        State,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    flow = models.ForeignKey(Flow, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
