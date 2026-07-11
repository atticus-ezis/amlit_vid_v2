import yaml
from django.contrib import messages
from stories.models import Story
from django.shortcuts import get_object_or_404, render, redirect
from pathlib import Path
from blueprints.script import get_blueprint, save_blueprint, re_prompt_blueprint
from .models import Blueprint
from .forms import BlueprintRepromptForm, BlueprintDetailForm
from django.db import transaction
from blueprints.schema import BlueprintSchema
from django.contrib import messages

prompt_markdown = (Path(__file__).parent / "prompt.md").read_text()


def blueprint_view(request, story_pk):
    story = get_object_or_404(Story, pk=story_pk)
    existing_blueprints = Blueprint.objects.filter(story=story).order_by("-pk")
    context = {
        "story": story,
        "existing_blueprints": existing_blueprints,
    }
    if request.method == 'POST' and not existing_blueprints.exists():
        prompt = prompt_markdown.replace("{{insert story here}}", story.content)
        try:
            validated_blueprint_data = get_blueprint(prompt=prompt)
            blueprint = save_blueprint(yaml_content=validated_blueprint_data, story=story)
            return redirect("blueprint-detail", blueprint_pk=blueprint.pk)
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, "blueprint.html", context)

    return render(request, "blueprint.html", context)


def blueprint_detail(request, blueprint_pk):
    blueprint = get_object_or_404(Blueprint, pk=blueprint_pk)
    existing_blueprints = Blueprint.objects.filter(story=blueprint.story).exclude(pk=blueprint.pk)

    context = {
        "blueprint": blueprint,
        "existing_blueprints": existing_blueprints,
        "form": BlueprintDetailForm(initial={"yaml_content": blueprint.as_yaml()}),
        "reprompt_form": BlueprintRepromptForm(),
    }

    if request.method == "POST":
        if "save" in request.POST:
            form = BlueprintDetailForm(request.POST)
            context["form"] = form
            if form.is_valid():
                try:
                    content = yaml.safe_load(form.cleaned_data["yaml_content"])
                    BlueprintSchema.model_validate(content)
                    blueprint.content = content
                    blueprint.generation_type=Blueprint.GenerationType.MANUAL_EDIT,
                    blueprint.save()
                except Exception as e:
                    messages.error(request, str(e))
                return redirect("blueprint-detail", blueprint_pk=new_blueprint.pk, context=context)

        # save the blueprint
        elif "submit" in request.POST:
            with transaction.atomic():
                # change status of existing blueprint if ACCEPTED
                blueprint.story.blueprints.filter(
                    review_status=Blueprint.ReviewStatus.ACCEPTED
                ).exclude(
                    pk=blueprint.pk
                ).update(review_status=Blueprint.ReviewStatus.PENDING)
                blueprint.review_status=Blueprint.ReviewStatus.ACCEPTED
                blueprint.save()
                blueprint = save_blueprint(yaml_content=blueprint.content, story=blueprint.story)
                return redirect("storyboard", blueprint_pk=blueprint.pk)

        elif "re_prompt" in request.POST:
            reprompt_form = BlueprintRepromptForm(request.POST)
            context["reprompt_form"] = reprompt_form
            if reprompt_form.is_valid():
                re_prompt=reprompt_form.cleaned_data["re_prompt"]
                try:
                    yaml_content = re_prompt_blueprint(
                        re_prompt=re_prompt,
                        original_blueprint=blueprint.as_yaml(),
                        script_criteria=prompt_markdown,
                    )
                    new_blueprint = save_blueprint(yaml_content=yaml_content, story=blueprint.story)
                    new_blueprint.generation_type = Blueprint.GenerationType.RE_PROMPT
                    new_blueprint.re_prompt = re_prompt
                    new_blueprint.save()
                    return redirect("blueprint-detail", blueprint_pk=new_blueprint.pk)
                except ValueError as e:
                    messages.error(request, str(e))

    return render(request, "blueprint_detail.html", context)

