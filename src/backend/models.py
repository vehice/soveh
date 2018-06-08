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
    stain = models.CharField(max_length=250, null=True, blank=True)

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
    no_order = models.CharField(max_length=250, null=True, blank=True)
    center = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    sampled_at = models.DateTimeField(null=True, blank=True)
    forms = GenericRelation(Form)

    def __str__(self):
        return str(self.pk)

    @property
    def form(self):
        return self.form.get()


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


class AnalysisForm(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.SET_NULL)
    organs = models.ManyToManyField(Organ)
    no_fish = models.IntegerField(null=True, blank=True)
    forms = GenericRelation(Form)


class Cassette(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    sample_id = models.CharField(max_length=250, null=True, blank=True)
    cassette_name = models.CharField(max_length=250, null=True, blank=True)
    identifications = models.ManyToManyField(Identification)
    organs = models.ManyToManyField(Organ)


class Slice(models.Model):
    slice_name = models.CharField(max_length=250, null=True, blank=True)
    start_block = models.DateTimeField(null=True, blank=True)
    end_block = models.DateTimeField(null=True, blank=True)
    start_slice = models.DateTimeField(null=True, blank=True)
    end_slice = models.DateTimeField(null=True, blank=True)
    start_scan = models.DateTimeField(null=True, blank=True)
    end_scan = models.DateTimeField(null=True, blank=True)
    start_stain = models.DateTimeField(null=True, blank=True)
    box_id = models.CharField(max_length=250, null=True, blank=True)
    end_stain = models.DateTimeField(null=True, blank=True)
    slice_store = models.CharField(max_length=250, null=True, blank=True)
    cassettes = models.ManyToManyField(Cassette)
    analysis = models.ManyToManyField(AnalysisForm)
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
