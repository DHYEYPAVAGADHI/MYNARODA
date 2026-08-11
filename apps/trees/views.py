import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.trees.models import Tree, TreeSpecies, TreePhoto, TreeMaintenanceLog, GrowthStage, TreeHealth
from apps.events.models import Event

class TreeListView(View):
    template_name = "trees/list.html"

    def get(self, request):
        species_id = request.GET.get("species")
        ward = request.GET.get("ward")
        status = request.GET.get("status")
        search_query = request.GET.get("q")

        trees = Tree.objects.filter(deleted_at__isnull=True)

        if species_id:
            trees = trees.filter(species_id=species_id)
        if ward:
            trees = trees.filter(ward=ward)
        if status:
            trees = trees.filter(verification_status=status)
        if search_query:
            trees = trees.filter(location_name__icontains=search_query) | trees.filter(contributor__full_name__icontains=search_query)

        # Prepare tree coordinate data for map markers (JSON format)
        map_data = []
        for t in trees:
            if t.latitude and t.longitude:
                map_data.append({
                    "id": str(t.id),
                    "lat": t.latitude,
                    "lng": t.longitude,
                    "species": t.species.name,
                    "health": t.get_health_status_display(),
                    "status": t.get_verification_status_display(),
                    "location": t.location_name or t.ward,
                    "url": f"/trees/{t.id}/",
                })

        species_list = TreeSpecies.objects.all()
        
        # Get unique wards for filter
        wards = Tree.objects.filter(ward__isnull=False).exclude(ward="").values_list("ward", flat=True).distinct()

        context = {
            "trees": trees.order_by("-planted_at"),
            "species_list": species_list,
            "wards": wards,
            "selected_species": species_id,
            "selected_ward": ward,
            "selected_status": status,
            "search_query": search_query,
            "map_data_json": json.dumps(map_data),
        }
        return render(request, self.template_name, context)


class TreeDetailView(View):
    template_name = "trees/detail.html"

    def get(self, request, pk):
        tree = get_object_or_404(Tree, id=pk)
        photos = TreePhoto.objects.filter(tree=tree).order_by("-created_at")
        maintenance_logs = TreeMaintenanceLog.objects.filter(tree=tree).order_by("-created_at")

        context = {
            "tree": tree,
            "photos": photos,
            "maintenance_logs": maintenance_logs,
            "health_choices": TreeHealth.choices,
            "growth_choices": GrowthStage.choices,
            "maintenance_types": TreeMaintenanceLog.MaintenanceType.choices,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        """Handle posting maintenance reports or growth logs."""
        tree = get_object_or_404(Tree, id=pk)
        action = request.POST.get("action")

        if not request.user.is_authenticated:
            messages.error(request, _("You must be logged in to submit updates."))
            return redirect("account_login")

        if action == "report_maintenance":
            issue_type = request.POST.get("issue_type")
            description = request.POST.get("description", "")
            if not issue_type:
                messages.error(request, _("Please specify the issue type."))
                return redirect("trees:detail", pk=pk)

            TreeMaintenanceLog.objects.create(
                tree=tree,
                reported_by=request.user,
                issue_type=issue_type,
                description=description
            )
            messages.success(request, _("Maintenance issue reported successfully. A coordinator will review it shortly."))
        
        elif action == "add_photo":
            image_url = request.POST.get("image_url")
            notes = request.POST.get("notes", "")
            if not image_url:
                messages.error(request, _("Please provide an image URL."))
                return redirect("trees:detail", pk=pk)

            # Set as primary if no primary exists
            is_primary = not TreePhoto.objects.filter(tree=tree, is_primary=True).exists()

            TreePhoto.objects.create(
                tree=tree,
                cloudinary_id="user_upload_" + timezone.now().strftime("%Y%m%d%H%M%S"),
                cloudinary_url=image_url,
                is_primary=is_primary,
                caption=notes,
                uploaded_by=request.user
            )
            messages.success(request, _("Growth photo added successfully."))

        return redirect("trees:detail", pk=pk)


class PlantTreeView(LoginRequiredMixin, View):
    template_name = "trees/plant.html"

    def get(self, request):
        species_list = TreeSpecies.objects.all()
        events = Event.objects.filter(status=Event.EventStatus.UPCOMING)
        return render(request, self.template_name, {
            "species_list": species_list,
            "events": events
        })

    def post(self, request):
        species_id = request.POST.get("species")
        location_name = request.POST.get("location_name", "")
        ward = request.POST.get("ward", "")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        event_id = request.POST.get("event")
        notes = request.POST.get("notes", "")
        image_url = request.POST.get("image_url", "")

        if not species_id or not latitude or not longitude:
            messages.error(request, _("Species and GPS coordinates are required."))
            return redirect("trees:plant")

        species = get_object_or_404(TreeSpecies, id=species_id)
        
        event = None
        if event_id:
            event = get_object_or_404(Event, id=event_id)

        # Create Tree
        tree = Tree.objects.create(
            species=species,
            contributor=request.user,
            planted_by=request.user,
            event=event,
            latitude=float(latitude),
            longitude=float(longitude),
            location_name=location_name,
            ward=ward,
            notes=notes,
            planted_at=timezone.now().date(),
            qr_code_url=f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://mynaroda.in/trees/{species_id}/" # Mock QR code
        )

        # Create initial TreePhoto if image uploaded
        if image_url:
            TreePhoto.objects.create(
                tree=tree,
                cloudinary_id="initial_plant_" + timezone.now().strftime("%Y%m%d%H%M%S"),
                cloudinary_url=image_url,
                is_primary=True,
                caption=_("Initial planting photo."),
                uploaded_by=request.user
            )

        messages.success(request, _("Tree logged successfully! It is pending coordinator field verification."))
        return redirect("trees:detail", pk=tree.id)
