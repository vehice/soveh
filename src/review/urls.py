from django.urls import path

from review import views


app_name = "review"
urlpatterns = [
    path("", views.index, name="index"),
    path("state/<int:index>", views.list, name="list"),
    path("stage/<int:pk>/", views.update_stage, name="stage"),
    path("files/<int:pk>/", views.FileView.as_view(), name="files"),
    path("mails/<int:pk>/", views.MailView.as_view(), name="mail_list"),
    path(
        "analysis/<int:pk>/mails", views.analysis_mailing_list, name="analysis_emails"
    ),
    path("analysis/<int:pk>/send", views.send_email, name="send_email"),
]
