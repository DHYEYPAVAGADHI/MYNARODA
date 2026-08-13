import re

with open("apps/cms/views.py", "r") as f:
    content = f.read()

# Add the new view
new_view = """
class HarGharTirangaPassView(View):
    template_name = "pages/har_ghar_tiranga_pass.html"

    def get(self, request, token_id):
        from django.shortcuts import get_object_or_404
        from apps.cms.models import HarGharTirangaRegistration
        registration = get_object_or_404(HarGharTirangaRegistration, token_id=token_id)
        
        # Build absolute URL for QR code
        pass_url = request.build_absolute_uri(
            reverse("cms:tiranga_pass", kwargs={"token_id": token_id})
        )
        
        return render(request, self.template_name, {
            "registration": registration,
            "pass_url": pass_url,
        })
"""

# Insert it before the last view or just append it
content += new_view

with open("apps/cms/views.py", "w") as f:
    f.write(content)
