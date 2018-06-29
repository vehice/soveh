from django.conf.urls import include, url
from django.urls import path
from django.conf import settings
from django_js_reverse import views as js_reverse_views
from app import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^users$', views.show_users, name='users'),
    url(r'^clientes$', views.show_clientes, name='clientes'),
    url(r'^analisis$', views.show_analisis, name='analisis'),
    url(r'^ingresos$', views.show_ingresos, name='ingresos'),
    url(r'^ingresos/new$', views.new_ingreso, name='ingresos_new'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
