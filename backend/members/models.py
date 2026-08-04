from django.db import models
from accounts.models import User


class MembershipApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='membership_application',
    )
    full_name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    batch = models.CharField(max_length=20)
    roll_no = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, blank=True)
    reason = models.TextField(
        blank=True,
        help_text="Why do you want to join?"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} — {self.status}"

    def approve(self):
        from django.utils import timezone
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        self.save()
        self.user.role = 'member'
        self.user.save()

    def reject(self):
        from django.utils import timezone
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        self.save()