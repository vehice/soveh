from django.conf.urls import include, re_path
from django.urls import path
from django.conf import settings
from django_js_reverse import views as js_reverse_views
from app import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    re_path(r"^$", views.home, name="home"),
    re_path(r"^users$", views.show_users, name="users"),
    re_path(r"^clientes$", views.show_clientes, name="clientes"),
    re_path(r"^analisis$", views.show_analisis, name="analisis"),
    re_path(r"^ingresos$", views.show_ingresos, name="ingresos"),
    re_path(r"^ingresos/tabla$", views.tabla_ingresos, name="tabla_ingresos"),
    re_path(r"^estudios$", views.show_estudios, name="estudios"),
    re_path(r"^ingresos/new$", views.new_ingreso, name="ingresos_new"),
    re_path(r"^research/new$", csrf_exempt(views.new_research), name="research_new"),
    re_path(r"^derivacion/(?P<all>\d+)$", views.show_patologos, name="patologos"),
    re_path(r"^control/tabla$", views.tabla_patologos, name="tabla_patologos"),
    re_path(
        r"^template-reception/(?P<id>\d+)/(?P<userId>\d+)$",
        views.template_reception,
        name="template_reception",
    ),
    re_path(
        r"^download-reception/(?P<id>\d+)$",
        views.download_reception,
        name="download_reception",
    ),
    re_path(
        r"^template-report/(?P<id>\d+)$", views.template_report, name="template_report"
    ),
    re_path(
        r"^download-report/(?P<id>\d+)$", views.download_report, name="download_report"
    ),
    re_path(
        r"^download-resumen-report/(?P<id>\d+)$",
        views.download_resumen_report,
        name="download_report",
    ),
    re_path(
        r"^template-resumen-report/(?P<id>\d+)/(?P<userId>\d+)$",
        views.template_resumen_report,
        name="template_resumen_report",
    ),
    re_path(
        r"^preview-report/(?P<id>\d+)$", views.preview_report, name="preview_report"
    ),
    re_path(r"^notification$", views.notification, name="notification"),
    re_path(r"^logactions/(?P<id>\d+)$", views.show_log_actions, name="logactions"),
    re_path(
        r"^change_language$", views.ChangeLanguage.as_view(), name="change_language"
    ),
]
