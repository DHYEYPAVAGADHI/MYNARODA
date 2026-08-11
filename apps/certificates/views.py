from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from apps.certificates.models import Certificate

class CertificateListView(LoginRequiredMixin, View):
    template_name = "certificates/list.html"

    def get(self, request):
        certificates = Certificate.objects.filter(user=request.user)
        return render(request, self.template_name, {"certificates": certificates})


class CertificateVerifyView(View):
    template_name = "certificates/verify.html"

    def get(self, request, certificate_number):
        certificate = Certificate.objects.filter(certificate_number=certificate_number).first()
        
        context = {
            "certificate": certificate,
            "certificate_number": certificate_number,
        }
        return render(request, self.template_name, context)
