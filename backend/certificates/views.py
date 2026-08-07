import io
import qrcode

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.urls import reverse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader

from .models import Certificate
from events.models import Event
from attendance.models import Attendance


def _build_certificate_pdf(certificate, request):
    """Generates a PDF for the given Certificate and saves it to pdf_file."""
    verify_url = request.build_absolute_uri(
        reverse('certificates:verify', args=[certificate.certificate_id])
    )

    # 1. Make the QR code image in memory
    qr_img = qrcode.make(verify_url)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # 2. Draw the certificate page
    pdf_buffer = io.BytesIO()
    page_size = landscape(A4)
    c = canvas.Canvas(pdf_buffer, pagesize=page_size)
    width, height = page_size

    c.setFont('Helvetica-Bold', 30)
    c.drawCentredString(width / 2, height - 120, 'Certificate of Participation')

    c.setFont('Helvetica', 16)
    c.drawCentredString(width / 2, height - 180, 'This is to certify that')

    c.setFont('Helvetica-Bold', 24)
    member_name = certificate.member.get_full_name() or certificate.member.username
    c.drawCentredString(width / 2, height - 220, member_name)

    c.setFont('Helvetica', 16)
    c.drawCentredString(
        width / 2, height - 260,
        f"has successfully participated in \"{certificate.event.title}\""
    )
    c.drawCentredString(
        width / 2, height - 290,
        f"held on {certificate.event.event_date.strftime('%d %B, %Y')}"
    )

    # 3. Paste the QR code (bottom-right) for verification
    qr_reader = ImageReader(qr_buffer)
    c.drawImage(qr_reader, width - 160, 60, width=100, height=100)
    c.setFont('Helvetica', 8)
    c.drawCentredString(width - 110, 50, 'Scan to verify')

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    filename = f"certificate_{certificate.certificate_id}.pdf"
    certificate.pdf_file.save(filename, ContentFile(pdf_buffer.read()), save=True)


@login_required
def generate_certificates(request, event_id):
    """President-only: create + generate a certificate for every member
    marked 'present' in the attendance of this event."""
    if not request.user.is_president:
        messages.error(request, 'Permission denied!')
        return redirect('core:home')

    event = get_object_or_404(Event, pk=event_id)
    present_records = Attendance.objects.filter(event=event, status='present')

    created_count = 0
    for record in present_records:
        certificate, created = Certificate.objects.get_or_create(
            member=record.member,
            event=event,
        )
        if created or not certificate.pdf_file:
            _build_certificate_pdf(certificate, request)
            created_count += 1

    messages.success(
        request,
        f'{created_count} certificate(s) generated for "{event.title}".'
    )
    return redirect('attendance:report', event_id=event_id)


@login_required
def my_certificates(request):
    certificates = Certificate.objects.filter(
        member=request.user
    ).select_related('event').order_by('-issued_at')
    return render(request, 'certificates/my_certificates.html', {
        'certificates': certificates,
    })


@login_required
def download_certificate(request, cert_id):
    certificate = get_object_or_404(Certificate, pk=cert_id)

    # Only the owner or a president/admin can download it
    if certificate.member != request.user and not request.user.is_president:
        messages.error(request, 'Permission denied!')
        return redirect('core:home')

    if not certificate.pdf_file:
        raise Http404('Certificate file not found.')

    return FileResponse(
        certificate.pdf_file.open('rb'),
        as_attachment=True,
        filename=f"certificate_{certificate.event.title}.pdf",
    )


def verify_certificate(request, certificate_id):
    """Public page — no login needed. Anyone with the QR/link can check
    whether a certificate is genuine."""
    certificate = Certificate.objects.filter(
        certificate_id=certificate_id
    ).select_related('member', 'event').first()

    return render(request, 'certificates/verify.html', {
        'certificate': certificate,
    })