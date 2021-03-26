from django.urls import path

from . import views


app_name = "lab"
urlpatterns = [
    path("cassette/build", views.CassetteBuildView.as_view(), name="cassette_build"),
    path(
        "cassette/process", views.CassetteProcessView.as_view(), name="cassette_process"
    ),
]
