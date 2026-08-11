import re

with open('templates/admin_panel/leadership_photos.html', 'r') as f:
    content = f.read()

# Update subtitle
content = content.replace(
    '<div class="ph-sub">Manage the 12 Mentoring Leadership photos on the homepage</div>',
    '<div class="ph-sub">Update the President and Convener portraits and Mentoring Leadership photos shown on the homepage.</div>'
)

# Extract the loop block to duplicate it
loop_block = """  <div class="lp-card">
    <form method="post" enctype="multipart/form-data">
      {% csrf_token %}
      
      <div class="lp-avatar-wrapper">
        {% if leader.url %}
          <img src="{{ leader.url }}" alt="{{ leader.name }}">
        {% else %}
          <div class="lp-avatar-placeholder">👤</div>
        {% endif %}
      </div>
      
      <div class="lp-name">{{ leader.name }}</div>
      <div class="lp-role">{{ leader.role }}</div>
      
      <div class="lp-actions">
        <label class="lp-btn-choose">
          Choose Photo
          <input type="file" name="{{ leader.field }}" accept="image/*" style="display:none;" onchange="previewImage(this, '{{ leader.field }}')">
        </label>
        
        <button type="submit" class="lp-btn-save" id="btn-save-{{ leader.field }}">
          Save Photo
        </button>
      </div>
    </form>
  </div>"""

new_html = f"""
<h2 style="font-size: 20px; font-weight: 700; color: var(--text); margin-top: 24px;">Main Planning Committee</h2>
<div class="lp-grid" style="margin-top: 16px; margin-bottom: 48px;">
  {{% for leader in committee_leaders %}}
{loop_block}
  {{% endfor %}}
</div>

<h2 style="font-size: 20px; font-weight: 700; color: var(--text);">Mentoring Leadership</h2>
<div class="lp-grid" style="margin-top: 16px;">
  {{% for leader in leaders %}}
"""

old_html = """<div class="lp-grid">
  {% for leader in leaders %}"""

content = content.replace(old_html, new_html)

with open('templates/admin_panel/leadership_photos.html', 'w') as f:
    f.write(content)
print("Updated admin template")
