import re

with open('templates/pages/landing.html', 'r') as f:
    content = f.read()

# 1. Update the gradient overlay
old_overlay = r'<div class="absolute inset-0" style="background: linear-gradient\(90deg, rgba\(255,255,255,0\.40\) 0%, rgba\(255,255,255,0\.15\) 100%\);"></div>'
new_overlay = '<div class="absolute inset-0 w-full lg:w-[65%]" style="background: linear-gradient(90deg, rgba(255,255,255,0.72) 0%, rgba(255,255,255,0) 100%); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); mask-image: linear-gradient(90deg, black 60%, transparent 100%); -webkit-mask-image: linear-gradient(90deg, black 60%, transparent 100%);"></div>'
# Fallback if old_overlay has different values:
pattern_overlay = r'<div class="absolute inset-0" style="background: linear-gradient\(90deg,.*?\);"></div>'
content = re.sub(pattern_overlay, new_overlay, content)

# 2. Main heading update
old_heading = r'<h2 class="font-serif text-\[#0F172A\] font-bold text-\[42px\] md:text-5xl lg:text-\[68px\] leading-tight mb-6 notranslate" translate="no">'
new_heading = '<h2 class="font-serif text-[#0B1020] font-extrabold text-[42px] md:text-5xl lg:text-[68px] leading-tight mb-6 notranslate" translate="no" style="text-shadow: 0 2px 12px rgba(255,255,255,0.65);">'
content = content.replace(old_heading, new_heading)

# 3. Paragraph text update
old_p = r'<p class="font-sans text-\[#1F2937\] text-\[18px\] leading-\[1\.8\] mb-10 max-w-\[600px\]">'
new_p = '<p class="font-sans font-medium text-[#111827] text-[18px] leading-[1.85] mb-10 max-w-[600px]" style="text-shadow: 0 1px 4px rgba(255,255,255,0.35);">'
content = content.replace(old_p, new_p)

# 4. Highlighted phrases
content = content.replace('<strong>Har Ghar Tiranga</strong>', '<strong class="text-[#0B1020] font-bold">Har Ghar Tiranga</strong>')
content = content.replace('<strong>11th to 15th August</strong>', '<strong class="text-[#0B1020] font-bold">11th to 15th August</strong>')
content = content.replace('<strong>Tiranga Yatra on 12th August</strong>', '<strong class="text-[#0B1020] font-bold">Tiranga Yatra on 12th August</strong>')

# 5. Button update
old_btn = r'class="bg-\[#FF7A00\] hover:bg-\[#E66E00\] hover:-translate-y-1 text-white font-bold h-14 px-7 rounded-full shadow-lg transition-all flex items-center justify-center gap-3 w-fit text-lg"'
new_btn = 'class="bg-[#FF7A00] hover:bg-[#E66E00] hover:-translate-y-1 text-[#FFFFFF] font-bold h-14 px-7 rounded-full shadow-lg transition-all flex items-center justify-center gap-3 w-fit text-lg"'
content = re.sub(old_btn, new_btn, content)

with open('templates/pages/landing.html', 'w') as f:
    f.write(content)
print("Updated landing.html")
