from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.gallery.models import Photo, GalleryCategory, GalleryCollection, PhotoTag


class GalleryListView(View):
    template_name = "gallery/list.html"

    def get(self, request):
        category_slug = request.GET.get("category")
        collection_slug = request.GET.get("collection")
        search_query = request.GET.get("q")

        photos = Photo.objects.filter(approval_status=Photo.ApprovalStatus.APPROVED)

        if category_slug:
            photos = photos.filter(category__slug=category_slug)
        if collection_slug:
            photos = photos.filter(collections__slug=collection_slug)
        if search_query:
            photos = photos.filter(title__icontains=search_query) | photos.filter(location__icontains=search_query)

        categories = GalleryCategory.objects.all()
        collections = GalleryCollection.objects.filter(is_published=True)

        context = {
            "photos": photos.order_by("-created_at"),
            "categories": categories,
            "collections": collections,
            "selected_category": category_slug,
            "selected_collection": collection_slug,
            "search_query": search_query,
        }
        return render(request, self.template_name, context)


class SubmitPhotoView(LoginRequiredMixin, View):
    """
    Allows logged-in citizens and volunteers to submit campaign photographs.
    Photos are saved with PENDING approval status and only appear publicly
    after an administrator approves them from the admin panel.
    """
    template_name = "gallery/submit.html"

    def get(self, request):
        categories = GalleryCategory.objects.all()
        return render(request, self.template_name, {"categories": categories})

    def post(self, request):
        title = request.POST.get("title", "").strip()
        category_id = request.POST.get("category")
        location = request.POST.get("location", "").strip()
        image_file = request.FILES.get("image")

        # Validation
        if not title:
            messages.error(request, _("Please provide a title for the photograph."))
            return redirect("gallery:submit")

        if not category_id:
            messages.error(request, _("Please select a category."))
            return redirect("gallery:submit")

        if not image_file:
            messages.error(request, _("Please select an image file to upload."))
            return redirect("gallery:submit")

        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
        if image_file.content_type not in allowed_types:
            messages.error(request, _("Only JPEG, PNG, WebP, and GIF images are accepted."))
            return redirect("gallery:submit")

        # Validate file size (max 10 MB)
        max_size = 10 * 1024 * 1024
        if image_file.size > max_size:
            messages.error(request, _("Image file must be smaller than 10 MB."))
            return redirect("gallery:submit")

        category = get_object_or_404(GalleryCategory, id=category_id)

        # Create Photo record — status defaults to PENDING
        photo = Photo.objects.create(
            title=title,
            category=category,
            local_image=image_file,
            location=location,
            photographer=request.user,
            approval_status=Photo.ApprovalStatus.PENDING,
            cloudinary_id="local_upload_" + timezone.now().strftime("%Y%m%d%H%M%S"),
        )

        messages.success(
            request,
            _("Your photograph has been submitted for review. It will appear in the public gallery once approved by an administrator.")
        )
        return redirect("accounts:dashboard")
