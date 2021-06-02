from django.urls import path

from lab import views


app_name = "lab"
urlpatterns = [
    path("", views.home, name="home"),
    path("<int:pk>", views.home_detail, name="home_detail"),
    path("case/<int:pk>", views.CaseDetail.as_view(), name="case_detail"),
    path("case/<int:pk>/sheet", views.CaseReadSheet.as_view(), name="case_read_sheet"),
    path("organs", views.organ_list, name="organ_index"),
    path("stains", views.stain_list, name="stain_index"),
    #
    # Cassettes Routes
    #
    path("cassettes", views.CassetteIndex.as_view(), name="cassette_index"),
    path("cassettes/<int:pk>", views.CassetteDetail.as_view(), name="cassette_detail"),
    path("cassettes/prebuild", views.cassette_prebuild, name="cassette_prebuild"),
    path("cassettes/build", views.CassetteBuild.as_view(), name="cassette_build"),
    #
    # Slide Routes
    #
    path("slides", views.SlideIndex.as_view(), name="slide_index"),
    path("slides/<int:pk>", views.SlideDetail.as_view(), name="slide_detail"),
    path("slides/build", views.SlideBuild.as_view(), name="slide_build"),
    #
    # Process Routes
    #
    path("process", views.ProcessIndex.as_view(), name="process_index"),
]
