from django.contrib import admin
from .models import Specie, WaterSource, Fixative, Exam, Customer, LarvalStage, \
QuestionReceptionCondition, EntryForm, AnswerReceptionCondition, Organ, Slice, \
Diagnostic, DiagnosticDistribution, DiagnosticIntensity, Pathology, OrganLocation

admin.site.register(Specie)
admin.site.register(WaterSource)
admin.site.register(Fixative)
admin.site.register(Exam)
admin.site.register(Customer)
admin.site.register(LarvalStage)
admin.site.register(QuestionReceptionCondition)
admin.site.register(AnswerReceptionCondition)
admin.site.register(EntryForm)
admin.site.register(Slice)
admin.site.register(Organ)
admin.site.register(OrganLocation)
admin.site.register(Diagnostic)
admin.site.register(DiagnosticDistribution)
admin.site.register(DiagnosticIntensity)
admin.site.register(Pathology)
