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
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Fijador"
        verbose_name_plural = "Fijadores"

class Exam(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre")
    stain = models.CharField(max_length=250, null=True, blank=True, verbose_name="Tinción")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Exámen"
        verbose_name_plural = "Exámenes"

class Organ(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Órgano"
        verbose_name_plural = "Órganos"


class OrganLocation(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre de localización")
    organs = models.ManyToManyField(Organ, verbose_name="Órganos")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Localización"
        verbose_name_plural = "Localizaciones"

class Pathology(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre del hallazgo")
    organs = models.ManyToManyField(Organ, verbose_name="Órganos")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Hallazgo"
        verbose_name_plural = "Hallazgos"


class Diagnostic(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre del diagnóstico")
    organs = models.ManyToManyField(Organ, verbose_name="Órganos")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Diagnóstico"
        verbose_name_plural = "Diagnósticos"

class DiagnosticDistribution(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    organs = models.ManyToManyField(Organ)

    def __str__(self):
        return self.name


class DiagnosticIntensity(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    organs = models.ManyToManyField(Organ)

    def __str__(self):
        return self.name


# class QuestionReceptionCondition(models.Model):
#     STATUS = (('a', 'Active'), ('i', 'Inactive'))

#     text = models.CharField(max_length=250, null=True, blank=True)
#     status = models.CharField(max_length=1, choices=STATUS)

#     def __str__(self):
#         return self.text


class Customer(models.Model):
    TYPE_CUSTOMER = (('l', 'Laboratorio'), ('e', 'Empresa'))
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre")
    company = models.CharField(max_length=250, null=True, blank=True, verbose_name="Compañía / Empresa")
    type_customer = models.CharField(
        max_length=1, null=True, blank=True, choices=TYPE_CUSTOMER, verbose_name="Tipo de Cliente")


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cliente"


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
    observation = models.TextField(null=True, blank=True)
    no_order = models.CharField(max_length=250, null=True, blank=True)
    no_caso = models.CharField(max_length=250, null=True, blank=True)
    center = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    sampled_at = models.DateTimeField(null=True, blank=True)
    forms = GenericRelation(Form)
    flag_subflow = models.BooleanField(default=False)
    responsible = models.CharField(max_length=250, null=True, blank=True)
    company = models.CharField(max_length=250, null=True, blank=True)
    no_request = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return str(self.pk)

    @property
    def form(self):
        return self.form.get()

    @property
    def get_subflow(self):
        subflows = EntryForm.objects.filter(no_caso=self.no_caso).order_by('id')
        if subflows.count() > 1:
            for i in range(len(subflows)):
                if subflows[i].pk == self.pk:
                    return str(i+1)
        else:
            return "N/A"

class Identification(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    cage = models.CharField(max_length=250, null=True, blank=True)
    no_fish = models.IntegerField(null=True, blank=True)
    no_container = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    extra_features_detail = models.TextField(null=True, blank=True)
    is_optimum = models.NullBooleanField()
    observation = models.TextField(null=True, blank=True)
    group = models.CharField(max_length=250, null=True, blank=True)
    temp_id = models.CharField(max_length=250, null=True, blank=True)
    organs = organs = models.ManyToManyField(Organ)

    def __str__(self):
        return str(self.pk)

# class AnswerReceptionCondition(models.Model):
#     ANSWER = (('si', 'Si'), ('no', 'No'), ('n/a', 'N/A'))

#     question = models.ForeignKey(
#         QuestionReceptionCondition,
#         null=True,
#         on_delete=models.SET_NULL,
#     )
#     # entryform = models.ForeignKey(
#     #     EntryForm,
#     #     null=True,
#     #     on_delete=models.SET_NULL,
#     # )
#     identification = models.ForeignKey(
#         Identification,
#         null=True,
#         on_delete=models.SET_NULL,
#     )
#     answer = models.CharField(max_length=3, choices=ANSWER)

#     def __str__(self):
#         return str(self.pk)


class AnalysisForm(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.SET_NULL)
    # no_fish = models.IntegerField(null=True, blank=True)
    forms = GenericRelation(Form)
    comments = models.TextField(blank=True, null=True)

class Sample(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(null=True, blank=True)
    exams = models.ManyToManyField(Exam)
    organs = models.ManyToManyField(Organ)
    # cassette = models.ForeignKey(Cassette, null=True, on_delete=models.SET_NULL)
    identification = models.ForeignKey(Identification, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.index)

class Cassette(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(null=True, blank=True)
    cassette_name = models.CharField(max_length=250, null=True, blank=True)
    processor_loaded_at = models.DateTimeField(null=True, blank=True)
    # identifications = models.ManyToManyField(Identification)
    sample = models.ForeignKey(Sample, null=True, on_delete=models.SET_NULL)
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
    cassette = models.ForeignKey(Cassette, null=True, on_delete=models.SET_NULL)
    analysis = models.ForeignKey(AnalysisForm, null=True, on_delete=models.SET_NULL)
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(null=True, blank=True)

class Img(models.Model):
    file = models.ImageField(upload_to='vehice_images')
    desc = models.TextField(blank=True, null=True)
    time_stamp = models.DateTimeField(auto_now_add=True)

    @property
    def is_new(self):
        return timezone.now() - timedelta(minutes=1) <= self.time_stamp

class Report(models.Model):
    analysis = models.ForeignKey(
        AnalysisForm, null=True, on_delete=models.SET_NULL)
    slice = models.ForeignKey(Slice, null=True, on_delete=models.SET_NULL)
    organ = models.ForeignKey(Organ, null=True, on_delete=models.SET_NULL)
    organ_location = models.ForeignKey(
        OrganLocation, null=True, on_delete=models.SET_NULL)
    pathology = models.ForeignKey(
        Pathology, null=True, on_delete=models.SET_NULL)
    diagnostic = models.ForeignKey(
        Diagnostic, null=True, on_delete=models.SET_NULL)
    diagnostic_distribution = models.ForeignKey(
        DiagnosticDistribution, null=True, on_delete=models.SET_NULL)
    diagnostic_intensity = models.ForeignKey(
        DiagnosticIntensity, null=True, on_delete=models.SET_NULL)
    images = models.ManyToManyField(Img)
    identification = models.ForeignKey(
        Identification, null=True, on_delete=models.SET_NULL)

class ReportFinal(models.Model):
    analysis = models.ForeignKey(
        AnalysisForm, null=True, on_delete=models.SET_NULL)
    box_findings = models.TextField(null=True, blank=True)
    box_diagnostics = models.TextField(null=True, blank=True)
    box_comments = models.TextField(null=True, blank=True)
    box_tables = models.TextField(null=True, blank=True)