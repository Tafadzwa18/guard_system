from django.contrib import admin
from .models import Site, Route, Checkpoint, Shift, PatrolSession, CheckIn

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name", "site", "is_active", "expected_duration_minutes")
    list_filter = ("site", "is_active")
    search_fields = ("name",)

@admin.register(Checkpoint)
class CheckpointAdmin(admin.ModelAdmin):
    list_display = ("name", "route", "code", "order_index")
    list_filter = ("route",)
    search_fields = ("name", "code")

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("guard", "route", "start_time", "end_time", "is_active")
    list_filter = ("route", "is_active")
    search_fields = ("guard__username",)

@admin.register(PatrolSession)
class PatrolSessionAdmin(admin.ModelAdmin):
    list_display = ("guard", "route", "status", "started_at", "ended_at")
    list_filter = ("status", "route")
    search_fields = ("guard__username",)

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ("session", "checkpoint", "checked_in_at", "method")
    list_filter = ("method", "checkpoint__route")
    search_fields = ("checkpoint__code", "session__guard__username")
