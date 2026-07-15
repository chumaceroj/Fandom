from django.urls import path

from . import views

# List of URL routes for Blog pages ("url_pattern", function, nickname_for_route)
urlpatterns = [
    path("", views.index, name="index"),
]