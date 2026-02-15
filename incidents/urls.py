from django.urls import path
from . import views

urlpatterns = [
    path("guard/patrol/<int:session_id>/incident/new/", views.create_incident, name="create_incident"),

    path("dashboard/incidents/", views.incident_list, name="incident_list"),
    path("dashboard/incidents/<int:incident_id>/", views.incident_detail, name="incident_detail"),
]
