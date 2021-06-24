from django.urls import path

from report import views


app_name = "report"
urlpatterns = [
    path("service", views.ServiceView.as_view(), name="service"),
    path("efficiency", views.EfficiencyView.as_view(), name="efficiency"),
    path("control", views.ControlView.as_view(), name="control"),
    path("analysis", views.AnalysisView.as_view(), name="analysis"),
]
