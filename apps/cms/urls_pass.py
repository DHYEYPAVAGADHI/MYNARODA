import re

with open("apps/cms/urls.py", "r") as f:
    content = f.read()

# Insert before the closing bracket of urlpatterns
new_url = '    path("har-ghar-tiranga/pass/<str:token_id>/", views.HarGharTirangaPassView.as_view(), name="tiranga_pass"),\n]'
content = content.replace(']', new_url)

with open("apps/cms/urls.py", "w") as f:
    f.write(content)
