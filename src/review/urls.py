from django.urls import path

from review import views


app_name = "review"
urlpatterns = [
    path("", views.index, name="index"),
    path("state/<int:index>", views.list, name="list"),
    path("stage/<int:pk>/", views.update_stage, name="stage"),
    path("files/<int:pk>/", views.FileView.as_view(), name="files"),
    path("download/<int:pk>", views.download_file, name="download_file"),
    path("mails/<int:pk>/", views.MailView.as_view(), name="mail_list"),
]
