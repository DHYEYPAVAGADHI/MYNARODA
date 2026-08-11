import os
import sys
import json
import urllib.request
import urllib.parse
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from modeltranslation.translator import translator

def translate_text(text, target_lang):
    if not text:
        return text
    if not isinstance(text, str):
        return text
    if text.strip() == "":
        return text
        
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
    
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            return "".join([d[0] for d in data[0] if d[0]])
    except Exception as e:
        print(f"Error translating '{text[:20]}...': {e}")
        return text

def run():
    print("Translating DB content...")
    for model, trans_opts in translator._registry.items():
        print(f"Processing model: {model.__name__}")
        try:
            objects = model.objects.all()
        except AttributeError:
            continue
            
        for obj in objects:
            changed = False
            for field in trans_opts.fields:
                en_val = getattr(obj, f"{field}_en", None)
                if not en_val:
                    continue
                
                # Hindi
                hi_val = getattr(obj, f"{field}_hi", None)
                # If hi_val starts with [Hi] or is empty, overwrite it
                if not hi_val or str(hi_val).startswith("[Hi]") or str(hi_val) == str(en_val):
                    new_hi = translate_text(en_val, "hi")
                    setattr(obj, f"{field}_hi", new_hi)
                    changed = True
                    print(f"  {field}_hi: {str(new_hi)[:30]}...")

                # Gujarati
                gu_val = getattr(obj, f"{field}_gu", None)
                if not gu_val or str(gu_val).startswith("[Gu]") or str(gu_val) == str(en_val):
                    new_gu = translate_text(en_val, "gu")
                    setattr(obj, f"{field}_gu", new_gu)
                    changed = True
                    print(f"  {field}_gu: {str(new_gu)[:30]}...")
            
            if changed:
                obj.save()
    print("Done!")

if __name__ == "__main__":
    run()
