from django.contrib import admin
from backend.models import *
from django.forms import Textarea, TextInput 

class CustomExam(admin.ModelAdmin):
    list_display = ('name', 'service', 'stain')
    # readonly_fields  = ('get_service_desc',)

    def get_service_desc(self, obj):
        return obj.service.description

    # get_service_desc.short_description = 'Descripción del Servicio'

admin.site.register(Exam, CustomExam)

class CustomCustomer(admin.ModelAdmin):
    list_display = ('name', 'company', 'type_customer')

admin.site.register(Customer, CustomCustomer)

admin.site.register(Diagnostic)

admin.site.register(OrganLocation)

admin.site.register(Fixative)

admin.site.register(Organ)

admin.site.register(Responsible)

admin.site.register(EmailCcTo)

admin.site.register(Research)

class CustomStain(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'description')

admin.site.register(Stain, CustomStain)

class CustomEmailAttachment(admin.TabularInline):
    model = EmailTemplateAttachment

class CustomEmail(admin.ModelAdmin):
    list_display = ('name', 'body')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':3, 'cols':50})},
        models.CharField: {'widget': TextInput()},
    }
    inlines = [CustomEmailAttachment,]

admin.site.register(EmailTemplate, CustomEmail)

class OrgansInline(admin.TabularInline):
    model = Pathology.organs.through
    verbose_name_plural = "Órganos Relacionados"
    verbose_name = "Órgano"

@admin.register(Pathology)
class CustomPathology(admin.ModelAdmin):
    inlines = (OrgansInline,)
    exclude = ('organs',)
