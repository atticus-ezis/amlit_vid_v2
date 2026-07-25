import base64
import logging
from .models import Image
from blueprints.models import Blueprint, ImageStack
from django.shortcuts import get_object_or_404, render
from storyboards.api import openai_generation
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Case, When, Value, IntegerField

logger = logging.getLogger(__name__)

image_styles = {"pixar": "in a pixar semi realistic style"}
image_sizes = {
    "landscape": Image.SizeChoice.LANDSCAPE,
    "portrait": Image.SizeChoice.PORTRAIT,
}


def storyboard_view(request, blueprint_pk):
    blueprint = get_object_or_404(Blueprint, pk=blueprint_pk)
    blueprint_stacks = ImageStack.objects.filter(blueprint=blueprint)
    
    image_size = image_sizes[request.POST.get("image_size") or "landscape"]
    image_style = (request.POST.get("image_style") or "pixar").lower()

    available_images = Image.objects.filter(
        image_stack__in=blueprint_stacks,
        size=image_size,
        style=image_style
    )

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
    character_image_stacks = available_images.filter(image_stack__in=character_stacks).annotate(
        is_approved=Case(
            When(review_status=Image.ReviewStatus.APPROVED, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
        ).order_by(
            "is_approved", 
            "created_at"
        )

    context = {
        "character_image_stacks": character_image_stacks
    }
    return render(request, "storyboard.html", context)


def generate_character_design_sheet_images(
    stack: ImageStack, 
    size: str, 
    style: str
) -> list[Image]:
    try:
        with transaction.atomic():
            prompt = get_character_design_sheet_prompt(
                stack=stack,
                style=style
            )

            response = openai_generation(prompt=prompt, size=size)
            print(f"DEBUG: AI Response{response}")

            image_bytes = base64.b64decode(response["image_64"])
            filename = f"{stack.name}.png"
            img = Image.objects.create(
                image_stack=stack,
                ai_model=response["model"],
                prompt=prompt,
                size=response["size"],
                style=style,
            )
            img.image_file.save(
                filename,
                ContentFile(image_bytes),
                save=True,
            )
    except Exception:
        logger.exception(
            f"Failed generating character design sheets for {stack.name} with characters: {[character.name for character in stack.characters]}"
        )
        raise
    


def get_character_design_sheet_prompt(
        stack: ImageStack, 
        style: str
    ):
    style_description = image_styles[style]
    title = stack.blueprint.story.project.title
    character_list = (", ").join([character.name for character in stack.characters])
    prompt = f"Character design sheet for {title}, {character_list}, {style_description}"
    return prompt


def accept_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    # only one image in a chain can be approved
    # find existing images in the chain which are approved
    existing_accepted = [
        i for i in image.generation_chain 
        if i.review_status == Image.ReviewStatus.APPROVED 
        and i.pk != image.pk
    ]
    for i in existing_accepted:
        i.review_status = Image.ReviewStatus.REJECTED
        i.save(update_fields=["review_status"])

    image.review_status = Image.ReviewStatus.APPROVED
    image.save(update_fields=["review_status"])
    
    has_approved = any(
        i.review_status == Image.ReviewStatus.APPROVED
        for i in image.generation_chain
    )

    images = [
        {"id": i.id, "status": i.review_status} for i in image.generation_chain
    ]
    print(f"images --- {images}")

    return JsonResponse({
        "success": True,
        "status": image.review_status,
        "id": image.pk,
        "rejected_ids": [i.id for i in existing_accepted],
        "images": images,
        "has_approved": has_approved,
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