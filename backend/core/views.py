from django.shortcuts import render
from django.utils import timezone
from events.models import Event
from accounts.models import User


def home(request):
    # Upcoming 3 events, soonest first
    upcoming_events = Event.objects.filter(
        is_public=True,
        event_date__gte=timezone.now().date(),
    ).order_by('event_date')[:3]

    # Quick statistics for the dashboard cards
    total_members = User.objects.filter(
        role__in=['member', 'president', 'admin']
    ).count()
    total_events = Event.objects.count()
    upcoming_events_count = Event.objects.filter(
        is_public=True,
        event_date__gte=timezone.now().date(),
    ).count()

    context = {
        'upcoming_events': upcoming_events,
        'total_members': total_members,
        'total_events': total_events,
        'upcoming_events_count': upcoming_events_count,
    }
    return render(request, 'core/index.html', context)