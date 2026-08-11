import textwrap

leaders = [
    ("Shri Nitin Nabin", "Hon'ble National President, BJP", "nitin_nabin_photo"),
    ("Shri Bhupendrabhai Patel", "Hon'ble Chief Minister, Gujarat", "bhupendrabhai_patel_photo"),
    ("Shri Jagdish Vishwakarma", "Hon'ble State President, BJP Gujarat", "jagdish_vishwakarma_photo"),
    ("Shri Harshbhai Sanghavi", "Hon'ble Dy. Chief Minister of Gujarat", "harshbhai_sanghavi_photo"),
    ("Shri Ratnakarji", "Hon'ble State Organization General Secretary", "ratnakarji_photo"),
    ("Shri Ajay Brahmbhatt", "State General Secretary, BJP Gujarat", "ajay_brahmbhatt_photo"),
    ("Shri Anirudhbhai Dave", "State General Secretary, BJP Gujarat", "anirudhbhai_dave_photo"),
    ("Dr. Prashantbhai Korat", "State General Secretary, BJP Gujarat", "prashantbhai_korat_photo"),
    ("Shri Hitendrasinh Chauhan", "State General Secretary, BJP Gujarat", "hitendrasinh_chauhan_photo"),
    ("Shri Prerakbhai Shah", "President, Karnavati Mahanagar BJP", "prerakbhai_shah_photo"),
    ("Shri Hasmukhbhai Patel", "Hon. Member of Parliament", "hasmukhbhai_patel_photo"),
    ("Shri Dineshbhai Makwana", "Hon. Member of Parliament", "dineshbhai_makwana_photo"),
]

html = """{% extends "admin/change_form.html" %}

{% block content %}
<div class="p-6">
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 font-serif">Leadership Photos</h1>
        <p class="text-gray-500 mt-2">Manage the photos displayed on the Mentoring Leadership section of the homepage.</p>
    </div>

    <form method="post" enctype="multipart/form-data" id="leadership_form">
        {% csrf_token %}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
"""

for name, role, field in leaders:
    card = f"""
            <div class="bg-white border border-gray-200 rounded-[24px] p-6 text-center shadow-sm hover:shadow-md transition-shadow">
                <div class="relative w-[120px] h-[120px] mx-auto mb-4 bg-gray-50 rounded-full border-4 border-gray-100 overflow-hidden flex items-center justify-center">
                    {{% if adminform.form.instance.{field} %}}
                        <img src="{{{{ adminform.form.instance.{field}.url }}}}" class="w-full h-full object-cover" alt="{name}">
                    {{% else %}}
                        <svg class="w-12 h-12 text-gray-300" fill="currentColor" viewBox="0 0 24 24"><path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                    {{% endif %}}
                </div>
                
                <h3 class="font-bold text-gray-900 text-lg mb-1">{name}</h3>
                <p class="text-sm text-gray-500 mb-6 min-h-[40px]">{role}</p>

                <div class="flex flex-col gap-3">
                    <label class="cursor-pointer bg-green-50 text-[#15803D] hover:bg-green-100 border border-green-200 font-semibold py-2.5 px-4 rounded-xl transition-colors">
                        Choose Photo
                        <input type="file" name="{field}" accept="image/*" class="hidden" onchange="previewImage(this, this.closest('.bg-white').querySelector('img, svg'))">
                    </label>
                    <button type="submit" name="_save" class="bg-[#15803D] hover:bg-[#166534] text-white font-semibold py-2.5 px-4 rounded-xl transition-colors shadow-sm">
                        Save Photo
                    </button>
                </div>
            </div>
"""
    html += card

html += """
        </div>
    </form>
</div>

<script>
function previewImage(input, previewElement) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            if (previewElement.tagName.toLowerCase() === 'svg') {
                var img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'w-full h-full object-cover';
                previewElement.parentNode.replaceChild(img, previewElement);
            } else {
                previewElement.src = e.target.result;
            }
            
            // Highlight the save button to prompt the user
            var saveBtn = input.closest('.bg-white').querySelector('button[type="submit"]');
            saveBtn.classList.remove('bg-[#15803D]');
            saveBtn.classList.add('bg-orange-500');
            saveBtn.classList.add('hover:bg-orange-600');
            saveBtn.innerText = 'Click to Save Changes';
        }
        reader.readAsDataURL(input.files[0]);
    }
}
</script>
{% endblock %}
"""

with open('templates/admin/cms/leadershipphotos/change_form.html', 'w') as f:
    f.write(html)
print('Generated change_form.html')
