from django.db import models
from workflows.models import Flow


class Specie(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class WaterSource(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class LarvalStage(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class Fixative(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class Exam(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class Organ(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class QuestionReceptionCondition(models.Model):
    STATUS = (('a', 'Active'), ('i', 'Inactive'))

    text = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS)

    def __str__(self):
        return self.text


class Customer(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    company = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class EntryForm(models.Model):
    form_id = models.CharField(max_length=250, null=True, blank=True)
    flow = models.OneToOneField(Flow, null=True, on_delete=models.SET_NULL)
    specie = models.ForeignKey(Specie, null=True, on_delete=models.SET_NULL)

    watersource = models.ForeignKey(
        WaterSource,
        null=True,
        on_delete=models.SET_NULL,
    )
    larvalstage = models.ForeignKey(
        LarvalStage,
        null=True,
        on_delete=models.SET_NULL,
    )
    fixative = models.ForeignKey(
        Fixative,
        null=True,
        on_delete=models.SET_NULL,
    )
    customer = models.ForeignKey(
        Customer, null=True, on_delete=models.SET_NULL)
    questionreceptionconditions = models.ManyToManyField(
        QuestionReceptionCondition, through='AnswerReceptionCondition')
    observation = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sampled_at = models.DateTimeField(null=True, blank=True)


class AnswerReceptionCondition(models.Model):
    ANSWER = (('si', 'Si'), ('no', 'No'), ('n/a', 'N/A'))

    question = models.ForeignKey(
        QuestionReceptionCondition,
        null=True,
        on_delete=models.SET_NULL,
    )
    entryform = models.ForeignKey(
        EntryForm,
        null=True,
        on_delete=models.SET_NULL,
    )
    answer = models.CharField(max_length=3, choices=ANSWER)
