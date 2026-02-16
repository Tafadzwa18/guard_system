from django.urls import path
from . import views

urlpatterns = [
    path("guard/", views.guard_home, name="guard_home"),
    path("guard/start/<int:route_id>/", views.start_patrol, name="start_patrol"),
    path("guard/patrol/<int:session_id>/", views.patrol_checkin, name="patrol_checkin"),
    path("guard/patrol/<int:session_id>/end/", views.end_patrol, name="end_patrol"),
    path("guard/patrol/<int:session_id>/summary/", views.patrol_summary, name="patrol_summary"),
    path("guard/patrol/<int:session_id>/scan/<str:code>/", views.qr_scan_checkin, name="qr_scan_checkin"), # QR scan endpoint
    path("guard/patrol/<int:session_id>/qr-pack/", views.session_qr_pack, name="session_qr_pack"),
    path("guard/patrol/<int:session_id>/scan-camera/", views.scan_camera, name="scan_camera"),


]
