from datetime import datetime

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from numpy import busday_count

from accounts.models import User
from workflows.models import Form


def entry_files_directory_path(instance, filename):
    return "uploads/template/{0}/{1}".format(instance.template.name, filename)


class Specie(models.Model):
    """Details information about the sample's species."""

    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class WaterSource(models.Model):
    """Details information about the sample's water source."""

    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class LarvalStage(models.Model):
    """Details information about the sample's growth stage."""

    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Fixative(models.Model):
    """Stores information about the unit's used fixative."""

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "fijador"
        verbose_name_plural = "fijadores"


class Service(models.Model):
    """
    Service defines the workflow to be followed,
    and the analysis availables.
    """

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre"
    )
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "servicio"
        verbose_name_plural = "servicios"


RESEARCH_TYPE_OPTIONS = [(1, "Estudio Vehice"), (2, "Seguimiento de rutina")]


class Research(models.Model):
    """
    Research encapsulates multiple :model:`backend.Entryform`
    with their common data.
    """

    code = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="código"
    )
    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre"
    )
    description = models.TextField(null=True, blank=True, verbose_name="descripción")
    type = models.IntegerField(
        default=1, choices=RESEARCH_TYPE_OPTIONS, verbose_name="tipo"
    )
    init_date = models.DateTimeField(null=True, blank=True)
    clients = models.ManyToManyField("Customer", verbose_name="clientes")
    services = models.ManyToManyField(
        "AnalysisForm", verbose_name="servicios Asociados"
    )
    status = models.BooleanField(default=False, verbose_name="¿activo?")

    # Copy of user full name to avoid empty data if user is removed
    external_responsible = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="responsable externo"
    )
    internal_responsible = models.ForeignKey(
        User, null=True, on_delete=models.PROTECT, verbose_name="responsable interno"
    )

    def __str__(self):
        return self.code + " " + self.name

    class Meta:
        verbose_name = "estudio"
        verbose_name_plural = "estudios"


class Stain(models.Model):
    """
    A stain dyes a sample which allows the Pathologist
    to study certain chemicals reactions on it.

    Certain services :model:`backend.Stain` use a speficic Stain.
    """

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre"
    )
    abbreviation = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="abreviación"
    )
    description = models.TextField(null=True, blank=True, verbose_name="descripción")

    def __str__(self):
        return self.abbreviation

    class Meta:
        verbose_name = "tinción"
        verbose_name_plural = "tinciones"


PRICING_UNIT = ((1, "Por órgano"), (2, "Por pez"))


class Exam(models.Model):
    """Stores basic information about services done by the company."""

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre"
    )
    stain = models.ForeignKey(
        Stain, null=True, on_delete=models.SET_NULL, verbose_name="tinción"
    )
    pathologists_assignment = models.BooleanField(
        default=True, verbose_name="asignación de patólogo"
    )
    pricing_unit = models.IntegerField(
        default=1, choices=PRICING_UNIT, verbose_name="unidad de cobro"
    )
    service = models.ForeignKey(
        Service,
        null=True,
        default=1,
        on_delete=models.SET_NULL,
        verbose_name="tipo de Servicio",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "exámen"
        verbose_name_plural = "exámenes"


ORGAN_TYPE = ((1, "Órgano por sí solo"), (2, "Conjunto de órganos"))


class Organ(models.Model):
    """
    An Organ stores information about the organ itself
    but also helps as a pivot to bind different Findings to it.
    """

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre (ESP)"
    )
    abbreviation = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="abreviatura (ESP)"
    )
    name_en = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre (EN)"
    )
    abbreviation_en = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="abreviatura (EN)"
    )
    organ_type = models.IntegerField(default=1, choices=ORGAN_TYPE, verbose_name="tipo")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "órgano"
        verbose_name_plural = "órganos"


class OrganLocation(models.Model):
    """
    Stores information about the area where an specific Organ can be located.
    """

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre de localización"
    )
    organs = models.ManyToManyField(Organ, verbose_name="órganos")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "localización"
        verbose_name_plural = "localizaciones"


class Pathology(models.Model):
    """Stores information about findings for an Organ."""

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="Nombre del hallazgo"
    )
    organs = models.ManyToManyField(Organ, verbose_name="Órganos")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Hallazgo"
        verbose_name_plural = "Hallazgos"


