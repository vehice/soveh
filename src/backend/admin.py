from django.contrib import admin
from backend.models import *
from django.forms import Textarea, TextInput

admin.site.register(Diagnostic)
admin.site.register(OrganLocation)
admin.site.register(Fixative)
admin.site.register(Organ)
admin.site.register(Responsible)
admin.site.register(EmailCcTo)
admin.site.register(Research)
admin.site.register(Specie)


class OrgansInline(admin.TabularInline):
    model = Pathology.organs.through
    verbose_name_plural = "Órganos Relacionados"
    verbose_name = "Órgano"


class CustomEmailAttachment(admin.TabularInline):
    model = EmailTemplateAttachment


@admin.register(AnalysisForm)
class CustomAnalysisForm(admin.ModelAdmin):
    list_display = ("id", "entryform", "exam", "stain", "patologo", "status")
    ordering = ["-entryform__no_caso"]
    search_fields = ("entryform__no_caso", "exam__name")


@admin.register(EntryForm)
class CustomEntryForm(admin.ModelAdmin):
    list_display = ("id", "no_caso", "customer", "created_at", "sampled_at")
    ordering = ["-no_caso"]
    search_fields = ("no_caso",)


@admin.register(SampleExams)
class CustomSampleExam(admin.ModelAdmin):
    list_display = ("id", "sample", "exam", "organ", "stain", "unit_organ")
    search_fields = ("sample__entryform__no_caso", "exam__name")


@admin.register(Exam)
class CustomExam(admin.ModelAdmin):
    list_display = ("name", "service", "stain")

    def get_form(self, request, obj=None, **kwargs):
        form = super(CustomExam, self).get_form(request, obj, **kwargs)
        field = form.base_fields["stain"]
        field.widget.can_delete_related = False
        return form


@admin.register(EmailTemplate)
class CustomEmail(admin.ModelAdmin):
    list_display = ("name", "body")
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 3, "cols": 50})},
        models.CharField: {"widget": TextInput()},
    }
    inlines = [
        CustomEmailAttachment,
    ]


@admin.register(Customer)
class CustomCustomer(admin.ModelAdmin):
    list_display = ("name", "company", "type_customer")


@admin.register(Pathology)
class CustomPathology(admin.ModelAdmin):
    inlines = (OrgansInline,)
    exclude = ("organs",)


@admin.register(Stain)
class CustomStain(admin.ModelAdmin):
    list_display = ("name", "abbreviation", "description")
