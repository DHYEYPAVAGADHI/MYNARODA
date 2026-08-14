import io
import time
import requests
import qrcode
import os
from datetime import date
from celery import shared_task
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from decouple import config

from apps.volunteers.models import PledgeRegistration

@shared_task(bind=True, max_retries=3)
def send_email_certificate_task(self, pledge_id):
    try:
        pledge = PledgeRegistration.objects.get(id=pledge_id)
        if not pledge.email or not pledge.certificate_pdf:
            return "No email or certificate to send."
            
        subject = "Your Green Naroda • Clean Naroda Certificate"
        body = f"""Dear {pledge.full_name},
        
Thank you for taking the Green Naroda • Clean Naroda Pledge.

Your official participation certificate is attached to this email.

Together for a Greener Tomorrow.

Regards,
Green Naroda • Clean Naroda Campaign
Ahmedabad Municipal Corporation"""

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email="prathampriority@mynaroda.in",
            to=[pledge.email],
        )
        
        # Attach the PDF
        if pledge.certificate_pdf:
            # If stored in Cloudinary, reading the file might need requests. If stored via django-cloudinary-storage, .read() usually works or we download it.
            # To be safe for remote storage:
            if hasattr(pledge.certificate_pdf, 'url'):
                try:
                    pdf_content = requests.get(pledge.certificate_pdf.url).content
                    email.attach(f"{pledge.certificate_id}.pdf", pdf_content, "application/pdf")
                except:
                    email.attach(pledge.certificate_pdf.name, pledge.certificate_pdf.read(), "application/pdf")
            else:
                email.attach(pledge.certificate_pdf.name, pledge.certificate_pdf.read(), "application/pdf")

        email.send(fail_silently=False)
        return "Email sent successfully."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

@shared_task(bind=True, max_retries=3)
def send_whatsapp_certificate_task(self, pledge_id):
    try:
        pledge = PledgeRegistration.objects.get(id=pledge_id)
        if not pledge.mobile_number or not pledge.certificate_pdf:
            return "No mobile number or certificate."

        phone_number = pledge.mobile_number
        if not phone_number.startswith('91'):
            phone_number = f"91{phone_number}"

        PHONE_NUMBER_ID = config('WHATSAPP_PHONE_NUMBER_ID', default='')
        ACCESS_TOKEN = config('WHATSAPP_ACCESS_TOKEN', default='')
        
        url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": "pledge_certificate",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "document",
                                "document": {
                                    "link": pledge.certificate_pdf.url if pledge.certificate_pdf else "",
                                    "filename": f"{pledge.certificate_id}.pdf"
                                }
                            }
                        ]
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": pledge.full_name}
                        ]
                    }
                ]
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        try:
            response.raise_for_status()
            pledge.whatsapp_sent = True
            pledge.save(update_fields=['whatsapp_sent'])
            return "WhatsApp sent successfully."
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                # Log error and mark failed, do not retry
                print(f"WhatsApp 401 Unauthorized: {response.text}")
                pledge.whatsapp_sent = False
                pledge.save(update_fields=['whatsapp_sent'])
                return "WhatsApp unauthorized, marked as FAILED."
            elif response.status_code in [429, 500, 502, 503, 504]:
                # Retry on rate limit or server error
                raise self.retry(exc=http_err, countdown=60)
            else:
                # Log other errors and fail without retry
                print(f"WhatsApp HTTP Error {response.status_code}: {response.text}")
                pledge.whatsapp_sent = False
                pledge.save(update_fields=['whatsapp_sent'])
                return f"WhatsApp failed with status {response.status_code}."
    except requests.exceptions.RequestException as exc:
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        # Any other unknown error, do not retry blindly for now, just mark failed
        pledge.whatsapp_sent = False
        pledge.save(update_fields=['whatsapp_sent'])
        return str(exc)


