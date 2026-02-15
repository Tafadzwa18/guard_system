from django.urls import path
from . import views

urlpatterns = [
    path("guard/", views.guard_home, name="guard_home"),
    path("guard/start/<int:route_id>/", views.start_patrol, name="start_patrol"),
    path("guard/patrol/<int:session_id>/", views.patrol_checkin, name="patrol_checkin"),
    path("guard/patrol/<int:session_id>/end/", views.end_patrol, name="end_patrol"),
    path("guard/patrol/<int:session_id>/summary/", views.patrol_summary, name="patrol_summary"),
]
