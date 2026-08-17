import io
import os
import math
import random
import qrcode

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.urls import reverse

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader

from .models import Certificate
from events.models import Event
from attendance.models import Attendance


def _draw_gradient_rect(c, x, y, width, height, color_start, color_end, steps=120, vertical=True):
    """Draws a smooth gradient-filled rectangle."""
    for i in range(steps):
        frac = i / steps
        r = color_start.red + (color_end.red - color_start.red) * frac
        g = color_start.green + (color_end.green - color_start.green) * frac
        b = color_start.blue + (color_end.blue - color_start.blue) * frac
        c.setFillColorRGB(r, g, b)
        if vertical:
            seg_h = height / steps
            c.rect(x, y + i * seg_h, width, seg_h + 1, fill=1, stroke=0)
        else:
            seg_w = width / steps
            c.rect(x + i * seg_w, y, seg_w + 1, height, fill=1, stroke=0)


def _draw_seal(c, cx, cy, navy, gold):
    """Draws a decorative circular seal/medallion to fill empty space."""
    outer_r = 46
    inner_r = 38

    c.setStrokeColor(gold)
    c.setLineWidth(2.5)
    c.circle(cx, cy, outer_r, stroke=1, fill=0)

    c.setStrokeColor(navy)
    c.setLineWidth(1)
    c.circle(cx, cy, inner_r, stroke=1, fill=0)

    c.setStrokeColor(gold)
    c.setLineWidth(0.75)
    c.circle(cx, cy, inner_r - 6, stroke=1, fill=0)

    # 5-point star at center
    star_r_outer = 13
    star_r_inner = 5.5
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = star_r_outer if i % 2 == 0 else star_r_inner
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    p = c.beginPath()
    p.moveTo(*points[0])
    for pt in points[1:]:
        p.lineTo(*pt)
    p.close()
    c.setFillColor(gold)
    c.drawPath(p, fill=1, stroke=0)

    c.setFont('Helvetica-Bold', 6.5)
    c.setFillColor(navy)
    c.drawCentredString(cx, cy - inner_r + 9, 'GENESIS')
    c.setFont('Helvetica', 5)
    c.setFillColor(navy)
    c.drawCentredString(cx, cy + inner_r - 13, 'CERTIFIED')


def _draw_signature(c, x, y, w, h, seed_text, color):
    """Draws a realistic hand-drawn-looking signature scribble using bezier-like curves."""
    rnd = random.Random(seed_text)
    n_points = 16
    xs = [x + i * (w / (n_points - 1)) for i in range(n_points)]
    base = y + h * 0.45
    terms = [
        (rnd.uniform(0.6, 1.6), rnd.uniform(0, 6.28), rnd.uniform(0.25, 1.0) * h * 0.35)
        for _ in range(3)
    ]
    ys = []
    for i in range(n_points):
        t = i / (n_points - 1)
        val = base
        for freq, phase, amp in terms:
            val += amp * math.sin(freq * t * 6.283 + phase)
        val += rnd.uniform(-h * 0.04, h * 0.04)
        ys.append(val)

    c.setStrokeColor(color)
    c.setLineWidth(1.4)
    c.setLineCap(1)
    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(xs[0], ys[0])
    for i in range(1, n_points):
        p.lineTo(xs[i], ys[i])
    c.drawPath(p, stroke=1, fill=0)

    # flourish swash underline for a signature-like finish
    c.setLineWidth(0.9)
    p2 = c.beginPath()
    fx0, fx1 = x + w * 0.08, x + w * 0.85
    fy = y + h * 0.08
    p2.moveTo(fx0, fy)
    p2.curveTo(
        fx0 + (fx1 - fx0) * 0.25, fy - h * 0.18,
        fx0 + (fx1 - fx0) * 0.75, fy + h * 0.18,
        fx1, fy,
    )
    c.drawPath(p2, stroke=1, fill=0)


