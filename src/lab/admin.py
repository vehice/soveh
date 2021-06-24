from django.contrib import admin

from lab.models import ExamTree, Process, ProcessTree, Tree

admin.site.register(Process)
admin.site.register(Tree)
admin.site.register(ProcessTree)
admin.site.register(ExamTree)
