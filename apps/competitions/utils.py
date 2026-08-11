import os
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.utils.timezone import now
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_organization_certificate(registration):
    """
    Generates both PNG and PDF certificates for an organization.
    Saves them directly to the registration model fields.
    """
    # Create PNG Certificate
    png_content = generate_png_certificate(registration)
    png_filename = f"{registration.registration_id}.png"
    registration.certificate_png.save(png_filename, png_content, save=False)

    # Create PDF Certificate
    pdf_content = generate_pdf_certificate(registration)
    pdf_filename = f"{registration.registration_id}.pdf"
    registration.certificate_pdf.save(pdf_filename, pdf_content, save=False)
    
    registration.certificate_generated = True
    registration.save(update_fields=['certificate_png', 'certificate_pdf', 'certificate_generated'])

def generate_png_certificate(registration):
    width, height = 1754, 1240
    img = Image.new('RGB', (width, height), color='#F0FDF4')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([40, 40, width-40, height-40], outline='#0B7A3B', width=10)
    draw.rectangle([55, 55, width-55, height-55], outline='#F59E0B', width=4)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Times.ttc", 80)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Times.ttc", 40)
        name_font = ImageFont.truetype("/System/Library/Fonts/Times.ttc", 90)
        text_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 35)
    except IOError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    title = "CERTIFICATE OF PARTICIPATION"
    try:
        _, _, w, h = draw.textbbox((0, 0), title, font=title_font)
    except AttributeError:
        w, h = draw.textsize(title, font=title_font)
    draw.text(((width - w) / 2, 150), title, fill='#0B7A3B', font=title_font)

    subtitle = "Green Naroda • Clean Naroda Campaign"
    try:
        _, _, w, h = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    except AttributeError:
        w, h = draw.textsize(subtitle, font=subtitle_font)
    draw.text(((width - w) / 2, 260), subtitle, fill='#F59E0B', font=subtitle_font)

    body1 = "This is to certify that"
    try:
        _, _, w, h = draw.textbbox((0, 0), body1, font=text_font)
    except AttributeError:
        w, h = draw.textsize(body1, font=text_font)
    draw.text(((width - w) / 2, 400), body1, fill='#111827', font=text_font)

    name = registration.organization_name.upper()
    try:
        _, _, w, h = draw.textbbox((0, 0), name, font=name_font)
    except AttributeError:
        w, h = draw.textsize(name, font=name_font)
    draw.text(((width - w) / 2, 480), name, fill='#0B7A3B', font=name_font)

    org_type = registration.organization_type.name if registration.organization_type else "Organization"
    body2 = f"has registered as a participating {org_type} in {registration.city}."
    try:
        _, _, w, h = draw.textbbox((0, 0), body2, font=text_font)
    except AttributeError:
        w, h = draw.textsize(body2, font=text_font)
    draw.text(((width - w) / 2, 620), body2, fill='#111827', font=text_font)

    body3 = "We appreciate your dedication to environmental awareness and nation-building."
    try:
        _, _, w, h = draw.textbbox((0, 0), body3, font=text_font)
    except AttributeError:
        w, h = draw.textsize(body3, font=text_font)
    draw.text(((width - w) / 2, 680), body3, fill='#111827', font=text_font)

    sig_y = 950
    draw.line((200, sig_y, 500, sig_y), fill="#000", width=2)
    draw.text((250, sig_y + 10), "Campaign Lead", fill="#000", font=text_font)
    
    draw.line((width - 500, sig_y, width - 200, sig_y), fill="#000", width=2)
    draw.text((width - 450, sig_y + 10), "Hon'ble Mayor / AMC", fill="#000", font=text_font)

    draw.text((200, 1050), f"Date: {now().strftime('%d %B %Y')}", fill="#6B7280", font=text_font)
    draw.text((200, 1100), f"ID: {registration.registration_id}", fill="#6B7280", font=text_font)

    verify_url = f"https://mynaroda.in/verify/organization/{registration.registration_id}/"
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_w, qr_h = qr_img.size
    img.paste(qr_img, (width - qr_w - 200, 1000))

    out = BytesIO()
    img.save(out, format='PNG', quality=95)
    out.seek(0)
    return ContentFile(out.read())

def generate_pdf_certificate(registration):
    out = BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(out, pagesize=landscape(A4))
    
    # Background
    c.setFillColorRGB(240/255, 253/255, 244/255)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # Borders
    c.setStrokeColorRGB(11/255, 122/255, 59/255)
    c.setLineWidth(10)
    c.rect(40, 40, width-80, height-80)
    
    c.setStrokeColorRGB(245/255, 158/255, 11/255)
    c.setLineWidth(4)
    c.rect(55, 55, width-110, height-110)
    
    # Content
    c.setFillColorRGB(11/255, 122/255, 59/255)
    c.setFont("Times-Bold", 40)
    c.drawCentredString(width/2, height - 120, "CERTIFICATE OF PARTICIPATION")
    
    c.setFillColorRGB(245/255, 158/255, 11/255)
    c.setFont("Times-Roman", 20)
    c.drawCentredString(width/2, height - 160, "Green Naroda • Clean Naroda Campaign")
    
    c.setFillColorRGB(17/255, 24/255, 39/255)
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 250, "This is to certify that")
    
    c.setFillColorRGB(11/255, 122/255, 59/255)
    c.setFont("Times-Bold", 45)
    c.drawCentredString(width/2, height - 320, registration.organization_name.upper())
    
    c.setFillColorRGB(17/255, 24/255, 39/255)
    c.setFont("Helvetica", 16)
    org_type = registration.organization_type.name if registration.organization_type else "Organization"
    c.drawCentredString(width/2, height - 390, f"has registered as a participating {org_type} in {registration.city}.")
    c.drawCentredString(width/2, height - 420, "We appreciate your dedication to environmental awareness and nation-building.")
    
    # Signatures
    sig_y = height - 520
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    
    c.line(120, sig_y, 300, sig_y)
    c.drawCentredString(210, sig_y - 20, "Campaign Lead")
    
    c.line(width - 300, sig_y, width - 120, sig_y)
    c.drawCentredString(width - 210, sig_y - 20, "Hon'ble Mayor / AMC")
    
    # Metadata
    c.setFillColorRGB(107/255, 114/255, 128/255)
    c.setFont("Helvetica", 14)
    c.drawString(120, 60, f"Date: {now().strftime('%d %B %Y')}")
    c.drawString(120, 40, f"ID: {registration.registration_id}")
    
    # QR Code (since we are doing this quickly, we'll draw it via temp file)
    verify_url = f"https://mynaroda.in/verify/organization/{registration.registration_id}/"
    qr = qrcode.QRCode(version=1, box_size=4, border=0)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_path = f"/tmp/qr_{registration.registration_id}.png"
    qr_img.save(qr_path)
    
    c.drawImage(qr_path, width - 180, 40, width=80, height=80)
    os.remove(qr_path)
    
    c.save()
    out.seek(0)
    return ContentFile(out.read())
