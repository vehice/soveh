from django.contrib import admin
from .models import Specie, WaterSource, Fixative, Exam, Customer, LarvalStage, EntryForm, Organ, Slice, \
Diagnostic, DiagnosticDistribution, DiagnosticIntensity, Pathology, OrganLocation, Responsible

# admin.site.register(Customer)

class CustomExam(admin.ModelAdmin):
    list_display = ('name', 'stain')

admin.site.register(Exam, CustomExam)

class CustomCustomer(admin.ModelAdmin):
    list_display = ('name', 'company', 'type_customer')

admin.site.register(Customer, CustomCustomer)

admin.site.register(Diagnostic)

admin.site.register(OrganLocation)

admin.site.register(Fixative)

admin.site.register(Organ)

admin.site.register(Responsible)

class OrgansInline(admin.TabularInline):
    model = Pathology.organs.through
    verbose_name_plural = "Órganos Relacionados"
    verbose_name = "Órgano"

@admin.register(Pathology)
class CustomPathology(admin.ModelAdmin):
    inlines = (OrgansInline,)
    exclude = ('organs',)
