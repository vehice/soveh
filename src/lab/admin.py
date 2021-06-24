from django.contrib import admin

from lab.models import Process, Tree, ProcessTree

admin.site.register(Process)
admin.site.register(Tree)
admin.site.register(ProcessTree)
