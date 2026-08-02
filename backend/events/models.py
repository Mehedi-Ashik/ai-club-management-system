from django.db import models


class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    CATEGORY_CHOICES = [
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
    )
    event_date = models.DateField()
    venue = models.CharField(max_length=100, blank=True)
    capacity = models.IntegerField(default=100)
    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming',
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_full(self):
        return self.registrations.count() >= self.capacity


class EventRegistration(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='event_registrations',
    )
    reg_type = models.CharField(
        max_length=20,
        default='member',
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} → {self.event.title}"