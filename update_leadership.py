import re

with open('templates/pages/landing.html', 'r') as f:
    content = f.read()

new_html = """
    <!-- Row 1: Featured Leader (Alone) -->
    <div class="flex justify-center mb-10">
      <div class="ml-card reveal" tabindex="0" style="max-width:320px;width:100%;">
        <div class="ml-avatar mx-auto mb-5" style="width:112px;height:112px;">
          {% if leadership_photos and leadership_photos.nitin_nabin_photo %}
            <img src="{{ leadership_photos.nitin_nabin_photo.url }}" alt="Shri Nitin Nabin" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-4xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name text-lg">Shri Nitin Nabin</h3>
        <p class="ml-role">Hon&apos;ble National President, BJP</p>
      </div>
    </div>

    <!-- Row 2: Four Leaders in One Line -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6 mb-10">
      <div class="ml-card reveal reveal-delay-1" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.bhupendrabhai_patel_photo %}
            <img src="{{ leadership_photos.bhupendrabhai_patel_photo.url }}" alt="Shri Bhupendrabhai Patel" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-3xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Shri Bhupendrabhai Patel</h3>
        <p class="ml-role">Hon&apos;ble Chief Minister, Gujarat</p>
      </div>
      <div class="ml-card reveal reveal-delay-2" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.jagdish_vishwakarma_photo %}
            <img src="{{ leadership_photos.jagdish_vishwakarma_photo.url }}" alt="Shri Jagdish Vishwakarma" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-3xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Shri Jagdish Vishwakarma</h3>
        <p class="ml-role">Hon&apos;ble State President, BJP Gujarat</p>
      </div>
      <div class="ml-card reveal reveal-delay-3" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.harshbhai_sanghavi_photo %}
            <img src="{{ leadership_photos.harshbhai_sanghavi_photo.url }}" alt="Shri Harshbhai Sanghavi" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-3xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Shri Harshbhai Sanghavi</h3>
        <p class="ml-role">Hon&apos;ble Dy. Chief Minister of Gujarat</p>
      </div>
      <div class="ml-card reveal reveal-delay-4" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.ratnakarji_photo %}
            <img src="{{ leadership_photos.ratnakarji_photo.url }}" alt="Shri Ratnakarji" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-3xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Shri Ratnakarji</h3>
        <p class="ml-role">Hon'ble State Organization General Secretary</p>
      </div>
    </div>

    <!-- Row 3: State General Secretaries — 4 cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6 mb-10">
      <div class="ml-card reveal reveal-delay-1" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.ajay_brahmbhatt_photo %}
            <img src="{{ leadership_photos.ajay_brahmbhatt_photo.url }}" alt="Shri Ajay Brahmbhatt" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-2xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Shri Ajay Brahmbhatt</h3>
        <p class="ml-role">State General Secretary, BJP Gujarat</p>
      </div>
      <div class="ml-card reveal reveal-delay-2" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.anirudhbhai_dave_photo %}
            <img src="{{ leadership_photos.anirudhbhai_dave_photo.url }}" alt="Shri Anirudhbhai Dave" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-2xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Shri Anirudhbhai Dave</h3>
        <p class="ml-role">State General Secretary, BJP Gujarat</p>
      </div>
      <div class="ml-card reveal reveal-delay-3" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.prashantbhai_korat_photo %}
            <img src="{{ leadership_photos.prashantbhai_korat_photo.url }}" alt="Dr. Prashantbhai Korat" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-2xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Dr. Prashantbhai Korat</h3>
        <p class="ml-role">State General Secretary, BJP Gujarat</p>
      </div>
      <div class="ml-card reveal reveal-delay-4" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.hitendrasinh_chauhan_photo %}
            <img src="{{ leadership_photos.hitendrasinh_chauhan_photo.url }}" alt="Shri Hitendrasinh Chauhan" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-2xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Shri Hitendrasinh Chauhan</h3>
        <p class="ml-role">State General Secretary, BJP Gujarat</p>
      </div>
    </div>

    <!-- Row 4: Karnavati & Parliamentary Leadership — 3 cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6 max-w-4xl mx-auto">
      <div class="ml-card reveal reveal-delay-1" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.prerakbhai_shah_photo %}
            <img src="{{ leadership_photos.prerakbhai_shah_photo.url }}" alt="Shri Prerakbhai Shah" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-2xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Shri Prerakbhai Shah</h3>
        <p class="ml-role">President, Karnavati Mahanagar BJP</p>
      </div>
      <div class="ml-card reveal reveal-delay-2" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.hasmukhbhai_patel_photo %}
            <img src="{{ leadership_photos.hasmukhbhai_patel_photo.url }}" alt="Shri Hasmukhbhai Patel" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-2xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Shri Hasmukhbhai Patel</h3>
        <p class="ml-role">Hon. Member of Parliament</p>
      </div>
      <div class="ml-card reveal reveal-delay-3" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:96px;height:96px;">
          {% if leadership_photos and leadership_photos.dineshbhai_makwana_photo %}
            <img src="{{ leadership_photos.dineshbhai_makwana_photo.url }}" alt="Shri Dineshbhai Makwana" class="w-full h-full object-cover rounded-full">
          {% else %}
            <i class="fa-solid fa-user-tie text-2xl text-[#9CA3AF]" aria-hidden="true"></i>
          {% endif %}
        </div>
        <h3 class="ml-name">Shri Dineshbhai Makwana</h3>
        <p class="ml-role">Hon. Member of Parliament</p>
      </div>
    </div>
"""

# Extract the header block which we want to keep
header_pattern = r'(<!-- Section Header -->\s*<div class="text-center mb-16 reveal">[\s\S]*?</div>)'
header_match = re.search(header_pattern, content)
header_html = header_match.group(1) if header_match else ''

# Replace everything from "<!-- Row 1" to "</div>\n</section>"
pattern = r'<!-- Row 1: National & State Leadership — 4 cards -->[\s\S]*?<!-- Row 4: Karnavati & Parliamentary Leadership — 3 cards -->[\s\S]*?</div>\n    </div>'

def replacer(match):
    return new_html.strip()

content = re.sub(pattern, replacer, content)

with open('templates/pages/landing.html', 'w') as f:
    f.write(content)
print("Updated landing.html")
