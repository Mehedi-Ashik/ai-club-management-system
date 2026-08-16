import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from events.models import Event
from accounts.models import User
from attendance.models import Attendance
from certificates.models import Certificate
from blog.models import BlogPost
from forum.models import ForumThread


def home(request):
    upcoming_events = Event.objects.filter(
        is_public=True,
        event_date__gte=timezone.now().date(),
    ).order_by('event_date')[:3]

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


@login_required
def dashboard(request):
    if not request.user.is_president:
        messages.error(request, 'Permission denied!')
        return redirect('core:home')

    # Summary cards
    total_members = User.objects.filter(
        role__in=['member', 'president', 'admin']
    ).count()
    total_events = Event.objects.count()
    total_certificates = Certificate.objects.count()
    total_blog_posts = BlogPost.objects.count()
    total_forum_threads = ForumThread.objects.count()

    # Chart 1: Events by category
    category_data = Event.objects.values('category').annotate(count=Count('id'))
    category_labels = [c['category'].title() for c in category_data]
    category_counts = [c['count'] for c in category_data]

    # Chart 2: Attendance status (overall present vs absent)
    attendance_data = Attendance.objects.values('status').annotate(count=Count('id'))
    attendance_labels = [a['status'].title() for a in attendance_data]
    attendance_counts = [a['count'] for a in attendance_data]

    # Chart 3: Registrations per event (top 5)
    top_events = Event.objects.annotate(
        reg_count=Count('registrations')
    ).order_by('-reg_count')[:5]
    event_labels = [e.title for e in top_events]
    event_reg_counts = [e.reg_count for e in top_events]

    context = {
        'total_members': total_members,
        'total_events': total_events,
        'total_certificates': total_certificates,
        'total_blog_posts': total_blog_posts,
        'total_forum_threads': total_forum_threads,
        'category_labels': json.dumps(category_labels),
        'category_counts': json.dumps(category_counts),
        'attendance_labels': json.dumps(attendance_labels),
        'attendance_counts': json.dumps(attendance_counts),
        'event_labels': json.dumps(event_labels),
        'event_reg_counts': json.dumps(event_reg_counts),
    }
    return render(request, 'core/dashboard.html', context)