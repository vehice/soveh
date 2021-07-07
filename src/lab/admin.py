from django.contrib import admin
from lab.models import CaseProcessTree, Process, Tree, TreeProcess

admin.site.register(Process)
admin.site.register(CaseProcessTree)
admin.site.register(Tree)
admin.site.register(TreeProcess)
