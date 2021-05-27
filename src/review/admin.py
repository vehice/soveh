from django.contrib import admin

from review.models import Recipient, MailList


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.items.get_queryset()


@admin.register(MailList)
class MailListAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.items.get_queryset()
