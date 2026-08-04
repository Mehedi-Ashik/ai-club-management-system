from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MembershipApplication
from accounts.models import User


def member_list(request):
    members = User.objects.filter(role='member')
    return render(request, 'members/member_list.html', {
        'members': members
    })


@login_required
def apply_membership(request):
    # Already a member or president or admin
    if request.user.role in ['member', 'president', 'admin']:
        messages.info(request, 'You are already a member!')
        return redirect('core:home')

    # Already applied
    if MembershipApplication.objects.filter(
        user=request.user
    ).exists():
        messages.warning(
            request,
            'You have already submitted an application!'
        )
        return redirect('core:home')

    if request.method == 'POST':
        MembershipApplication.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            department=request.POST.get('department'),
            batch=request.POST.get('batch'),
            roll_no=request.POST.get('roll_no'),
            phone=request.POST.get('phone', ''),
            reason=request.POST.get('reason', ''),
        )
        messages.success(
            request,
            'Application submitted! Please wait for approval.'
        )
        return redirect('core:home')

    return render(request, 'members/apply.html')


@login_required
def application_list(request):
    if not request.user.is_president:
        messages.error(request, 'Permission denied!')
        return redirect('core:home')

    applications = MembershipApplication.objects.filter(
        status='pending'
    ).order_by('-applied_at')

    return render(request, 'members/application_list.html', {
        'applications': applications
    })


@login_required
def approve_application(request, pk):
    if not request.user.is_president:
        messages.error(request, 'Permission denied!')
        return redirect('core:home')

    application = get_object_or_404(MembershipApplication, pk=pk)
    application.approve()
    messages.success(
        request,
        f'{application.full_name} has been approved as a member!'
    )
    return redirect('members:applications')


@login_required
def reject_application(request, pk):
    if not request.user.is_president:
        messages.error(request, 'Permission denied!')
        return redirect('core:home')

    application = get_object_or_404(MembershipApplication, pk=pk)
    application.reject()
    messages.warning(
        request,
        f'{application.full_name} application has been rejected.'
    )
    return redirect('members:applications')