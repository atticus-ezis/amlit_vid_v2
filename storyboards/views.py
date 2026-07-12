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

logger = logging.getLogger(__name__)

styles = {"pixar": "in a pixar semi realistic style"}
batch_number = 5


# Create your views here.
# todo add a style input option
def storyboard_view(request, blueprint_pk):
    blueprint = get_object_or_404(Blueprint, pk=blueprint_pk)

    if request.method == "POST":
        print("post request started")
        # add these to settings later
        selected_style = request.POST.get("image_style")
        style = styles[selected_style]
        size = (
            Image.SizeChoice.LANDSCAPE
            if request.POST.get("image_size") == "landscape"
            else Image.SizeChoice.PORTRAIT
        )
        action = request.POST.get("action")

        if action == "generate_character_sheets":
            print("DEBUG: generating character sheet...")
            # creates the first batch of INITIAL images
            characters = blueprint.characters.all()
            number_of_needed_sheets = (len(characters) + 4) // batch_number
            completed_sheets = (
                Image.objects.filter(
                    characters__blueprint=blueprint,
                    generation_type=Image.GenerationType.INITIAL,
                    size=size,
                    style=style,
                )
                .distinct()
                .count()
            )

            # both are 0...
            # needed is 1 and completed is 5
            print(f"needed {number_of_needed_sheets} completed {completed_sheets}")
            if number_of_needed_sheets != completed_sheets:
                print("Images NEEDED! Generating images")
                existing_character_ids = completed_sheets.values_list(
                    "characters__id", flat=True
                )
                ungenerated_characters = characters.exclude(
                    id__in=existing_character_ids
                )
                try:
                    character_sheet_objects = generate_character_design_sheet_images(
                        characters=ungenerated_characters, size=size.value, style=style
                    )
                    print(
                        f"Completed {len(character_sheet_objects)} of {number_of_needed_sheets}"
                    )
                except ValueError as e:
                    messages.error(request, str(e))
            else:
                print("DEBUG: sheet(s) exist")
                print(f"Existing... \n{completed_sheets}")

    existing_character_sheets = (
        Image.objects.filter(characters__in=blueprint.characters.all())
        .exclude(generation_type=Image.ReviewStatus.REJECTED)
        .distinct()
    )

    print(f"Existing character sheets {existing_character_sheets}")

    # existing_background_sheets=Image.objects.filter(
    #     background__in=blueprint.backgrounds.all()
    #     ).exclude(generation_type=Image.GenerationType.REJECTED)

    # existing_scenes=Image.objects.filter(
    #     scene__in=blueprint.scenes.all()
    # ).exclude(generation_type=Image.GenerationType.REJECTED)

    context = {
        "existing_character_sheets": existing_character_sheets,
        # "existing_background_sheets": existing_background_sheets,
        # "existing_scenes": existing_scenes
    }
    return render(request, "storyboard.html", context)


def generate_character_design_sheet_images(
    characters: list[QuerySet], size: str, style: str
) -> list[Image]:
    character_count = characters.count()
    image_count = 1
    first_char = characters.first()
    if not first_char:
        raise ValueError(
            "No character provided to 'def generate_character_design_sheet_images"
        )

    project_slug = first_char.blueprint.story.project.slug
    images = []
    for i in range(0, character_count, batch_number):
        try:
            with transaction.atomic():
                character_batch = list(characters[i : i + batch_number])
                prompt = get_character_design_sheet_prompt(
                    characters=character_batch, style=style
                )
                print(f"DEBUG: prompt... {prompt}")
                print("waiting for ai...")
                response = openai_generation(prompt=prompt, size=size)
                print(f"OPEN AI Response{response}")

                image_bytes = base64.b64decode(response["image_64"])
                filename = f"character_design_sheet_{image_count}.png"

                img = Image.objects.create(
                    key=f"{project_slug}_character_design_sheet_{image_count}",
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
                images.append(img)
                image_count += 1
                print(f"DEBUG: saved image {img.key}: url -> {img.image_file.url}")
        except Exception:
            logger.exception(
                "Failed generating character design sheets for project %s", project_slug
            )
    return images


def get_character_design_sheet_prompt(characters: QuerySet, style: str):
    first_char = characters[0]
    if not first_char:
        raise ValueError("No character in prompt")
    story_title = first_char.blueprint.story.project.title
    character_list = (", ").join([character.name for character in characters])
    prompt = f"Character design sheet for {story_title}, {character_list}, {style}"
    return prompt
