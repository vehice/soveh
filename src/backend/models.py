from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from workflows.models import Form
from accounts.models import User


def entry_files_directory_path(instance, filename):
    return 'uploads/template/{0}/{1}'.format(instance.template.name, filename)

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

class Service(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre")
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

class Research(models.Model):
    code = models.CharField(max_length=250, null=True, blank=True, verbose_name="Código")
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    status = models.BooleanField(default=False, verbose_name="¿Activo?")

    def __str__(self):
        return self.code + ' ' + self.name

    class Meta:
        verbose_name = "Estudio"
        verbose_name_plural = "Estudios"

PRICING_UNIT = (
    (1, "Por órgano"),
    (2, "Por pez")
)

class Exam(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre")
    stain = models.CharField(max_length=250, null=True, blank=True, verbose_name="Tinción")
    pathologists_assignment = models.BooleanField(default=True, verbose_name="Asignación de patólogo")
    pricing_unit = models.IntegerField(default=1, choices=PRICING_UNIT, verbose_name="Unidad de cobro")
    service = models.ForeignKey(Service, null=True, default=1, on_delete=models.SET_NULL, verbose_name="Tipo de Servicio")
    

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Exámen"
        verbose_name_plural = "Exámenes"


ORGAN_TYPE = (
    (1, "Órgano por sí solo"),
    (2, "Conjunto de órganos")
)

class Organ(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre (ESP)")
    abbreviation = models.CharField(max_length=250, null=True, blank=True, verbose_name="Abreviatura (ESP)")
    name_en = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre (EN)")
    abbreviation_en = models.CharField(max_length=250, null=True, blank=True, verbose_name="Abreviatura (EN)")
    organ_type = models.IntegerField(default=1, choices=ORGAN_TYPE, verbose_name="Tipo")

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

class EntryForm_Type(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tipo de Ingreso"
        verbose_name_plural = "Tipos de Ingreso"

class CaseFile(models.Model):
    file = models.FileField(upload_to='vehice_case_files')
    loaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    
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
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    anamnesis = models.TextField(null=True, blank=True)
    entryform_type = models.ForeignKey(
        EntryForm_Type,
        null=True,
        on_delete=models.SET_NULL,
    )
    attached_files = models.ManyToManyField(CaseFile)
    score_diagnostic = models.FloatField(default=None, null=True, blank=True)
    score_report = models.FloatField(default=None, null=True, blank=True)
    

    def __str__(self):
        return str(self.pk)

    @property
    def form(self):
        return self.form.get()

    @property
    def get_subflow(self):
        subflows = EntryForm.objects.filter(no_caso=self.no_caso, forms__cancelled=0).order_by('id')
        if subflows.count() > 1:
            for i in range(len(subflows)):
                if subflows[i].pk == self.pk:
                    return str(i+1)
        else:
            return "N/A"

class Identification(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    cage = models.CharField(max_length=250, default="", null=True, blank=True)
    no_fish = models.IntegerField(default="0", null=True, blank=True)
    no_container = models.IntegerField(default="0", null=True, blank=True)
    weight = models.FloatField(default="0", null=True, blank=True)
    extra_features_detail = models.TextField(default="", null=True, blank=True)
    is_optimum = models.NullBooleanField()
    observation = models.TextField(default="", null=True, blank=True)
    group = models.CharField(default="", max_length=250, null=True, blank=True)
    temp_id = models.CharField(default="",max_length=250, null=True, blank=True)
    organs = models.ManyToManyField(Organ)
    organs_before_validations = models.ManyToManyField(Organ, related_name='organs_before_validations')
    removable = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)

class ServiceComment(models.Model):
    text = models.TextField(blank=True, null=True)
    done_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

class ExternalReport(models.Model):
    file = models.FileField(upload_to='vehice_external_reports')
    loaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

class AnalysisForm(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.SET_NULL)
    # no_fish = models.IntegerField(null=True, blank=True)
    forms = GenericRelation(Form)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    patologo = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    service_comments = models.ManyToManyField(ServiceComment)
    external_reports = models.ManyToManyField(ExternalReport)
    assignment_done_at = models.DateTimeField(default=None, blank=True, null=True)
    assignment_deadline = models.DateTimeField(default=None, blank=True, null=True)
    assignment_comment = models.TextField(default="", blank=True, null=True)
    manual_closing_date = models.DateTimeField(default=None, blank=True, null=True)
    manual_cancelled_date = models.DateTimeField(default=None, blank=True, null=True)
    pre_report_started = models.BooleanField(default=False)
    pre_report_started_at = models.DateTimeField(default=None, blank=True, null=True)
    pre_report_ended = models.BooleanField(default=False)
    pre_report_ended_at = models.DateTimeField(default=None, blank=True, null=True)
    report_code = models.CharField(max_length=250, null=True, blank=True)
    researches = models.ManyToManyField(Research)
    score_diagnostic = models.FloatField(default=None, null=True, blank=True)
    score_report = models.FloatField(default=None, null=True, blank=True)

    @property
    def status(self):
        if self.forms.get().form_closed:
            status = "Finalizado"
        elif self.forms.get().cancelled:
            status = "Anulado"
        elif self.exam.pathologists_assignment and self.pre_report_started and not self.pre_report_ended:
            status = "Lectura Iniciada"
        elif self.exam.pathologists_assignment and self.pre_report_started and self.pre_report_ended:
            status = "Pre-Informe Terminado"
        else:
            status = "En Curso"
        return status

class Sample(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(null=True, blank=True)
    # exams = models.ManyToManyField(Exam)
    # organs = models.ManyToManyField(Organ)
    # cassette = models.ForeignKey(Cassette, null=True, on_delete=models.SET_NULL)
    identification = models.ForeignKey(Identification, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.index)

class SampleExams(models.Model):
    sample = models.ForeignKey(Sample, null=True, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.CASCADE)
    # analysis = models.ForeignKey(AnalysisForm, null=True, on_delete=models.CASCADE)
    organ = models.ForeignKey(Organ, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.sample)

class Cassette(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(null=True, blank=True)
    cassette_name = models.CharField(max_length=250, null=True, blank=True)
    processor_loaded_at = models.DateTimeField(null=True, blank=True)
    # identifications = models.ManyToManyField(Identification)
    samples = models.ManyToManyField(Sample)
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
        return datetime.timezone.now() - datetime.timedelta(minutes=1) <= self.time_stamp

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
    sample = models.ForeignKey(Sample, null=True, on_delete=models.SET_NULL)

class ReportFinal(models.Model):
    analysis = models.ForeignKey(
        AnalysisForm, null=True, on_delete=models.SET_NULL)
    no_reporte = models.CharField(max_length=250, null=True, blank=True)
    box_findings = models.TextField(null=True, blank=True)
    box_diagnostics = models.TextField(null=True, blank=True)
    box_comments = models.TextField(null=True, blank=True)
    box_tables = models.TextField(null=True, blank=True)

class Responsible(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True)
    email = models.CharField(max_length=250, null=True, blank=True)
    phone = models.CharField(max_length=250, null=True, blank=True)
    job = models.CharField(max_length=250, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Responsable"
        verbose_name_plural = "Responsables"

class EmailCcTo(models.Model):
    email = models.CharField(max_length=250, null=True, blank=True, verbose_name="Correo Electrónico")

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = "Destinatario copiado en Plantilla Email"
        verbose_name_plural = "Destinatarios copiados en Plantilla Email"

class EmailTemplate(models.Model):
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Nombre")
    body = models.TextField(max_length=1000, null=True, blank=True, verbose_name="Mensaje")
    cc = models.ManyToManyField(EmailCcTo, verbose_name="Copia para", blank=True)
    
    class Meta:
        verbose_name = "Plantilla Email"
        verbose_name_plural = "Plantillas Emails"

class EmailTemplateAttachment(models.Model):
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.CASCADE)
    template_file = models.FileField(
        upload_to=entry_files_directory_path, verbose_name="Archivo Adjunto")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Email Adjunto"
        verbose_name_plural = "Email Adjuntos"
        
class CaseVersion(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    version = models.IntegerField(null=True, blank=True)
    generated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    generated_at = models.DateTimeField(auto_now_add=True)

RESUME_DOCUMENT_LANG =(
    (1, "es"),
    (2, "en"),
)

class DocumentCaseResume(models.Model):
    entryform = models.ForeignKey(
        EntryForm, null=True, on_delete=models.SET_NULL)
    filename = models.CharField(max_length=250, null=True, blank=True)
    file = models.FileField(upload_to='pdfs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    lang = models.IntegerField(choices=RESUME_DOCUMENT_LANG, default=1)
    case_version = models.ForeignKey(CaseVersion, null=True, on_delete=models.SET_NULL)
    version = models.IntegerField(null=True, blank=True)
    generated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.filename

class DocumentResumeActionLog(models.Model):
    document = models.ForeignKey(DocumentCaseResume, null=True, on_delete=models.SET_NULL)
    mail_action = models.BooleanField(default=False)
    download_action = models.BooleanField(default=False)
    action_date = models.DateTimeField(auto_now_add=True)
    done_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)


