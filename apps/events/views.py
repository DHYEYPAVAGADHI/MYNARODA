from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.events.models import Event, EventRegistration

class EventListView(View):
    template_name = "events/list.html"

    def get(self, request):
        status_filter = request.GET.get("status", "upcoming")
        
        events = Event.objects.filter(is_published=True)
        if status_filter == "upcoming":
            events = events.filter(starts_at__gte=timezone.now())
        elif status_filter == "past":
            events = events.filter(starts_at__lt=timezone.now())

        context = {
            "events": events.order_by("starts_at"),
            "status_filter": status_filter,
        }
        return render(request, self.template_name, context)


class EventDetailView(View):
    template_name = "events/detail.html"

    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug, is_published=True)
        
        is_registered = False
        if request.user.is_authenticated:
            is_registered = EventRegistration.objects.filter(
                event=event, 
                user=request.user, 
                is_cancelled=False
            ).exists()

        context = {
            "event": event,
            "is_registered": is_registered,
            "registration_count": event.registration_count,
            "is_full": event.is_full,
        }
        return render(request, self.template_name, context)


class EventRegisterView(LoginRequiredMixin, View):
    """View to handle event registration/cancel registration."""
    
    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug, is_published=True)
        action = request.POST.get("action", "register")

        if action == "register":
            if event.is_full:
                messages.error(request, _("This event is already full!"))
                return redirect("events:detail", slug=slug)

            registration, created = EventRegistration.objects.get_or_create(
                event=event,
                user=request.user,
                defaults={"is_cancelled": False}
            )
            if not created and registration.is_cancelled:
                registration.is_cancelled = False
                registration.save()

            messages.success(request, _("You have successfully registered for this event! Your QR pass has been generated in your Dashboard."))
            
        elif action == "cancel":
            registration = EventRegistration.objects.filter(event=event, user=request.user).first()
            if registration:
                registration.is_cancelled = True
                registration.save()
                messages.success(request, _("Your registration has been cancelled."))
            else:
                messages.error(request, _("You are not registered for this event."))

        return redirect("events:detail", slug=slug)
