from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from accounts import views

urlpatterns = [
    url(r'^user/$', csrf_exempt(views.USER.as_view()), name='user'),
    url(r'^user/(?P<id>\d+)$',
        csrf_exempt(views.USER.as_view()),
        name='user_with_id'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^profile$', views.user_profile, name='profile'),
    url(r'^changepassword/$',
        csrf_exempt(views.change_password),
        name='change-password'),
    url(r'^changeinfo/$', csrf_exempt(views.change_info), name='change_info'),
    url(r'^permisos/$', csrf_exempt(views.PERMISOS.as_view()),
        name='permisos'),
    # url(r'^password_reset/$',
        # auth_views.password_reset, {
        #     'template_name': "registration/password_reset_form.html",
        #     'html_email_template_name':
        #     "registration/password_reset_email.html",
        #     'post_reset_redirect': 'password_reset_done'
        # },
        # name='password_reset'),
    # url(r'^password_reset/done/$',
    #     auth_views.password_reset_done,
    #     {'template_name': "registration/password_reset_done.html"},
    #     name='password_reset_done'),
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     auth_views.password_reset_confirm, {
    #         'template_name': "registration/password_reset_confirm.html",
    #         'post_reset_redirect': 'password_reset_complete'
    #     },
    #     name='password_reset_confirm'),
    # url(r'^reset/done/$',
    #     auth_views.password_reset_complete,
    #     {'template_name': "registration/password_reset_complete.html"},
    #     name='password_reset_complete'),
]
