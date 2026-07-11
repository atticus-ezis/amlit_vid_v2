import anthropic
from .schema import BlueprintSchema
from django.conf import settings
from stories.models import Story
from blueprints.models import Blueprint, Character, Background, Scene, Dialogue

max_tokens = 4096

SYSTEM = '''
You are a script writter who will adapt a well-known children's story into a 2-3 minute YouTube video for children.
This script is part of an automated pipeline designed to generate the audio, images and video. 
You output only valid YAML — no markdown fences, no explanation, no commentary. 
Follow the format and rules provided exactly.
'''

models = {
    "opus":  "claude-opus-4-7",
    "sonnet":  "claude-sonnet-4-6",
}

def blueprint_api_call(prompt, model=models["opus"], system=SYSTEM):
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_KEY)
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        tools=[{
            "name": "output",
            "description": "Return structured output",
            "input_schema": BlueprintSchema.model_json_schema(),
        }],
        tool_choice={"type": "tool", "name": "output"},
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].input


def yaml_error_catch_reprompt(yaml_response):
    max_tries = 3
    fromat_errors = []
    while max_tries > 0:
        try:
            BlueprintSchema.model_validate(yaml_response)
            return yaml_response
        except Exception as e:
            fromat_errors.append(f"- {e}/n")
            max_tries -= 1
            retry_system = '''
            You correct yaml formatting errors for the provided yaml and error message.
            Return only the yaml content as specified by the provoded schema.
            '''
            retry_prompt = f"Formatting error: {e}\n Original yaml: {yaml_response}"
            yaml_response = blueprint_api_call(system=retry_system, prompt=retry_prompt, model=models["sonnet"])
    raise ValueError(f"Blueprint generation failed after 3 re-prompts.\n Errors: {fromat_errors}\n YAML: {yaml_response}") from last_error
    

def get_blueprint(prompt):
    blueprint_yaml=blueprint_api_call(prompt=prompt)
    return yaml_error_catch_reprompt(blueprint_yaml)


def re_prompt_blueprint(re_prompt, original_blueprint, script_criteria):
    re_prompt_system = '''
    You are a script editor who will make re-writes to the 'Original Script' based on the 'User Instructions'.
    Insure the re-write still complies with the original 'Script Criteria'. 
    Maintain the same structure. 
    '''

    prompt=f"User Instructions: {re_prompt}\n Original Script: {original_blueprint}\n Script Criteria: {script_criteria}"
    yaml_response = blueprint_api_call(system=re_prompt_system, prompt=prompt, model=models["opus"])
    return yaml_error_catch_reprompt(yaml_response)



########## save

def save_blueprint(yaml_content: dict, story: Story):
    data = yaml_content
    existing_blueprint = (
        Blueprint.objects.filter(story=story)
        .order_by("-updated_at")
        .first()
    )
    # if existing_blueprint and existing_blueprint.content == data:
    #     return existing_blueprint
    
    if existing_blueprint:
        blueprint = existing_blueprint
        blueprint.content = data
        blueprint.save()

        # delete old children (to avoid duplicates)
        blueprint.characters.all().delete()
        blueprint.backgrounds.all().delete()
        blueprint.scenes.all().delete()
    else:
        blueprint = Blueprint.objects.create(
            story=story,
            content=data,
        )


    character_map = {}
    for key, name in data["design_sheets"]["characters"].items():
        character = Character.objects.create(
            blueprint=blueprint,
            key=key,
            name=name,
        )
        character_map[key] = character

    for key, name in data["design_sheets"]["backgrounds"].items():
        Background.objects.create(
            blueprint=blueprint,
            key=key,
            name=name,
        )

    for scene in data["scenes"]:
        scene_object = Scene.objects.create(
            blueprint=blueprint,
            sequence=scene["sequence"],
            key=scene["key"],
            duration=scene["duration"],
            narration=scene["narration"],
            image_prompt=scene["image_prompt"],
            video_prompt=scene["video_prompt"],
            reference_image_keys=scene["reference_image_keys"],
        )
        for char_key, line in scene["dialogue"].items():
            Dialogue.objects.create(
                scene=scene_object,
                character=character_map[char_key],
                line=line,
            )
    return blueprint    


