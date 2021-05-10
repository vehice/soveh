from django.urls import path

from report import views


app_name = "report"
urlpatterns = [path("pathologist", views.PathologistView.as_view(), name="pathologist")]
