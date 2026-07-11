from typing import Annotated
from pydantic import BaseModel, Field, model_validator

class SceneSchema(BaseModel):
    sequence: int
    key: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    duration: Annotated[int, Field(ge=5, le=15)]
    narration: str
    image_prompt: str
    video_prompt: str
    reference_image_keys: Annotated[list[str], Field(min_length=1, max_length=3)]
    dialogue: dict[str, str]

class DesignSheetsSchema(BaseModel):
    characters: dict[str, str]
    backgrounds: dict[str, str]

class BlueprintSchema(BaseModel):
    story_title: str
    design_sheets: DesignSheetsSchema
    scenes: Annotated[list[SceneSchema], Field(min_length=8, max_length=13)]

    @model_validator(mode='after')
    def validate_keys(self):
        character_keys = set(self.design_sheets.characters.keys())
        background_keys = set(self.design_sheets.backgrounds.keys())
        seen_scene_keys: set[str] = set()

        for scene in sorted(self.scenes, key=lambda s: s.sequence):
            invalid_dialogue = set(scene.dialogue.keys()) - character_keys
            if invalid_dialogue:
                raise ValueError(
                    f"Scene '{scene.key}' dialogue references unknown character keys: {invalid_dialogue}"
                )

            valid_ref_keys = character_keys | background_keys | seen_scene_keys
            invalid_refs = set(scene.reference_image_keys) - valid_ref_keys
            if invalid_refs:
                raise ValueError(
                    f"Scene '{scene.key}' reference_image_keys contains unknown keys: {invalid_refs}"
                )

            seen_scene_keys.add(scene.key)

        return self

# client = anthropic.Anthropic()

# response = client.messages.create(
#     model="claude-opus-4-7",
#     max_tokens=4096,
#     messages=[{"role": "user", "content": YOUR_PROMPT_WITH_FEW_SHOTS}],
#     output_config={
#         "format": {
#             "type": "json_schema",
#             "schema": Script.model_json_schema(),
#         }
#     },
# )

# script = Script.model_validate_json(response.content[0].text)