class Diagnostic(models.Model):
    """
    Stores detailed information about a Diagnostic,
    which can be generated from a Finding and a Localization.
    """

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre del diagnóstico"
    )
    organs = models.ManyToManyField(Organ, verbose_name="órganos")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "diagnóstico"
        verbose_name_plural = "diagnósticos"


class DiagnosticDistribution(models.Model):
    """
    Stores possible distribution level that a diagnostic can have,
    where a distribution is how focused in an area the Finding is.
    """

    name = models.CharField(max_length=250, null=True, blank=True)
    organs = models.ManyToManyField(Organ)

    def __str__(self):
        return self.name


class DiagnosticIntensity(models.Model):
    """
    Stores information about the intensity level of a diagnostic
    """

    name = models.CharField(max_length=250, null=True, blank=True)
    organs = models.ManyToManyField(Organ)

    def __str__(self):
        return self.name


TYPE_CUSTOMER = (("l", "Laboratorio"), ("e", "Empresa"))


class Customer(models.Model):
    """
    Stores detailed information about a Customer that request Services.
    """

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre"
    )
    company = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="empresa"
    )
    type_customer = models.CharField(
        max_length=1,
        null=True,
        blank=True,
        choices=TYPE_CUSTOMER,
        verbose_name="Tipo de Cliente",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "cliente"


class Laboratory(models.Model):
    """
    Entrance Laboratory for Entryform.
    """

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="nombre"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Laboratorio de Ingreso"


class EntryForm_Type(models.Model):
    """
    Stores information a about a entry type, this defines the subsequent
    flow the process will take, as different types require different
    processes.
    """

    name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "tipo de Ingreso"
        verbose_name_plural = "tipos de Ingreso"


class CaseFile(models.Model):
    """Stores information about file uploads related to Cases"""

    file = models.FileField(upload_to="vehice_case_files")
    loaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


ENTRY_FORMAT_OPTIONS = [
    (1, "Tubo"),
    (2, "Cassette"),
    (3, "Bloque"),
    (4, "Slide s/teñir"),
    (5, "Slide teñido"),
    (6, "Vivo"),
    (7, "Muerto"),
]


class EntryForm(models.Model):
    """
    Stores information about a new Case, this is detailed data for the services
    to be done.
    """

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
    laboratory = models.ForeignKey(
        Laboratory,
        null=True,
        on_delete=models.SET_NULL,
    )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    observation = models.TextField(null=True, blank=True)
    no_order = models.CharField(max_length=250, null=True, blank=True)
    no_caso = models.CharField(max_length=250, null=True, blank=True)
    center = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    sampled_at = models.DateTimeField(null=True, blank=True)
    sampled_at_hour = models.CharField(max_length=5, null=True, blank=True)
    sampled_at_am_pm = models.CharField(max_length=2, null=True, blank=True)
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
    attached_files = models.ManyToManyField(CaseFile, blank=True)
    transfer_order = models.CharField(max_length=250, null=True, blank=True)
    entry_format = models.IntegerField(choices=ENTRY_FORMAT_OPTIONS, default=1)

    def __str__(self):
        return f"#{self.pk} - {self.no_caso}"

    @property
    def form(self):
        return self.form.get()

    @property
    def delay(self):
        """Returns an integer despicting the ongoing days counts"""
        days = 0
        try:
            days = busday_count(
                self.created_at.date(), datetime.now().date(), weekmask="1111110"
            )
        except AttributeError:
            days = 0
        return days

    @property
    def get_subflow(self):
        subflows = EntryForm.objects.filter(
            no_caso=self.no_caso, forms__cancelled=0
        ).order_by("id")
        if subflows.count() > 1:
            for i in range(len(subflows)):
                if subflows[i].pk == self.pk:
                    return str(i + 1)
        else:
            return "N/A"

    class Meta:
        verbose_name = "Caso"
        verbose_name_plural = "Casos"


class Identification(models.Model):
    """
    Details information about a group of :model:`backend.Sample` that share the same origin.
    """

    entryform = models.ForeignKey(EntryForm, null=True, on_delete=models.SET_NULL)
    correlative = models.IntegerField(default=1, null=True, blank=True)
    cage = models.CharField(max_length=250, default="", null=True, blank=True)
    quantity = models.IntegerField(default="0", null=True, blank=True)
    client_case_number = models.CharField(
        max_length=250, default="", null=True, blank=True
    )
    weight = models.FloatField(default="0", null=True, blank=True)
    extra_features_detail = models.TextField(default="", null=True, blank=True)
    is_optimum = models.NullBooleanField()
    observation = models.TextField(default="", null=True, blank=True)
    group = models.CharField(default="", max_length=250, null=True, blank=True)
    removable = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    samples_are_correlative = models.BooleanField(default=False)

    # deprecated attr
    temp_id = models.CharField(default="", max_length=250, null=True, blank=True)
    no_fish = models.IntegerField(default="0", null=True, blank=True)
    no_container = models.IntegerField(default="0", null=True, blank=True)
    organs = models.ManyToManyField(Organ)
    organs_before_validations = models.ManyToManyField(
        Organ, related_name="organs_before_validations"
    )

    def __str__(self):
        return f"{self.cage} {self.group} {self.extra_features_detail}"


class Unit(models.Model):
    correlative = models.IntegerField(default=1, null=True, blank=True)
    organs = models.ManyToManyField("Organ", through="OrganUnit")
    identification = models.ForeignKey(
        Identification, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return str(self.correlative)


class OrganUnit(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    organ = models.ForeignKey(Organ, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.unit.identification.entryform.no_caso}-{self.unit.identification}-{self.unit.correlative}: {self.organ.abbreviation}"


class ServiceComment(models.Model):
    """
    Stores comments done by a User related to a specific service in a :model:`backend.AnalysisForm`
    """

    text = models.TextField(blank=True, null=True)
    done_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class ExternalReport(models.Model):
    """
    Stores files uploaded by a User related to a specific service in a :model:`backend.AnalysisForm`

    Files uploaded are stored in the MEDIA_ROOT/vehice_external_reports folder
    """

    file = models.FileField(upload_to="vehice_external_reports")
    loaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


# Service
class AnalysisForm(models.Model):
    """
    An Analysis is the process in which a Pathologists User can store Findings related to a specific service,
    it details the time it took to complete, and serves as a pivot to other models.
    """

    entryform = models.ForeignKey(EntryForm, null=True, on_delete=models.SET_NULL)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.SET_NULL)
    forms = GenericRelation(Form)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    patologo = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, blank=True)
    service_comments = models.ManyToManyField(ServiceComment, blank=True)
    external_reports = models.ManyToManyField(ExternalReport, blank=True)
    assignment_done_at = models.DateTimeField(default=None, blank=True, null=True)
    assignment_deadline = models.DateTimeField(default=None, blank=True, null=True)
    assignment_comment = models.TextField(default="", blank=True, null=True)
    manual_closing_date = models.DateTimeField(default=None, blank=True, null=True)
    manual_cancelled_date = models.DateTimeField(default=None, blank=True, null=True)
    manual_cancelled_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="cancelled_by",
        blank=True,
    )
    pre_report_started = models.BooleanField(default=False)
    pre_report_started_at = models.DateTimeField(default=None, blank=True, null=True)
    pre_report_ended = models.BooleanField(default=False)
    pre_report_ended_at = models.DateTimeField(default=None, blank=True, null=True)
    report_code = models.CharField(max_length=250, null=True, blank=True)
    researches = models.ManyToManyField(Research, blank=True)
    score_diagnostic = models.FloatField(default=None, null=True, blank=True)
    score_report = models.FloatField(default=None, null=True, blank=True)
    stain = models.ForeignKey(
        Stain, null=True, on_delete=models.SET_NULL, verbose_name="tinción", blank=True
    )

    def __str__(self):
        return f"{self.entryform.no_caso} - {self.exam.name}"

    @property
    def status(self):
        if self.forms.get().form_closed:
            status = "Finalizado"
        elif self.forms.get().cancelled:
            status = "Anulado"
        elif (
            self.exam.pathologists_assignment
            and self.pre_report_started
            and not self.pre_report_ended
        ):
            status = "Lectura Iniciada"
        elif (
            self.exam.pathologists_assignment
            and self.pre_report_started
            and self.pre_report_ended
        ):
            status = "Pre-Informe Terminado"
        else:
            status = "En Curso"
        return status

    class Meta:
        verbose_name = "Analisis"
        verbose_name_plural = "Analisis"


