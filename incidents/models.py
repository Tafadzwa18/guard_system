from django.conf import settings
from django.db import models
from django.utils import timezone

from patrols.models import PatrolSession, Checkpoint

User = settings.AUTH_USER_MODEL

class IncidentReport(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    session = models.ForeignKey(PatrolSession, on_delete=models.CASCADE, related_name="incidents")
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents")

    title = models.CharField(max_length=120)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.LOW)

    photo = models.ImageField(upload_to="incident_photos/", blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents_created")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.severity})"
