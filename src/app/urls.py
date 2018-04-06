from django.conf.urls import include, url

from app import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^users$', views.show_users, name='users'),
    url(r'^empresas$', views.show_empresas, name='empresas'),
    url(r'^analisis$', views.show_analisis, name='analisis'),
    url(r'^ingresos$', views.show_ingresos, name='analisis'),
    url(r'^ingresos/new$', views.new_ingreso, name='analisis'),
]
