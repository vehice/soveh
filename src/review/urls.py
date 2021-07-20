from django.urls import path

from review import views


app_name = "review"
urlpatterns = [
    path("", views.index, name="index"),
    path("state/<int:index>", views.list, name="list"),
    path("stage/<int:pk>/", views.update_stage, name="stage"),
    path("files/<int:pk>/", views.FileView.as_view(), name="files"),
    path("recipients/", views.new_recipient, name="create_recipient"),
    path(
        "recipients/<int:pk>/", views.AnalysisRecipientView.as_view(), name="recipients"
    ),
    path("lists/", views.new_mail_list, name="new_mail_list"),
    path("lists/<int:pk>/", views.mail_list_recipients, name="list_recipients"),
    path(
        "analysis/<int:pk>/mails", views.analysis_mailing_list, name="analysis_emails"
    ),
    path("analysis/<int:pk>/send", views.send_email, name="send_email"),
]
