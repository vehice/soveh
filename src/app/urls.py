from django.conf.urls import include, url
from django.urls import path
from django.conf import settings
from django_js_reverse import views as js_reverse_views
from app import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^users$', views.show_users, name='users'),
    url(r'^clientes$', views.show_clientes, name='clientes'),
    url(r'^analisis$', views.show_analisis, name='analisis'),
    url(r'^ingresos$', views.show_ingresos, name='ingresos'),
    url(r'^estudios$', views.show_estudios, name='estudios'),
    url(r'^ingresos/new$', views.new_ingreso, name='ingresos_new'),
    url(r'^research/new$', csrf_exempt(views.new_research), name='research_new'),
    url(r'^derivacion/(?P<all>\d+)$', views.show_patologos, name='patologos'),
    url(r'^template-report/(?P<id>\d+)$', views.template_report, name='template_report'),
    url(r'^download-report/(?P<id>\d+)$', views.download_report, name='download_report'),
    url(r'^download-resumen-report/(?P<id>\d+)$', views.download_resumen_report, name='download_report'),
    url(r'^template-resumen-report/(?P<id>\d+)/(?P<userId>\d+)$', views.template_resumen_report, name='template_resumen_report'),
    url(r'^preview-report/(?P<id>\d+)$', views.preview_report, name='preview_report'),
    url(r'^notification$', views.notification, name='notification'),
    url(r'^logactions/(?P<id>\d+)$', views.show_log_actions, name='logactions'),
    url(r'^change_language$', views.ChangeLanguage.as_view(), name='change_language'),
]
