import os
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.utils.timezone import now
from apps.student_portal.models import StudentCertificate

def generate_certificate(submission):
    # Create a base image (landscape A4 size approx: 1754 x 1240)
    width, height = 1754, 1240
    img = Image.new('RGB', (width, height), color='#F0FDF4') # Light green bg
    
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([40, 40, width-40, height-40], outline='#0B7A3B', width=10) # Deep Green
    draw.rectangle([55, 55, width-55, height-55], outline='#F59E0B', width=4) # Saffron
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Times.ttc", 80)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Times.ttc", 40)
        name_font = ImageFont.truetype("/System/Library/Fonts/Times.ttc", 100)
        text_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 35)
    except IOError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # Draw Title
    title = "CERTIFICATE OF PARTICIPATION"
    try:
        _, _, w, h = draw.textbbox((0, 0), title, font=title_font)
    except AttributeError:
        w, h = draw.textsize(title, font=title_font)
    draw.text(((width - w) / 2, 150), title, fill='#0B7A3B', font=title_font)

    # Subtitle
    subtitle = "Green Naroda • Clean Naroda Mission"
    try:
        _, _, w, h = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    except AttributeError:
        w, h = draw.textsize(subtitle, font=subtitle_font)
    draw.text(((width - w) / 2, 260), subtitle, fill='#F59E0B', font=subtitle_font)

    # Body text
    body1 = "This is to certify that"
    try:
        _, _, w, h = draw.textbbox((0, 0), body1, font=text_font)
    except AttributeError:
        w, h = draw.textsize(body1, font=text_font)
    draw.text(((width - w) / 2, 400), body1, fill='#111827', font=text_font)

    # Name
    name = submission.student_name.upper()
    try:
        _, _, w, h = draw.textbbox((0, 0), name, font=name_font)
    except AttributeError:
        w, h = draw.textsize(name, font=name_font)
    draw.text(((width - w) / 2, 480), name, fill='#0B7A3B', font=name_font)

    # Body 2
    body2 = f"from {submission.school_name} (Grade {submission.grade})"
    try:
        _, _, w, h = draw.textbbox((0, 0), body2, font=text_font)
    except AttributeError:
        w, h = draw.textsize(body2, font=text_font)
    draw.text(((width - w) / 2, 620), body2, fill='#111827', font=text_font)

    body3 = f"has successfully participated in the {submission.get_competition_type_display()}."
    try:
        _, _, w, h = draw.textbbox((0, 0), body3, font=text_font)
    except AttributeError:
        w, h = draw.textsize(body3, font=text_font)
    draw.text(((width - w) / 2, 680), body3, fill='#111827', font=text_font)

    body4 = "We appreciate their dedication to environmental awareness and nation-building."
    try:
        _, _, w, h = draw.textbbox((0, 0), body4, font=text_font)
    except AttributeError:
        w, h = draw.textsize(body4, font=text_font)
    draw.text(((width - w) / 2, 740), body4, fill='#111827', font=text_font)

    # Signatures
    sig_y = 950
    draw.line((200, sig_y, 500, sig_y), fill="#000", width=2)
    draw.text((250, sig_y + 10), "Campaign Lead", fill="#000", font=text_font)
    
    draw.line((width - 500, sig_y, width - 200, sig_y), fill="#000", width=2)
    draw.text((width - 450, sig_y + 10), "Hon'ble Mayor / AMC", fill="#000", font=text_font)

    # Date and ID
    draw.text((200, 1050), f"Date: {now().strftime('%d %B %Y')}", fill="#6B7280", font=text_font)
    draw.text((200, 1100), f"ID: {submission.participation_id}", fill="#6B7280", font=text_font)

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(f"https://mynaroda.in/verify/{submission.participation_id}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.resize((200, 200))
    img.paste(qr_img, (width - 400, 950))

    # Save to BytesIO (PNG)
    png_io = BytesIO()
    img.save(png_io, format='PNG')
    png_io.seek(0)

    # Save to BytesIO (PDF)
    pdf_io = BytesIO()
    img.save(pdf_io, format='PDF', resolution=100.0)
    pdf_io.seek(0)

    # Create StudentCertificate
    cert = StudentCertificate(submission=submission)
    file_name = f"GN_Certificate_{submission.participation_id}"
    
    cert.certificate_png.save(f"{file_name}.png", ContentFile(png_io.read()), save=False)
    cert.certificate_pdf.save(f"{file_name}.pdf", ContentFile(pdf_io.read()), save=False)
    cert.save()

    return cert
