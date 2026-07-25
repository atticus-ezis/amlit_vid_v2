from blueprints.models import ImageStack
from .models import Image
from storyboards.api import openai_generation
from django.db import transaction
import base64
from django.core.files.base import ContentFile
import logging
logger = logging.getLogger(__name__)

image_styles = {"pixar": "in a pixar semi realistic style"}

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