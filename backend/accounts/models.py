from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Super Admin'),
        ('president', 'Club President'),
        ('member', 'Member'),
        ('guest', 'Guest'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='guest',
    )
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_president(self):
        return self.role in ['admin', 'president']

    @property
    def is_member(self):
        return self.role in ['admin', 'president', 'member']


class Member(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='member_profile',
    )
    full_name = models.CharField(max_length=100)
    department = models.CharField(max_length=50, blank=True)
    batch = models.CharField(max_length=20, blank=True)
    roll_no = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} — {self.department}"