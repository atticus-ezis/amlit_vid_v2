import base64
import logging
from .models import Image
from blueprints.models import Blueprint
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, render
from storyboards.api import openai_generation
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q

logger = logging.getLogger(__name__)

image_styles = {"pixar": "in a pixar semi realistic style"}
image_sizes = {
    "landscape": Image.SizeChoice.LANDSCAPE,
    "portrait": Image.SizeChoice.PORTRAIT,
}

def get_display_images(
        blueprint: Blueprint,
        size: str,
        style: str,
):
    return Image.objects.filter(
            blueprint=blueprint,
            size=size,
            style=style,
        ).exclude(
            Q(review_status=Image.ReviewStatus.REJECTED) &
            ~Q(generation_type=Image.GenerationType.INITIAL)
        ).distinct()

# Create your views here.
# todo add a style input option
def storyboard_view(request, blueprint_pk):
    blueprint = get_object_or_404(Blueprint, pk=blueprint_pk)
    image_size = image_sizes[request.POST.get("image_size") or "landscape"]
    image_style = (request.POST.get("image_style") or "pixar").lower()

    characters = blueprint.characters.all()
    needed_character_sheets = (len(characters) + 4) // 5

    print("blueprint:", blueprint)
    print("size:", image_size)
    print("style:", image_style)

    display_images = get_display_images(
        blueprint=blueprint,
        size=image_size,
        style=image_style,
    )
    print(f"DEBUG: {display_images}")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "generate_character_sheets":
            character_sheets = display_images.filter(
                image_type=Image.ImageType.CHARACTER_DESIGN,
                generation_type=Image.GenerationType.INITIAL
            )
            character_sheet_count = character_sheets.count()

            if needed_character_sheets != character_sheet_count:
                print(f"DEBUG: {needed_character_sheets - character_sheet_count} Images NEEDED! Generating images")
                existing_character_ids = character_sheets.values_list(
                    "characters__id", flat=True
                )
                ungenerated_characters = characters.exclude(
                    id__in=existing_character_ids
                )
                try:
                    generate_character_design_sheet_images(
                        blueprint=blueprint,
                        characters=ungenerated_characters, 
                        size=image_size, 
                        style=image_style
                    )

                except RuntimeError as e:
                    messages.error(request, str(e))
                except Exception:
                    messages.error(request, "An unexpected error occurred while generating images.")


    latest_display_images = get_display_images(
        blueprint=blueprint,
        size=image_size,
        style=image_style,
    )

    existing_character_sheets = latest_display_images.filter(image_type=Image.ImageType.CHARACTER_DESIGN)
    


    # existing_background_sheets=Image.objects.filter(
    #     background__in=blueprint.backgrounds.all()
    #     ).exclude(generation_type=Image.GenerationType.REJECTED)

    # existing_scenes=Image.objects.filter(
    #     scene__in=blueprint.scenes.all()
    # ).exclude(generation_type=Image.GenerationType.REJECTED)

    context = {
        "existing_character_sheets": existing_character_sheets,
        "needed_character_sheets": needed_character_sheets
        # needed_character_sheets (int)
        # "existing_background_sheets": existing_background_sheets,
        # "existing_scenes": existing_scenes
    }
    return render(request, "storyboard.html", context)


def generate_character_design_sheet_images(
    blueprint: Blueprint, 
    characters: list[QuerySet], 
    size: str, 
    style: str
) -> list[Image]:
    batch_number = 5
    character_count = characters.count()
    image_count = 1

    for i in range(0, character_count, batch_number):
        try:
            with transaction.atomic():
                character_batch = list(characters[i : i + batch_number])
                prompt = get_character_design_sheet_prompt(
                    blueprint=blueprint,
                    characters=character_batch, 
                    style=style
                )

                response = openai_generation(prompt=prompt, size=size)
                print(f"OPEN AI Response{response}")

                image_bytes = base64.b64decode(response["image_64"])
                filename = f"character_design_sheet_{image_count}.png"
                key = f"{blueprint.story.project.slug}_character_design_sheet_{image_count}"

                img = Image.objects.create(
                    blueprint=blueprint,
                    key=key,
                    ai_model=response["model"],
                    prompt=prompt,
                    size=response["size"],
                    style=style,
                    image_type=Image.ImageType.CHARACTER_DESIGN,
                )
                img.characters.set(character_batch)
                img.image_file.save(
                    filename,
                    ContentFile(image_bytes),
                    save=True,
                )
                image_count += 1
                print(f"DEBUG: saved image {img.key}: url -> {img.image_file.url}")
        except Exception:
            logger.exception(
                "Failed generating character design sheets for project %s", blueprint.story.project.slug
            )
            raise
    


def get_character_design_sheet_prompt(
        blueprint: Blueprint, 
        characters: QuerySet, 
        style: str
    ):
    style_description = image_styles[style]
    story_title = blueprint.blueprint.story.project.title
    character_list = (", ").join([character.name for character in characters])
    prompt = f"Character design sheet for {story_title}, {character_list}, {style_description}"
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

    return JsonResponse({
        "success": True,
        "status": image.review_status,
        "id": image.pk,
        "rejected_ids": [i.id for i in existing_accepted]
    })

def reject_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    image.review_status = Image.ReviewStatus.REJECTED
    image.save(update_fields=["review_status"])

    return JsonResponse({
        "success": True,
        "status": image.review_status,
        "id": image.pk,
    })