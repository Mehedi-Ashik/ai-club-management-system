from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ForumThread, ForumReply


def thread_list(request):
    threads = ForumThread.objects.all()
    return render(request, 'forum/thread_list.html', {'threads': threads})


def thread_detail(request, pk):
    thread = get_object_or_404(ForumThread, pk=pk)
    replies = thread.replies.filter(parent__isnull=True)
    return render(request, 'forum/thread_detail.html', {
        'thread': thread,
        'replies': replies,
    })


@login_required
def thread_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        thread = ForumThread.objects.create(
            title=title,
            content=content,
            author=request.user,
        )
        messages.success(request, 'Thread created!')
        return redirect('forum:detail', pk=thread.pk)

    return render(request, 'forum/thread_create.html')


@login_required
def add_reply(request, pk):
    thread = get_object_or_404(ForumThread, pk=pk)

    if thread.is_locked:
        messages.error(request, 'This thread is locked.')
        return redirect('forum:detail', pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        parent_reply = None
        if parent_id:
            parent_reply = ForumReply.objects.filter(pk=parent_id).first()

        if content:
            ForumReply.objects.create(
                thread=thread,
                author=request.user,
                content=content,
                parent=parent_reply,
            )
            messages.success(request, 'Reply posted!')

    return redirect('forum:detail', pk=pk)


@login_required
def upvote_reply(request, pk):
    reply = get_object_or_404(ForumReply, pk=pk)

    if request.user in reply.upvotes.all():
        reply.upvotes.remove(request.user)
    else:
        reply.upvotes.add(request.user)

    return redirect('forum:detail', pk=reply.thread.pk)


@login_required
def toggle_lock(request, pk):
    thread = get_object_or_404(ForumThread, pk=pk)

    if not request.user.is_president:
        messages.error(request, 'Permission denied!')
        return redirect('forum:detail', pk=pk)

    thread.is_locked = not thread.is_locked
    thread.save()
    return redirect('forum:detail', pk=pk)