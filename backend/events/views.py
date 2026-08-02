from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, EventRegistration


def event_list(request):
    events = Event.objects.filter(
        is_public=True
    ).order_by('-created_at')
    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = EventRegistration.objects.filter(
            event=event,
            user=request.user
        ).exists()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_registered': is_registered,
    })


@login_required
def event_register(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.is_full:
        messages.error(request, 'Sorry, this event is full!')
        return redirect('events:detail', pk=pk)

    if EventRegistration.objects.filter(
        event=event, user=request.user
    ).exists():
        messages.warning(request, 'You are already registered!')
        return redirect('events:detail', pk=pk)

    EventRegistration.objects.create(
        event=event,
        user=request.user,
    )
    messages.success(
        request,
        f'Successfully registered for {event.title}!'
    )
    return redirect('events:detail', pk=pk)


@login_required
def event_create(request):
    if not request.user.is_president:
        messages.error(request, 'You do not have permission!')
        return redirect('events:list')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        event_date = request.POST.get('event_date')
        venue = request.POST.get('venue')
        capacity = request.POST.get('capacity', 100)
        fee = request.POST.get('fee', 0)
        is_public = request.POST.get('is_public') == 'on'

        Event.objects.create(
            title=title,
            description=description,
            category=category,
            event_date=event_date,
            venue=venue,
            capacity=capacity,
            fee=fee,
            is_public=is_public,
        )
        messages.success(request, 'Event created successfully!')
        return redirect('events:list')

    return render(request, 'events/event_create.html')