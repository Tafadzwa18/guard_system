from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Site(models.Model):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Route(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="routes")
    name = models.CharField(max_length=120)
    expected_duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.site.name} • {self.name}"


class Checkpoint(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="checkpoints")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=32, unique=True)  # for manual entry now (QR later)
    order_index = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order_index", "id"]

    def __str__(self):
        return f"{self.route.name} • {self.name}"


class Shift(models.Model):
    guard = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shifts")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="shifts")
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.guard} • {self.route} • {self.start_time}-{self.end_time}"


class PatrolSession(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        FLAGGED = "FLAGGED", "Flagged"

    guard = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patrol_sessions")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="patrol_sessions")
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    def end(self):
        self.ended_at = timezone.now()
        self.status = self.Status.COMPLETED
        self.save(update_fields=["ended_at", "status"])

    def __str__(self):
        return f"{self.guard} • {self.route} • {self.status}"


class CheckIn(models.Model):
    class Method(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        QR = "QR", "QR"

    session = models.ForeignKey(PatrolSession, on_delete=models.CASCADE, related_name="checkins")
    checkpoint = models.ForeignKey(Checkpoint, on_delete=models.CASCADE, related_name="checkins")
    checked_in_at = models.DateTimeField(default=timezone.now)
    method = models.CharField(max_length=10, choices=Method.choices, default=Method.MANUAL)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "checkpoint"], name="unique_checkpoint_per_session")
        ]
        ordering = ["checked_in_at", "id"]

    def __str__(self):
        return f"{self.session} • {self.checkpoint}"
