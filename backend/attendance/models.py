from django.db import models
from accounts.models import User
from events.models import Event


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendances',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='attendances',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
    )
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['member', 'event']

    def __str__(self):
        return f"{self.member.username} — {self.event.title} — {self.status}"