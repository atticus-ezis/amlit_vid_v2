
import logging
from .models import Image
from blueprints.models import Blueprint, ImageStack
from django.shortcuts import get_object_or_404, render
from storyboards.api import openai_generation
from django.contrib import messages
from .scripts import generate_character_design_sheet_images 
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Case, When, Value, IntegerField, Count

logger = logging.getLogger(__name__)

image_sizes = {
    "landscape": Image.SizeChoice.LANDSCAPE,
    "portrait": Image.SizeChoice.PORTRAIT,
}


def storyboard_view(request, blueprint_pk):
    blueprint = get_object_or_404(Blueprint, pk=blueprint_pk)
    blueprint_stacks = ImageStack.objects.filter(blueprint=blueprint)
    
    image_size = image_sizes[request.POST.get("image_size") or "landscape"]
    image_style = (request.POST.get("image_style") or "pixar").lower()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "generate_character_sheets":
            character_stacks = blueprint_stacks.filter(
                category = ImageStack.StackCategory.CHARACTERS
            )
            for stack in character_stacks:
                if stack.images.exists():
                    continue
                else:
                    try:
                        generate_character_design_sheet_images(
                            stack=stack,
                            size=image_size, 
                            style=image_style
                        )
                    except RuntimeError as e:
                        messages.error(request, str(e))
                    except Exception:
                        messages.error(request, "An unexpected error occurred while generating images.")
    
    character_stacks = blueprint_stacks.filter(category=ImageStack.StackCategory.CHARACTERS)
    character_sheets = [{"id": stack.id, "name": stack.name, "images": stack.images.all()} for stack in character_stacks]
    missing_character_sheets = character_stacks.annotate(
        image_count=Count("images")
    ).filter(image_count=0).exists()


    context = {
        "character_sheets": character_sheets,
        "missing_character_sheets": missing_character_sheets,
    }
    return render(request, "storyboard.html", context)


def accept_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    image_stack = Image.objects.filter(image_stack=image.image_stack)
    existing_approved = image_stack.filter(review_status=Image.ReviewStatus.APPROVED).exclude(pk=image.pk).first()
    updated_id = None or existing_approved.id
    if existing_approved.exists():
        existing_approved.update(review_status=Image.ReviewStatus.PENDING)
    image.update(review_status=Image.ReviewStatus.APPROVED)

    return JsonResponse({
        "success": True,
        "status": image.review_status,
        "id": image.pk,
        "change_card_id": updated_id,
        "image_stack": image.image_stack,
    })

def reject_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    image.review_status = Image.ReviewStatus.REJECTED
    image.save(update_fields=["review_status"])

    has_approved = any(
        i.review_status == Image.ReviewStatus.APPROVED
        for i in image.generation_chain
    )

    images = [
        {"id": i.id, "status": i.review_status} for i in image.generation_chain
    ]

    return JsonResponse({
        "success": True,
        "status": image.review_status,
        "id": image.pk,
        "has_approved": has_approved,
        "images": images,
        "image_stack": image.image_stack,
    })