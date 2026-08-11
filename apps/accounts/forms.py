"""
Accounts App — Forms
=====================
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserRole


class CustomSignupForm(forms.Form):
    """
    Custom signup form fields that allauth will mix in.
    Adds full_name, phone, and role selection.
    """
    
    PUBLIC_ROLES = (
        (UserRole.CITIZEN, _("Citizen")),
        (UserRole.VOLUNTEER, _("Volunteer")),
        (UserRole.PHOTOGRAPHER, _("Photographer")),
    )

    full_name = forms.CharField(
        max_length=150,
        required=True,
        label=_("Full Name"),
        widget=forms.TextInput(attrs={"placeholder": _("E.g. John Doe")}),
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        label=_("Phone Number (Optional)"),
        widget=forms.TextInput(attrs={"placeholder": _("+91XXXXXXXXXX")}),
    )
    role = forms.ChoiceField(
        choices=PUBLIC_ROLES,
        required=True,
        initial=UserRole.CITIZEN,
        label=_("Register As"),
    )

    def signup(self, request, user):
        """
        Invoked automatically by allauth when signup is successful.
        Updates the user with our custom fields.
        """
        user.full_name = self.cleaned_data["full_name"]
        user.phone = self.cleaned_data.get("phone", "")
        user.role = self.cleaned_data["role"]
        
        # We don't save the user here; allauth will save it.
        return user
