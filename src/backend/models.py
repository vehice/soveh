from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from workflows.models import Form


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
    TYPE_CUSTOMER = (('l', 'Laboratory'), ('s', 'Salmon Farming'))
    name = models.CharField(max_length=250, null=True, blank=True)
    company = models.CharField(max_length=250, null=True, blank=True)
    type_customer = models.CharField(
        max_length=1, null=True, blank=True, choices=TYPE_CUSTOMER)

    def __str__(self):
        return self.name


class EntryForm(models.Model):
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
    no_order = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    sampled_at = models.DateTimeField(null=True, blank=True)
    forms = GenericRelation(Form, related_query_name='form')

    def __str__(self):
        return str(self.pk)

    @property
    def form(self):
        return self.forms.get()


class Identification(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    cage = models.CharField(max_length=250, null=True, blank=True)
    no_fish = models.IntegerField(null=True, blank=True)
    no_container = models.IntegerField(null=True, blank=True)
    group = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return str(self.pk)


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

    def __str__(self):
        return str(self.pk)