class Sample(models.Model):
    """
    A Sample also known as Individual, is the lowest level subject of study in a Case, (Tube, Fish, Cassette, ...),
    to this Unit is the lab process applied to and it's its Slide what Pathologist users study.
    """

    entryform = models.ForeignKey(EntryForm, null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(null=True, blank=True)  # correlative
    identification = models.ForeignKey(
        Identification, null=True, on_delete=models.CASCADE
    )
    unit_organs = models.ManyToManyField(OrganUnit)

    def __str__(self):
        return f"{self.entryform.no_caso}-{self.identification}({self.index})"


class SampleExams(models.Model):
    """
    Pivot model to bind Samples :model:`backend.Sample` to the services applied to them :model:`backend.Exam`
    and the :model:`backend.Organ` that will be studied using a specific :model:`backend.Stain`
    """

    sample = models.ForeignKey(Sample, null=True, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, null=True, on_delete=models.CASCADE)
    organ = models.ForeignKey(Organ, null=True, on_delete=models.CASCADE)
    stain = models.ForeignKey(
        Stain, null=True, on_delete=models.SET_NULL, verbose_name="tinción"
    )
    unit_organ = models.ForeignKey(
        OrganUnit, null=True, on_delete=models.CASCADE, blank=True
    )

    def __str__(self):
        return str(self.sample)


class Cassette(models.Model):
    """
    Stores information about the Cassette generated in the lab process.

    A Cassette is a small plastic instrument where the Units are organized to be processed and later on turned into Blocks
    """

    entryform = models.ForeignKey(EntryForm, null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(null=True, blank=True)
    cassette_name = models.CharField(max_length=250, null=True, blank=True)
    processor_loaded_at = models.DateTimeField(null=True, blank=True)
    samples = models.ManyToManyField(Sample)
    organs = models.ManyToManyField(Organ)


class Slice(models.Model):
    """
    Stores information about a Slice generated in the lab process.

    A Slice is a thin layer of paraffin with a cut of an Unit :model:`backend.Sample` (usually an Organ :model:`backend.Organ`)
    meant to be Stained using a :model:`backend.Stain` depending on the Service.
    """

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
    entryform = models.ForeignKey(EntryForm, null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(null=True, blank=True)


class Img(models.Model):
    """
    Generic model to upload imgs.

    Uploaded images are stored in MEDIA_URL/vehice_images
    """

    file = models.ImageField(upload_to="vehice_images")
    desc = models.TextField(blank=True, null=True)
    time_stamp = models.DateTimeField(auto_now_add=True)

    @property
    def is_new(self):
        return (
            datetime.timezone.now() - datetime.timedelta(minutes=1) <= self.time_stamp
        )


class Report(models.Model):
    """
    Stores information about a Pathologist User's Findings to be structured and export in printable format.
    """

    analysis = models.ForeignKey(AnalysisForm, null=True, on_delete=models.SET_NULL)
    slice = models.ForeignKey(Slice, null=True, on_delete=models.SET_NULL)
    organ = models.ForeignKey(Organ, null=True, on_delete=models.SET_NULL)
    organ_location = models.ForeignKey(
        OrganLocation, null=True, on_delete=models.SET_NULL
    )
    pathology = models.ForeignKey(Pathology, null=True, on_delete=models.SET_NULL)
    diagnostic = models.ForeignKey(Diagnostic, null=True, on_delete=models.SET_NULL)
    diagnostic_distribution = models.ForeignKey(
        DiagnosticDistribution, null=True, on_delete=models.SET_NULL
    )
    diagnostic_intensity = models.ForeignKey(
        DiagnosticIntensity, null=True, on_delete=models.SET_NULL
    )
    images = models.ManyToManyField(Img)
    identification = models.ForeignKey(
        Identification, null=True, on_delete=models.SET_NULL
    )
    sample = models.ForeignKey(Sample, null=True, on_delete=models.SET_NULL)


class ReportFinal(models.Model):
    """
    Stores summarised data of a single :model:`backend.Report` to be exported.
    """

    analysis = models.ForeignKey(AnalysisForm, null=True, on_delete=models.SET_NULL)
    no_reporte = models.CharField(max_length=250, null=True, blank=True)
    box_findings = models.TextField(null=True, blank=True)
    box_diagnostics = models.TextField(null=True, blank=True)
    box_comments = models.TextField(null=True, blank=True)
    box_tables = models.TextField(null=True, blank=True)


class Responsible(models.Model):
    """
    Stores detailed information about a the individual responsible
    in a :model:`backend.Customer` side to keep track of a :model:`backend.Entryform`
    """

    name = models.CharField(max_length=250, null=True, blank=True)
    email = models.CharField(max_length=250, null=True, blank=True)
    phone = models.CharField(max_length=250, null=True, blank=True)
    job = models.CharField(max_length=250, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "responsable"
        verbose_name_plural = "responsables"


class EmailCcTo(models.Model):
    """
    Stores information a email address to send a copy :model:`backend.EmailTemplate`.
    """

    email = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="correo Electrónico"
    )

    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name = "destinatario copiado en Plantilla Email"
        verbose_name_plural = "destinatarios copiados en Plantilla Email"


class EmailTemplate(models.Model):
    """Stores information about reusable email template."""

    name = models.CharField(
        max_length=250, null=True, blank=True, verbose_name="Nombre"
    )
    body = models.TextField(
        max_length=1000, null=True, blank=True, verbose_name="Mensaje"
    )
    cc = models.ManyToManyField(EmailCcTo, verbose_name="Copia para", blank=True)

    class Meta:
        verbose_name = "Plantilla Email"
        verbose_name_plural = "Plantillas Emails"


class EmailTemplateAttachment(models.Model):
    """Stores information about an attachment for a single :model:`backend.EmailTemplate`"""

    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    template_file = models.FileField(
        upload_to=entry_files_directory_path, verbose_name="archivo Adjunto"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "email Adjunto"
        verbose_name_plural = "email Adjuntos"


class CaseVersion(models.Model):
    """
    Stores information about a Case study is current version, as changes are generated over time revisions can be added.
    """

    entryform = models.ForeignKey(EntryForm, null=True, on_delete=models.SET_NULL)
    version = models.IntegerField(null=True, blank=True)
    generated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    generated_at = models.DateTimeField(auto_now_add=True)


RESUME_DOCUMENT_LANG = (
    (1, "es"),
    (2, "en"),
)


class DocumentCaseResume(models.Model):
    """
    Details information about a file upload to attach to a :model:`backend.EntryForm`
    """

    entryform = models.ForeignKey(EntryForm, null=True, on_delete=models.SET_NULL)
    filename = models.CharField(max_length=250, null=True, blank=True)
    file = models.FileField(upload_to="pdfs", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    lang = models.IntegerField(choices=RESUME_DOCUMENT_LANG, default=1)
    case_version = models.ForeignKey(CaseVersion, null=True, on_delete=models.SET_NULL)
    version = models.IntegerField(null=True, blank=True)
    generated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.filename


class DocumentResumeActionLog(models.Model):
    """
    Logs information about actions performed on a :model:`backend.DocumentCaseResume`
    """

    document = models.ForeignKey(
        DocumentCaseResume, null=True, on_delete=models.SET_NULL
    )
    mail_action = models.BooleanField(default=False)
    download_action = models.BooleanField(default=False)
    action_date = models.DateTimeField(auto_now_add=True)
    done_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)


class LogType(models.Model):
    type = models.CharField(max_length=250, null=True, blank=True)


class Log(models.Model):
    """
    Logs
    """

    log_date = models.DateTimeField()
    user = models.ForeignKey(
        User, null=True, on_delete=models.PROTECT, verbose_name="Usuario"
    )
    log_type = models.ForeignKey(
        LogType, null=True, on_delete=models.PROTECT, verbose_name="Tipo"
    )
    modelo = models.IntegerField(null=True, blank=True)
    id_modelo = models.IntegerField(null=True, blank=True)
