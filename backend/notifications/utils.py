from .models import Notification


def notify(user, message, link=''):
    """Creates a notification for a user. Call this from any view."""
    Notification.objects.create(
        user=user,
        message=message,
        link=link,
    )