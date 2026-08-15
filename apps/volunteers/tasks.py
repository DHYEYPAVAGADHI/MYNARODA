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
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
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

        static_dir = os.path.join(settings.BASE_DIR, 'static', 'images')
        cert_images_dir = os.path.join(static_dir, 'certificate')
        font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'certificate')

        def load_font(name, size):
            try:
                return ImageFont.truetype(os.path.join(font_dir, name), size)
            except IOError:
                return ImageFont.load_default()

        label_font = load_font('Poppins-Regular.ttf', 14)
        value_font = load_font('Poppins-SemiBold.ttf', 18)
        title_font = load_font('Marcellus-Regular.ttf', 53)
        subtitle_font = load_font('Poppins-SemiBold.ttf', 16)
        certify_font = load_font('Poppins-Regular.ttf', 17)
        body_font = load_font('Poppins-Regular.ttf', 17)
        sign_name_font = load_font('Poppins-SemiBold.ttf', 17)
        sign_title_font = load_font('Poppins-Regular.ttf', 12)

        def fit_font(text, font_name, start_size, min_size, max_width):
            """Shrinks a font until `text` fits within max_width, so long
            names (participant or freedom fighter) never overflow the layout."""
            size = start_size
            font = load_font(font_name, size)
            while size > min_size and draw.textlength(text, font=font) > max_width:
                size -= 2
                font = load_font(font_name, size)
            return font

        def wrap_to_width(text, font, max_width, max_lines=2):
            """Greedy word-wrap so a name that's still too wide at the
            minimum font size wraps instead of overflowing its column."""
            words = text.split()
            lines = []
            current = ""
            i = 0
            while i < len(words) and len(lines) < max_lines:
                word = words[i]
                candidate = f"{current} {word}".strip()
                if not current or draw.textlength(candidate, font=font) <= max_width:
                    current = candidate
                    i += 1
                else:
                    lines.append(current)
                    current = ""
            if current:
                lines.append(current)
            if i < len(words):
                lines[-1] = lines[-1].rstrip(".,") + "…"
            return lines[:max_lines]

        # Double border frame (drawn first so the leaf art below sits on top of
        # it, matching the layering in the original template, instead of the
        # frame lines cutting across the leaves)
        draw.rectangle([28, 28, width - 28, height - 28], outline=GREEN, width=3)
        draw.rectangle([38, 38, width - 38, height - 38], outline=BORDER, width=1)

        # ── Decorative leaf border (left + right, faded toward center) ──
        border_path = os.path.join(cert_images_dir, 'border-leaves.png')
        if os.path.exists(border_path):
            try:
                border_w = 190
                border = Image.open(border_path).convert("RGBA")
                # Scale to fully COVER (border_w x height) without distorting
                # proportions, then center-crop the overflow — equivalent to
                # CSS object-fit:cover, instead of independently stretching
                # width and height (which warped the artwork).
                cover_scale = max(border_w / border.width, height / border.height)
                scaled_w = int(border.width * cover_scale)
                scaled_h = int(border.height * cover_scale)
                border = border.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
                # The source artwork (trunk + leaves) is anchored to the left
                # edge of the file with empty space to its right, so crop
                # from the left rather than the center.
                crop_x = 0
                crop_y = (scaled_h - height) // 2
                border = border.crop((crop_x, crop_y, crop_x + border_w, crop_y + height))
                # Fade out horizontally (fully opaque near the edge, transparent toward center)
                gradient = Image.new('L', (border_w, 1))
                for x in range(border_w):
                    frac = x / border_w
                    alpha = 255 if frac < 0.55 else max(0, int(255 * (1 - (frac - 0.55) / 0.45)))
                    gradient.putpixel((x, 0), alpha)
                gradient = gradient.resize((border_w, height))
                r, g, b, a = border.split()
                a = Image.composite(a, Image.new('L', a.size, 0), gradient)
                border.putalpha(a)
                img.paste(border, (0, 0), border)
                border_flipped = ImageOps.mirror(border)
                img.paste(border_flipped, (width - border_w, 0), border_flipped)
            except Exception:
                pass

        # ── Organizer logos (top-left) ──
        org_logos = ['logo-mynaroda.jpeg', 'logo-bjp.png', 'logo-pratham.png']
        draw.text((210, 60), "ORGANIZERS", font=label_font, fill=MUTED)
        lx = 210
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
        draw.text((width - 210, 70), "Certificate No.", font=label_font, fill=MUTED, anchor="ra")
        draw.text((width - 210, 92), pledge.certificate_id or "—", font=value_font, fill=TEXT, anchor="ra")
        draw.text((width - 210, 130), "Date", font=label_font, fill=MUTED, anchor="ra")
        draw.text((width - 210, 152), timezone.localtime(pledge.created_at).strftime("%d %B %Y"), font=value_font, fill=TEXT, anchor="ra")

        # ── Center emblem + titles ──
        gncn_logo_path = os.path.join(static_dir, 'logo-gncn.png')
        cy = 200
        if os.path.exists(gncn_logo_path):
            try:
                emblem = Image.open(gncn_logo_path).convert("RGBA")
                emblem.thumbnail((130, 130), Image.Resampling.LANCZOS)
                img.paste(emblem, (int(width / 2 - 65), cy), emblem)
                cy += 145
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

        # Participant name — auto-shrinks so long names never overflow the frame,
        # with vertical spacing scaled to the fitted font so it can't collide
        # with the lines above/below either.
        name = pledge.full_name
        draw.text((width / 2, cy), "This is to certify that", font=certify_font, fill=TEXT, anchor="mm")
        fitted_name_font = fit_font(name, 'CormorantGaramond-Italic.ttf', 56, 22, width - 600)
        cy += max(50, int(fitted_name_font.size * 1.0))
        draw.text((width / 2, cy), name, font=fitted_name_font, fill=GREEN, anchor="mm")
        cy += max(65, int(fitted_name_font.size * 1.4))

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

        # Tree No. / Tree Name / Plantation Location row — long values first shrink,
        # then wrap onto a second line rather than overflow into the next column.
        col_labels = ["TREE NO.", "TREE NAME", "PLANTATION LOCATION"]
        col_values = [pledge.tree_number or "—", fighter_name, "Naroda"]
        col_x = [width / 2 - 320, width / 2 - 40, width / 2 + 240]
        col_max_width = [260, 260, 260]
        row_extra = 0
        for lx2, label, value, max_w in zip(col_x, col_labels, col_values, col_max_width):
            draw.text((lx2, cy), label, font=label_font, fill=MUTED, anchor="lm")
            col_value_font = fit_font(value, 'Poppins-SemiBold.ttf', 18, 12, max_w)
            if draw.textlength(value, font=col_value_font) > max_w:
                lines = wrap_to_width(value, col_value_font, max_w, max_lines=2)
                line_h = col_value_font.size + 4
                for li, line in enumerate(lines):
                    draw.text((lx2, cy + 24 + li * line_h), line, font=col_value_font, fill=TEXT, anchor="lm")
                row_extra = max(row_extra, (len(lines) - 1) * line_h)
            else:
                draw.text((lx2, cy + 24), value, font=col_value_font, fill=TEXT, anchor="lm")
        cy += 90 + row_extra

        # Signatures — actual signature images, with name/role beneath
        sign_y = height - 220
        for sx2, sig_file, sname, stitle in [
            (width / 2 - 320, 'signature-payal-kukrani.png', "Shri Payalben Kukrani, MLA", "EVENT PRESIDENT"),
            (width / 2 + 320, 'signature-nikunj-khakhi.png', "Shri Nikunj Rameshbhai Khakhi", "EVENT CONVENOR"),
        ]:
            sig_path = os.path.join(cert_images_dir, sig_file)
            if os.path.exists(sig_path):
                try:
                    sig = Image.open(sig_path).convert("RGBA")
                    sig.thumbnail((190, 80), Image.Resampling.LANCZOS)
                    img.paste(sig, (int(sx2 - sig.width / 2), sign_y - sig.height - 4), sig)
                except Exception:
                    pass
            draw.line([(sx2 - 100, sign_y), (sx2 + 100, sign_y)], fill=TEXT, width=1)
            draw.text((sx2, sign_y + 22), sname, font=sign_name_font, fill=GREEN, anchor="mm")
            draw.text((sx2, sign_y + 44), stitle, font=sign_title_font, fill=MUTED, anchor="mm")

        # Tricolor seal (center) — three horizontal bands clipped to a circle
        seal_r = 50
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
        # Auto-fit the badge text to the inner circle's width instead of a
        # hardcoded size, so it never overflows past the ring.
        seal_text_max_width = int(inner_r * 1.7)
        seal_title_font = fit_font("CLEAN NARODA", 'Poppins-Bold.ttf', 12, 6, seal_text_max_width)
        seal_verified_font = fit_font("VERIFIED", 'Poppins-Bold.ttf', 12, 6, seal_text_max_width)
        draw.text((seal_cx, seal_cy - 8), "GREEN NARODA\nCLEAN NARODA", font=seal_title_font, fill=GREEN, anchor="mm", align="center", spacing=2)
        draw.text((seal_cx, seal_cy + 18), "VERIFIED", font=seal_verified_font, fill=ORANGE, anchor="mm")

        # QR Code (bottom center, below signatures)
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=4, border=2)
        qr.add_data(f"https://mynaroda.in/verify/{pledge.certificate_id}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((90, 90))
        img.paste(qr_img, (width - 250, height - 130))

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