def _build_certificate_pdf(certificate, request):
    """Generates a professional GENESIS / GUB certificate PDF."""
    verify_url = request.build_absolute_uri(
        reverse('certificates:verify', args=[certificate.certificate_id])
    )

    qr_img = qrcode.make(verify_url)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    pdf_buffer = io.BytesIO()
    page_size = landscape(A4)
    c = canvas.Canvas(pdf_buffer, pagesize=page_size)
    width, height = page_size

    navy = colors.HexColor('#0D47A1')
    light_navy = colors.HexColor('#1565C0')
    gold = colors.HexColor('#C9A227')
    gray = colors.HexColor('#6b7280')
    dark_text = colors.HexColor('#1f2430')
    green = colors.HexColor('#0B6E3A')

    # 1. Soft gradient background
    _draw_gradient_rect(
        c, 0, 0, width, height,
        colors.HexColor('#FFFFFF'), colors.HexColor('#EAF2FB'),
        steps=150, vertical=True,
    )

    # 2. Outer navy border
    margin = 24
    c.setStrokeColor(navy)
    c.setLineWidth(3)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    # 3. Inner gold border
    inner_margin = margin + 10
    c.setStrokeColor(gold)
    c.setLineWidth(1.2)
    c.rect(inner_margin, inner_margin, width - 2 * inner_margin, height - 2 * inner_margin)

    # 4. Gradient ribbon at top (navy -> green)
    strip_h = 8
    _draw_gradient_rect(
        c, margin, height - margin - strip_h, width - 2 * margin, strip_h,
        navy, green, steps=80, vertical=False,
    )

    # 5. Gold corner accents
    corner_size = 12
    for cx in [margin, width - margin - corner_size]:
        for cy in [margin, height - margin - corner_size]:
            c.setFillColor(gold)
            c.rect(cx, cy, corner_size, corner_size, fill=1, stroke=0)

    # 6. Logos: GUB (left), GENESIS (right)
    assets_dir = os.path.join(settings.BASE_DIR, 'certificates', 'assets')
    gub_logo_path = os.path.join(assets_dir, 'gub_logo.png')
    genesis_logo_path = os.path.join(assets_dir, 'genesis_logo.png')

    logo_h = 55
    if os.path.exists(gub_logo_path):
        gub_reader = ImageReader(gub_logo_path)
        iw, ih = gub_reader.getSize()
        logo_w = logo_h * iw / ih
        c.drawImage(gub_reader, margin + 30, height - margin - 20 - logo_h,
                    width=logo_w, height=logo_h, mask='auto')

    if os.path.exists(genesis_logo_path):
        genesis_reader = ImageReader(genesis_logo_path)
        iw, ih = genesis_reader.getSize()
        logo_w2 = logo_h * iw / ih
        c.drawImage(genesis_reader, width - margin - 30 - logo_w2, height - margin - 20 - logo_h,
                    width=logo_w2, height=logo_h, mask='auto')

    # 7. Header text
    c.setFillColor(green)
    c.setFont('Helvetica-Bold', 15)
    c.drawCentredString(width / 2, height - 78, 'GREEN UNIVERSITY OF BANGLADESH')

    c.setFillColor(navy)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(
        width / 2, height - 96,
        'GENESIS — Green Neural and Synaptic Intelligence Society'
    )

    # 8. Title
    c.setFillColor(navy)
    c.setFont('Helvetica-Bold', 32)
    c.drawCentredString(width / 2, height - 140, 'Certificate of Participation')

    c.setStrokeColor(gold)
    c.setLineWidth(2)
    line_w = 220
    c.line(width / 2 - line_w / 2, height - 154, width / 2 + line_w / 2, height - 154)

    # 9. Subtext
    c.setFillColor(gray)
    c.setFont('Helvetica-Oblique', 13)
    c.drawCentredString(width / 2, height - 188, 'This certificate is proudly presented to')

    # 10. Member name
    member_name = certificate.member.get_full_name() or certificate.member.username
    c.setFillColor(navy)
    c.setFont('Helvetica-Bold', 28)
    c.drawCentredString(width / 2, height - 230, member_name)

    c.setStrokeColor(light_navy)
    c.setLineWidth(1)
    name_line_w = 300
    c.line(width / 2 - name_line_w / 2, height - 242, width / 2 + name_line_w / 2, height - 242)

    # 11. Body — event details (dynamic)
    c.setFillColor(dark_text)
    c.setFont('Helvetica', 13)
    c.drawCentredString(
        width / 2, height - 270,
        f'for successfully participating in "{certificate.event.title}"'
    )
    venue_text = f" at {certificate.event.venue}" if certificate.event.venue else ""
    c.drawCentredString(
        width / 2, height - 291,
        f"held on {certificate.event.event_date.strftime('%d %B, %Y')}{venue_text}"
    )

    # 12. Decorative seal — fills the empty middle space
    _draw_seal(c, width / 2, 210, navy, gold)

    # 13. Signatures: scribble + name + role, above a line
    sign_y = 118
    line_len = 155
    signers = [
        ('Md. Rezaul Karim', 'Moderator, GENESIS'),
        ('Nusrat Jahan Mim', 'President, GENESIS'),
        ('Prof. Dr. Golam Sarowar', 'Vice-Chancellor, GUB'),
    ]
    total_w = width - 2 * margin - 80
    slot_w = total_w / 3
    start_x = margin + 40

    for i, (name, role) in enumerate(signers):
        cx = start_x + slot_w * i + slot_w / 2

        _draw_signature(
            c, cx - line_len / 2 + 10, sign_y + 4, line_len - 20, 26,
            seed_text=name, color=navy,
        )

        c.setStrokeColor(gray)
        c.setLineWidth(1)
        c.line(cx - line_len / 2, sign_y, cx + line_len / 2, sign_y)

        c.setFont('Helvetica-Bold', 8.5)
        c.setFillColor(dark_text)
        c.drawCentredString(cx, sign_y - 12, name)

        c.setFont('Helvetica', 7.5)
        c.setFillColor(gray)
        c.drawCentredString(cx, sign_y - 22, role)

    # 14. QR code — bottom-left corner, clear of borders and signatures
    qr_reader = ImageReader(qr_buffer)
    qr_size = 42
    qr_x = inner_margin + 14
    qr_y = inner_margin + 14
    c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)
    c.setFont('Helvetica', 5.5)
    c.setFillColor(gray)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 8, 'Scan to verify')

    # 15. Certificate ID — bottom-right corner
    c.setFont('Helvetica', 7.5)
    c.setFillColor(gray)
    c.drawRightString(
        width - inner_margin - 14, inner_margin + 20,
        f'Cert ID: {str(certificate.certificate_id)[:8].upper()}'
    )

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