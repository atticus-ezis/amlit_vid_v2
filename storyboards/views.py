
import logging
import json
from .models import Image
from blueprints.models import Blueprint, ImageStack
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from .scripts import generate_character_design_sheet_images, rank_queryset
from django.http import JsonResponse
from django.db.models import Count

logger = logging.getLogger(__name__)

image_sizes = {
    "landscape": Image.SizeChoice.LANDSCAPE,
    "portrait": Image.SizeChoice.PORTRAIT,
}

image_styles = {"pixar": "in a pixar semi realistic style"}


def storyboard_view(request, blueprint_pk):
    blueprint = get_object_or_404(Blueprint, pk=blueprint_pk)
    blueprint_stacks = ImageStack.objects.filter(blueprint=blueprint)
    
    image_size = image_sizes[request.POST.get("image_size") or "landscape"]
    image_style_value = (request.POST.get("image_style") or "pixar").lower()
    image_style = image_styles[image_style_value]


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
    
    available_images = Image.objects.filter(image_stack__in=blueprint_stacks, size=image_size, style=image_style_value)

    available_character_images = available_images.filter(image_stack__category=ImageStack.StackCategory.CHARACTERS)

    character_stacks = blueprint_stacks.filter(
        category=ImageStack.StackCategory.CHARACTERS, 
    )

    character_sheets = [{"id": stack.id, "name": stack.name, "images": rank_queryset(available_character_images.filter(image_stack=stack))} for stack in character_stacks]
    print(f"DEBUG: char sheets {character_sheets}")
    missing_character_sheets = False
    
    character_stacks = blueprint_stacks.filter(category=ImageStack.StackCategory.CHARACTERS)
    for stack in character_stacks:
        if not stack.images.exists():
            missing_character_sheets = True

    
    context = {
        "available_images": available_images,
        "character_sheets": character_sheets,
        "missing_character_sheets": missing_character_sheets,
    }
    return render(request, "storyboard.html", context)


def accept_image(request, pk):
    print("DEBUG: Accept Image")
    image = get_object_or_404(Image, pk=pk)
    image_stack = Image.objects.filter(image_stack=image.image_stack)
    existing_approved = image_stack.filter(review_status=Image.ReviewStatus.APPROVED).exclude(pk=image.pk).first()
    updated_id = existing_approved.pk if existing_approved else None
    if existing_approved:
        existing_approved.review_status=Image.ReviewStatus.PENDING
        existing_approved.save()
    image.review_status=Image.ReviewStatus.APPROVED
    if image.review_note is not None:
        image.review_note=""
    image.save()

    return JsonResponse({
        "success": True,
        "status": image.review_status,
        "id": image.pk,
        "change_card_id": updated_id,
        "image_stack_id": image.image_stack.id,
    })

def reject_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    image.review_status = Image.ReviewStatus.REJECTED
    image.save(update_fields=["review_status"])

    if request.body:
        data = json.loads(request.body)
        reason = data.get("reason")
        if reason:
            image.review_note = reason
            image.save(update_fields=["review_note"])

    return JsonResponse({
        "success": True,
        "status": image.review_status,
        "id": image.pk,
        "image_stack_id": image.image_stack.id,
    })

def reject_description(request, pk):
    print(f"description for id: {pk}")
    return JsonResponse({
        "REJECT NOTE SUCCESS"
    })

def regen_image(request, pk):
    body = json.loads(request.body)
    reprompt = body.get("reprompt")
    image_ids = body.get("reference_images")
    print(f"REPROMPT: {reprompt}, ids: {image_ids}")
    return JsonResponse({
        "REGEN SUCCESS"
    })