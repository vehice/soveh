from django.contrib import admin

from lab.models import Laboratory, Process


@admin.register(Laboratory)
class LaboratoryAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.items.get_queryset()


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.items.get_queryset()
