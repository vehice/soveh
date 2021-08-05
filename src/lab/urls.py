from django.urls import path

from lab import views


app_name = "lab"
urlpatterns = [
    path("", views.home, name="home"),
    path("<int:pk>", views.home_detail, name="home_detail"),
    path("case/<int:pk>", views.CaseDetail.as_view(), name="case_detail"),
    path("case/<int:pk>/sheet", views.CaseReadSheet.as_view(), name="case_read_sheet"),
    path("case/<int:pk>/state", views.case_process_state, name="case_process_state"),
    path(
        "case/<int:pk>/<int:step>/edit",
        views.redirect_to_workflow_edit,
        name="redirect_to_workflow_edit",
    ),
    path(
        "difference/<int:pk>",
        views.update_unit_difference,
        name="update_unit_difference",
    ),
    path("organs", views.organ_list, name="organ_index"),
    path("stains", views.stain_list, name="stain_index"),
    path("units", views.unit_select_options, name="unit_select_options"),
    #
    # Cassettes Routes
    #
    path("cassettes", views.cassette_home, name="cassette_home"),
    path("cassettes/index", views.CassetteIndex.as_view(), name="cassette_index"),
    path("cassettes/diff", views.cassette_differences, name="cassette_difference"),
    path("cassettes/<int:pk>", views.CassetteDetail.as_view(), name="cassette_detail"),
    path("cassettes/prebuild", views.cassette_prebuild, name="cassette_prebuild"),
    path("cassettes/build", views.CassetteBuild.as_view(), name="cassette_build"),
    path("cassettes/process", views.CassetteProcess.as_view(), name="cassette_process"),
    #
    # Slide Routes
    #
    path("slides", views.SlideIndex.as_view(), name="slide_index"),
    path("slides/<int:pk>", views.SlideDetail.as_view(), name="slide_detail"),
    path("slides/prebuild", views.slide_prebuild, name="slide_prebuild"),
    path("slides/build", views.SlideBuild.as_view(), name="slide_build"),
    #
    # Process Routes
    #
    path("process", views.ProcessList.as_view(), name="process_index"),
]
