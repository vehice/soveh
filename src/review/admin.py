from django.contrib import admin

from review.models import Recipient, MailList

admin.site.register(Recipient)
admin.site.register(MailList)
