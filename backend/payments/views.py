import uuid
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from events.models import Event, EventRegistration
from .models import Payment

SSLCOMMERZ_API_URL = 'https://sandbox.sslcommerz.com/gwprocess/v4/api.php'
SSLCOMMERZ_VALIDATION_URL = 'https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php'


@login_required
def initiate_payment(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    if event.fee <= 0:
        messages.info(request, 'This event is free, no payment needed.')
        return redirect('events:detail', pk=event.pk)

    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'You are already registered!')
        return redirect('events:detail', pk=event.pk)

    tran_id = f"GENESIS-{event.pk}-{request.user.pk}-{uuid.uuid4().hex[:8]}"

    payment = Payment.objects.create(
        event=event,
        user=request.user,
        amount=event.fee,
        tran_id=tran_id,
        status='pending',
    )

    post_data = {
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'total_amount': str(event.fee),
        'currency': 'BDT',
        'tran_id': tran_id,
        'success_url': request.build_absolute_uri(reverse('payments:success')),
        'fail_url': request.build_absolute_uri(reverse('payments:fail')),
        'cancel_url': request.build_absolute_uri(reverse('payments:cancel')),
        'cus_name': request.user.get_full_name() or request.user.username,
        'cus_email': request.user.email or 'test@example.com',
        'cus_add1': 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_postcode': '1000',
        'cus_country': 'Bangladesh',
        'cus_phone': '01700000000',
        'shipping_method': 'NO',
        'product_name': event.title,
        'product_category': 'Event Fee',
        'product_profile': 'general',
    }

    response = requests.post(SSLCOMMERZ_API_URL, data=post_data, timeout=15)
    result = response.json()

    if result.get('status') == 'SUCCESS':
        return redirect(result['GatewayPageURL'])
    else:
        payment.status = 'failed'
        payment.save()
        messages.error(request, 'Could not initiate payment. Please try again.')
        return redirect('events:detail', pk=event.pk)


@csrf_exempt
def payment_success(request):
    tran_id = request.POST.get('tran_id')
    val_id = request.POST.get('val_id')

    payment = Payment.objects.filter(tran_id=tran_id).first()
    if not payment:
        messages.error(request, 'Payment record not found.')
        return redirect('core:home')

    validation_params = {
        'val_id': val_id,
        'store_id': settings.SSLCOMMERZ_STORE_ID,
        'store_passwd': settings.SSLCOMMERZ_STORE_PASSWORD,
        'format': 'json',
    }
    validation_response = requests.get(
        SSLCOMMERZ_VALIDATION_URL, params=validation_params, timeout=15
    )
    validation_data = validation_response.json()

    if validation_data.get('status') in ('VALID', 'VALIDATED'):
        payment.status = 'success'
        payment.val_id = val_id
        payment.payment_method = request.POST.get('card_type', '')
        payment.save()

        EventRegistration.objects.get_or_create(
            event=payment.event,
            user=payment.user,
        )
        messages.success(
            request,
            f'Payment successful! You are registered for {payment.event.title}.'
        )
    else:
        payment.status = 'failed'
        payment.save()
        messages.error(request, 'Payment validation failed.')

    return redirect('events:detail', pk=payment.event.pk)


@csrf_exempt
def payment_fail(request):
    tran_id = request.POST.get('tran_id')
    payment = Payment.objects.filter(tran_id=tran_id).first()
    if payment:
        payment.status = 'failed'
        payment.save()
        messages.error(request, 'Payment failed. Please try again.')
        return redirect('events:detail', pk=payment.event.pk)
    messages.error(request, 'Payment failed.')
    return redirect('core:home')


@csrf_exempt
def payment_cancel(request):
    tran_id = request.POST.get('tran_id')
    payment = Payment.objects.filter(tran_id=tran_id).first()
    if payment:
        payment.status = 'cancelled'
        payment.save()
        messages.warning(request, 'Payment was cancelled.')
        return redirect('events:detail', pk=payment.event.pk)
    messages.warning(request, 'Payment was cancelled.')
    return redirect('core:home')