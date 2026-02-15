from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        SUPERVISOR = "SUPERVISOR", "Supervisor"
        GUARD = "GUARD", "Guard"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.GUARD
    )

    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_supervisor(self) -> bool:
        return self.role == self.Role.SUPERVISOR

    def is_guard(self) -> bool:
        return self.role == self.Role.GUARD
