from django.contrib import admin
from .models import IncidentReport

@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "session", "checkpoint", "created_at")
    list_filter = ("severity", "created_at")
    search_fields = ("title", "description", "session__guard__username")
