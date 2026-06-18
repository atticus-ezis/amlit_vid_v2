from typing import Optional
from amlit_video.settings import OPENAI_KEY
from openai import OpenAI, BadRequestError
from pathlib import Path
from .models import Image

sizes = {
    Image.DeviceType.DESKTOP: ["1536x1024"],
    Image.DeviceType.PHONE: ["1024x1536"],
}

model = "gpt-image-1"


def openai_generation(
    prompt: str, size: str = sizes[Image.DeviceType.DESKTOP][0], ai_model: str = model,
    reference_images: Optional[list[Path]] = None,
):
    client = OpenAI(api_key=OPENAI_KEY)
    format = "png"

    try:
        if not reference_images:
            result = client.images.generate(
                model=ai_model,
                prompt=prompt,
                size=size,
                output_format=format,
            )
        else:
            opened = [open(p, "rb") for p in reference_images]
            try:
                result = client.images.edit(
                    model=ai_model,
                    prompt=prompt,
                    image=opened if len(opened) > 1 else opened[0],
                    size=size,
                    output_format=format,
                )
            finally:
                for f in opened:
                    f.close()
    except BadRequestError as e:
        if e.code == "billing_hard_limit_reached":
            raise RuntimeError(
                "OpenAI billing limit reached. Add credits at platform.openai.com and try again."
            ) from None
        raise


    return {
        "image_64": result.data[0].b64_json,
        "model": ai_model,
        "size": Image.SizeChoice(size),
        "prompt": prompt,
    }

