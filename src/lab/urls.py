from django.urls import path

from lab import views


app_name = "lab"
urlpatterns = [
    path("case/<int:pk>", views.CaseDetail.as_view(), name="case_detail"),
    path("organs", views.organ_list, name="organ_index"),
    path("cassettes", views.CassetteIndex.as_view(), name="cassette_index"),
    path("cassette/<int:pk>", views.CassetteDetail.as_view(), name="cassette_detail"),
    path("cassette/prebuild", views.cassette_prebuild, name="cassette_prebuild"),
    path("cassette/build", views.CassetteBuild.as_view(), name="cassette_build"),
]
