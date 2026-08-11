import re

with open('templates/components/navbar.html', 'r') as f:
    content = f.read()

# CSS Updates

# 1. Update .gov-left gap
content = re.sub(
    r'\.gov-left\s*\{[^}]*\}',
    '''.gov-left {
    display: flex;
    align-items: flex-end;
    gap: 24px;
    padding-right: 20px;
    border-right: 1px solid rgba(0, 0, 0, 0.1);
  }''',
    content
)

# 2. Update .gov-org-logo
content = re.sub(
    r'\.gov-org-logo\s*\{[^}]*\}',
    '''.gov-org-logo {
    width: 72px;
    height: 72px;
    object-fit: contain;
    border-radius: 9999px;
    background: #FFFFFF;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 2px solid #E5E7EB;
    padding: 10px;
  }''',
    content
)

# 3. Update .gov-campaign-logo
content = re.sub(
    r'\.gov-campaign-logo\s*\{[^}]*\}',
    '''.gov-campaign-logo {
    width: 96px;
    height: 96px;
    object-fit: contain;
    flex-shrink: 0;
    background: #FFFFFF;
    border-radius: 9999px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 2px solid #E5E7EB;
    padding: 10px;
  }''',
    content,
    count=1 # Only replace the first one (the main desktop one)
)

# Update the tablet media query for .gov-campaign-logo
content = re.sub(
    r'\.gov-campaign-logo\s*\{\s*height:\s*72px;\s*\}',
    '''.gov-campaign-logo {
      width: 72px;
      height: 72px;
    }''',
    content
)

# Update the mobile media query for .gov-campaign-logo
content = re.sub(
    r'\.gov-campaign-logo\s*\{\s*height:\s*58px;\s*\}',
    '''.gov-campaign-logo {
      width: 58px;
      height: 58px;
    }''',
    content
)

# HTML Updates

# Left Organizer Logos
old_left_logos = """      <!-- My Naroda Samiti -->
      <div class="gov-org-item" title="My Naroda Samiti">
        <img src="{% static 'images/redesign/organizer-my-naroda-samiti.png' %}" alt="My Naroda Samiti"
          class="gov-org-logo">
        <span class="gov-org-label">My Naroda</span>
      </div>

      <!-- BJP Naroda -->
      <div class="gov-org-item" title="BJP Naroda">
        <img src="{% static 'images/redesign/organizer-bjp-naroda.png' %}" alt="BJP Naroda" class="gov-org-logo">
        <span class="gov-org-label">BJP Nation</span>
      </div>

      <!-- Pratham Priority -->
      <div class="gov-org-item" title="Pratham Priority">
        <div class="gov-org-logo-icon">🏆</div>
        <span class="gov-org-label">Pratham Priority</span>
      </div>"""

new_left_logos = """      <!-- My Naroda Samiti -->
      <div class="gov-org-item" title="My Naroda">
        <img src="{% static 'images/logo-mynaroda.jpeg' %}" alt="My Naroda" class="gov-org-logo">
        <span class="gov-org-label">My Naroda</span>
      </div>

      <!-- BJP Naroda -->
      <div class="gov-org-item" title="BJP Nation">
        <img src="{% static 'images/logo-bjp.png' %}" alt="BJP Nation" class="gov-org-logo">
        <span class="gov-org-label">BJP Nation</span>
      </div>

      <!-- Pratham Priority -->
      <div class="gov-org-item" title="Pratham Priority">
        <img src="{% static 'images/logo-pratham.png' %}" alt="Pratham Priority" class="gov-org-logo">
        <span class="gov-org-label">Pratham Priority</span>
      </div>"""

if old_left_logos in content:
    content = content.replace(old_left_logos, new_left_logos)
else:
    print("Could not find left logos HTML block")

# Center Campaign Logo
old_center_logo = """<a href="{% url 'cms:home' %}" aria-label="Green Naroda Clean Naroda Home">
        <img src="{% static 'images/logo.png' %}" alt="Green Naroda Clean Naroda Logo" class="gov-campaign-logo">
      </a>"""

new_center_logo = """<a href="{% url 'cms:home' %}" aria-label="Green Naroda Clean Naroda Home">
        <img src="{% static 'images/logo-gncn.png' %}" alt="Green Naroda Clean Naroda Logo" class="gov-campaign-logo">
      </a>"""

if old_center_logo in content:
    content = content.replace(old_center_logo, new_center_logo)
else:
    print("Could not find center logo HTML block")


with open('templates/components/navbar.html', 'w') as f:
    f.write(content)
print("Updated navbar.html")
