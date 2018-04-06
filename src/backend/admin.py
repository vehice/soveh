from django.contrib import admin
from .models import Specie, WaterSource, Fixative, Exam, Customer, LarvalStage, \
QuestionReceptionCondition, EntryForm, AnswerReceptionCondition, Organ

admin.site.register(Specie)
admin.site.register(Organ)
admin.site.register(WaterSource)
admin.site.register(Fixative)
admin.site.register(Exam)
admin.site.register(Customer)
admin.site.register(LarvalStage)
admin.site.register(QuestionReceptionCondition)
admin.site.register(AnswerReceptionCondition)
admin.site.register(EntryForm)
