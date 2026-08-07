from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Attendance
from events.models import Event
from accounts.models import User


@login_required
def mark_attendance(request, event_id):
    if not request.user.is_president:
        messages.error(request, 'Permission denied!')
        return redirect('core:home')

    event = get_object_or_404(Event, pk=event_id)
    members = User.objects.filter(role='member')

    if request.method == 'POST':
        present_ids = request.POST.getlist('present')
        for member in members:
            status = 'present' if str(member.id) in present_ids else 'absent'
            Attendance.objects.update_or_create(
                member=member,
                event=event,
                defaults={'status': status},
            )
        messages.success(request, 'Attendance marked successfully!')
        return redirect('attendance:report', event_id=event_id)

    existing = Attendance.objects.filter(event=event)
    marked = {a.member_id: a.status for a in existing}

    return render(request, 'attendance/mark.html', {
        'event': event,
        'members': members,
        'marked': marked,
    })


@login_required
def attendance_report(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    attendances = Attendance.objects.filter(
        event=event
    ).select_related('member')

    present = attendances.filter(status='present').count()
    absent = attendances.filter(status='absent').count()

    return render(request, 'attendance/report.html', {
        'event': event,
        'attendances': attendances,
        'present': present,
        'absent': absent,
    })