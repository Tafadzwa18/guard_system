from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/live/", views.live_dashboard, name="live_dashboard"),
    path("dashboard/history/", views.history, name="dashboard_history"),
]
