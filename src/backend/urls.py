from django.conf.urls import url
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from backend import views

urlpatterns = [
    path('customer', csrf_exempt(views.CUSTOMER.as_view()), name='customer'),
    path('exam', csrf_exempt(views.EXAM.as_view()), name='exam'),
    path(
        'entryform', csrf_exempt(views.ENTRYFORM.as_view()), name='entryform'),
    path(
        'entryform/<int:id>',
        csrf_exempt(views.ENTRYFORM.as_view()),
        name='entryform_id'),
    path('workflow', csrf_exempt(views.WORKFLOW.as_view()), name='workflow'),
]
