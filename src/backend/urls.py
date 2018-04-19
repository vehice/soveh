from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from backend import views

urlpatterns = [
    url(r'^customer$', csrf_exempt(views.CUSTOMER.as_view()), name='customer'),
    url(r'^exam$', csrf_exempt(views.EXAM.as_view()), name='exam'),
    url(r'^entryform$',
        csrf_exempt(views.ENTRYFORM.as_view()),
        name='entryform'),
]
