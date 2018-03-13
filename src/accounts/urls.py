from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from accounts import views


urlpatterns = [
    url(r'^user/$', csrf_exempt(views.USER.as_view()),name='user'),
    url(r'^user/(?P<id>\d+)$', csrf_exempt(views.USER.as_view()),name='user_with_id'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^profile$', views.user_profile, name='profile'),
    url(r'^changepassword/$',
            csrf_exempt(views.change_password),
            name='change-password'),
    url(r'^changeinfo/$',
            csrf_exempt(views.change_info),
            name='change_info'),
    url(r'^permisos/$', csrf_exempt(views.PERMISOS.as_view()), name='permisos'),

]
