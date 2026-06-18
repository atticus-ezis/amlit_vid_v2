import yaml
from django.apps import apps
from django.db import models
from stories.models import Story


class Blueprint(models.Model):

    class ReviewStatus(models.TextChoices):
        ACCEPTED = ("accepted", "Accepted")
        REJECTED = ("rejected", "Rejected")
        PENDING = ("pending", "Pending")

    class GenerationType(models.TextChoices):
        INITIAL = ("initial", "Initial")
        RE_PROMPT = ("re-prompt", "Re-prompt")
        MANUAL_EDIT = ("manual_edit", "Manual Edit")

    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="blueprints")
    content = models.JSONField(default=dict)
    generation_type = models.CharField(
        max_length=50,
        choices=GenerationType,
        default=GenerationType.INITIAL,
    )
    review_status = models.CharField(
        max_length=50,
        choices=ReviewStatus,
        default=ReviewStatus.PENDING,
    )
    re_prompt = models.TextField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # query all blueprints with matching story
        return f"Blueprint for {self.story.project.title}: {self.review_status} {self.updated_at:%Y-%m-%d %H:%M}"


    def as_yaml(self) -> str:
        return yaml.dump(
            self.content,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['story'],
                condition=models.Q(review_status='accepted'),
                name='unique_accepted_blueprint_per_story'
            ),
            models.CheckConstraint(
                condition=~models.Q(generation_type='re-prompt') | models.Q(re_prompt__isnull=False),
                name='re_prompt_required_for_re_prompt_type'
            ),
        ]


class Character(models.Model):
    blueprint = models.ForeignKey(Blueprint, on_delete=models.CASCADE, related_name="characters")
    key = models.SlugField(max_length=100)
    name = models.CharField(max_length=255)
    voice_id = models.TextField(null=True, blank=True)
    # character.images
    def __str__(self):
        return self.name


class Background(models.Model):
    blueprint = models.ForeignKey(Blueprint, on_delete=models.CASCADE, related_name="backgrounds")
    key = models.SlugField(max_length=100)
    name = models.CharField(max_length=255)
    # background.images

    def __str__(self):
        return self.name


class Scene(models.Model):
    blueprint = models.ForeignKey(Blueprint, on_delete=models.CASCADE, related_name="scenes")
    sequence = models.IntegerField()
    key = models.SlugField()
    duration = models.IntegerField()
    image_prompt = models.CharField(max_length=500) # prompt
    video_prompt = models.CharField(max_length=500)
    narration = models.TextField()

    reference_image_keys = models.JSONField(default=list)
    # scene.images

    def __str__(self):
        return f"Scene {self.sequence}: {self.key}"

    # pass to generate image
    def get_reference_images(self):
        Image = apps.get_model('images', 'Image')
        images = Image.objects.filter(
            key__in=self.reference_image_keys,
            review_status=Image.ReviewStatus.ACCEPTED,
        ).filter(
            models.Q(character__blueprint=self.blueprint) |
            models.Q(background__blueprint=self.blueprint) |
            models.Q(scene__blueprint=self.blueprint)
        )
        found_keys = set(images.values_list('key', flat=True))
        missing = set(self.reference_image_keys) - found_keys
        if missing:
            raise Image.DoesNotExist(f"Reference images not found: {missing}")
        return images


class Dialogue(models.Model):
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE, related_name="dialogues")
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="dialogues")
    line = models.TextField()

    def __str__(self):
        return f"{self.character}: {self.line[:50]}"
