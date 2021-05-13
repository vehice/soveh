from django.urls import path

from review import views


app_name = "review"
urlpatterns = [
    path("", views.index, name="index"),
    path("state/<int:index>", views.list, name="list"),
    path("stage/<int:pk>/", views.update_stage, name="stage"),
]
