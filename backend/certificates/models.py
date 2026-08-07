import uuid
from django.db import models
from accounts.models import User
from events.models import Event


class Certificate(models.Model):
    certificate_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    pdf_file = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True,
    )
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['member', 'event']

    def __str__(self):
        return f"{self.member.username} — {self.event.title}"