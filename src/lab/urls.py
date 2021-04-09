from django.urls import path

from lab import views


app_name = "lab"
urlpatterns = [
    path("case/<int:pk>", views.CaseDetail.as_view(), name="case_detail"),
    path("cassette/build", views.CassetteBuild.as_view(), name="cassette_build"),
    path("cassette/process", views.CassetteProcess.as_view(), name="cassette_process"),
    path("cassette/prebuild", views.cassette_prebuild, name="cassette_prebuild"),
]