@shared_task(bind=True, max_retries=3)
def generate_certificate_task(self, pledge_id):
    try:
        pledge = PledgeRegistration.objects.get(id=pledge_id)

        # "Tree Pledge Certificate" — 80th Independence Day design, 1600x1131
        width, height = 1600, 1131
        BG = '#fdf9ef'
        GREEN = '#0e4c24'
        ORANGE = '#a84304'
        TEXT = '#21201b'
        MUTED = '#736e60'
        BORDER = '#e4dcc8'

        img = Image.new('RGB', (width, height), color=BG)
        draw = ImageDraw.Draw(img)

        draw.rectangle([28, 28, width - 28, height - 28], outline=GREEN, width=3)
        draw.rectangle([38, 38, width - 38, height - 38], outline=BORDER, width=1)

        static_dir = os.path.join(settings.BASE_DIR, 'static', 'images')

        def load_font(name, size):
            try:
                return ImageFont.truetype(os.path.join('/System/Library/Fonts', name), size)
            except IOError:
                return ImageFont.load_default()

        label_font = load_font('Helvetica.ttc', 15)
        value_font = load_font('Helvetica.ttc', 20)
        badge_font = load_font('Helvetica.ttc', 13)
        title_font = load_font('Times.ttc', 52)
        subtitle_font = load_font('Helvetica.ttc', 17)
        certify_font = load_font('Helvetica.ttc', 18)
        name_font = load_font('Times.ttc', 56)
        body_font = load_font('Helvetica.ttc', 18)
        sign_name_font = load_font('Helvetica.ttc', 19)
        sign_title_font = load_font('Helvetica.ttc', 14)

        # ── Organizer logos (top-left) ──
        org_logos = ['logo-mynaroda.jpeg', 'logo-bjp.png', 'logo-pratham.png']
        draw.text((90, 60), "ORGANIZERS", font=label_font, fill=MUTED)
        lx = 90
        for logo_name in org_logos:
            logo_path = os.path.join(static_dir, logo_name)
            if os.path.exists(logo_path):
                try:
                    logo = Image.open(logo_path).convert("RGBA")
                    logo.thumbnail((66, 66), Image.Resampling.LANCZOS)
                    mask = Image.new('L', (66, 66), 0)
                    ImageDraw.Draw(mask).ellipse((0, 0, 66, 66), fill=255)
                    img.paste(logo, (lx, 88), mask if logo.mode == 'RGBA' else None)
                except Exception:
                    pass
            lx += 78

        # ── Certificate No. / Date (top-right) ──
        draw.text((width - 90, 70), "Certificate No.", font=label_font, fill=MUTED, anchor="ra")
        draw.text((width - 90, 92), pledge.certificate_id or "—", font=value_font, fill=TEXT, anchor="ra")
        draw.text((width - 90, 130), "Date", font=label_font, fill=MUTED, anchor="ra")
        draw.text((width - 90, 152), timezone.localtime(pledge.created_at).strftime("%d %B %Y"), font=value_font, fill=TEXT, anchor="ra")

        # ── Center emblem + titles ──
        gncn_logo_path = os.path.join(static_dir, 'logo-gncn.png')
        cy = 200
        if os.path.exists(gncn_logo_path):
            try:
                emblem = Image.open(gncn_logo_path).convert("RGBA")
                emblem.thumbnail((110, 110), Image.Resampling.LANCZOS)
                img.paste(emblem, (int(width / 2 - 55), cy), emblem)
                cy += 130
            except Exception:
                cy += 20
        else:
            cy += 20

        draw.text((width / 2, cy), "GREEN NARODA · CLEAN NARODA", font=label_font, fill=GREEN, anchor="mm")
        cy += 40
        draw.text((width / 2, cy), "TREE PLEDGE CERTIFICATE", font=title_font, fill=GREEN, anchor="mm")
        cy += 55
        draw.text((width / 2, cy), "80TH INDEPENDENCE DAY · GREEN NARODA CLEAN NARODA CAMPAIGN", font=subtitle_font, fill=ORANGE, anchor="mm")
        cy += 45

        draw.line([(width / 2 - 90, cy), (width / 2 + 90, cy)], fill=BORDER, width=2)
        cy += 40

        name = pledge.full_name
        draw.text((width / 2, cy), "This is to certify that", font=certify_font, fill=TEXT, anchor="mm")
        cy += 50
        draw.text((width / 2, cy), name, font=name_font, fill=GREEN, anchor="mm")
        cy += 60

        fighter_name = pledge.dedicated_to.name if pledge.dedicated_to else "an Indian Freedom Fighter"
        body = (
            f"pledged to plant, protect, and nurture a tree in honor of India's 80th Independence Day,\n"
            f"one of 28,855 trees planted across Naroda under the Green Naroda · Clean Naroda campaign,\n"
            f"in tribute to {fighter_name} and the freedom fighters who won that freedom."
        )
        draw.multiline_text((width / 2, cy), body, font=body_font, fill=TEXT, anchor="mm", align="center", spacing=14)
        cy += 90

        # Tricolor strip
        strip_w, strip_h = 220, 5
        sx = int(width / 2 - strip_w / 2)
        for i, color in enumerate(['#FF9933', '#ffffff', '#128807']):
            seg_w = strip_w // 3
            draw.rectangle([sx + i * seg_w, cy, sx + (i + 1) * seg_w, cy + strip_h], fill=color)
        cy += 45

        # Tree No. / Tree Name / Plantation Location row
        col_labels = ["TREE NO.", "TREE NAME", "PLANTATION LOCATION"]
        col_values = [pledge.tree_number or "—", fighter_name, "Naroda"]
        col_x = [width / 2 - 320, width / 2 - 40, width / 2 + 240]
        for lx2, label, value in zip(col_x, col_labels, col_values):
            draw.text((lx2, cy), label, font=label_font, fill=MUTED, anchor="lm")
            draw.text((lx2, cy + 24), value, font=value_font, fill=TEXT, anchor="lm")
        cy += 90

        # Signatures
        sign_y = height - 220
        for sx2, sname, stitle in [
            (width / 2 - 320, "Shri Payalben Kukrani, MLA", "EVENT PRESIDENT"),
            (width / 2 + 320, "Shri Nikunj Rameshbhai Khakhi", "EVENT CONVENOR"),
        ]:
            draw.line([(sx2 - 100, sign_y), (sx2 + 100, sign_y)], fill=TEXT, width=1)
            draw.text((sx2, sign_y + 22), sname, font=sign_name_font, fill=GREEN, anchor="mm")
            draw.text((sx2, sign_y + 44), stitle, font=sign_title_font, fill=MUTED, anchor="mm")

        # Tricolor seal (center) — three horizontal bands clipped to a circle
        seal_r = 55
        seal_cx, seal_cy = width / 2, sign_y - 10
        seal_img = Image.new('RGBA', (seal_r * 2, seal_r * 2), (0, 0, 0, 0))
        seal_draw = ImageDraw.Draw(seal_img)
        band_h = (seal_r * 2) / 3
        for i, color in enumerate(['#FF9933', '#ffffff', '#128807']):
            seal_draw.rectangle([0, i * band_h, seal_r * 2, (i + 1) * band_h], fill=color)
        mask = Image.new('L', (seal_r * 2, seal_r * 2), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, seal_r * 2, seal_r * 2), fill=255)
        img.paste(seal_img, (int(seal_cx - seal_r), int(seal_cy - seal_r)), mask)
        draw.ellipse([seal_cx - seal_r, seal_cy - seal_r, seal_cx + seal_r, seal_cy + seal_r], outline=GREEN, width=2)
        inner_r = seal_r - 8
        draw.ellipse([seal_cx - inner_r, seal_cy - inner_r, seal_cx + inner_r, seal_cy + inner_r], fill=BG)
        draw.text((seal_cx, seal_cy - 8), "GREEN NARODA\nCLEAN NARODA", font=badge_font, fill=GREEN, anchor="mm", align="center", spacing=2)
        draw.text((seal_cx, seal_cy + 18), "VERIFIED", font=badge_font, fill=ORANGE, anchor="mm")

        # QR Code (bottom center, below signatures)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=4, border=2)
        qr.add_data(f"https://mynaroda.in/verify/{pledge.certificate_id}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((90, 90))
        img.paste(qr_img, (width - 160, height - 130))

        png_io = io.BytesIO()
        img.save(png_io, format='PNG')
        safe_cert_id = (pledge.certificate_id or str(pledge.id)).replace('/', '-')
        file_name_png = f"{safe_cert_id}.png"

        pdf_io = io.BytesIO()
        img.save(pdf_io, format='PDF', resolution=300.0)
        file_name_pdf = f"{safe_cert_id}.pdf"

        pledge.certificate_image.save(file_name_png, ContentFile(png_io.getvalue()), save=False)
        pledge.certificate_pdf.save(file_name_pdf, ContentFile(pdf_io.getvalue()), save=False)

        pledge.generated_at = timezone.now()
        pledge.save()

        # Trigger whatsapp and email tasks
        send_whatsapp_certificate_task.delay(pledge.id)
        send_email_certificate_task.delay(pledge.id)

        return "Certificate generated."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
