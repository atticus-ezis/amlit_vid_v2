# Create your models here.
from django.db import models
from blueprints.models import ImageStack


def image_upload_path(instance, filename):
    blueprint_slug = instance.blueprint.story.project.slug
    return f"{blueprint_slug}/{instance.image_type}/{instance.generation_type}/{filename}"


class Image(models.Model):
    class SizeChoice(models.TextChoices):
        LANDSCAPE = ("1536x1024",)
        PORTRAIT = ("1024x1536",)

    class GenerationType(models.TextChoices):
        INITIAL = "initial", "Initial"
        RE_PROMPT = "re_prompt", "Re-Prompt"
        USER_UPLOAD = "user_upload", "User Upload"
    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class AIModels(models.TextChoices):
        GPT_IMAGE_1 = "gpt-image-1"

    # multiple choice
    generation_type = models.CharField(
        max_length=50,
        choices=GenerationType.choices,
        default=GenerationType.INITIAL,
    )
    ai_model = models.CharField(max_length=100, choices=AIModels.choices)
    size = models.CharField(
        choices=SizeChoice.choices,
        default=SizeChoice.LANDSCAPE.value,
        max_length=20,
    )
    review_status = models.CharField(
        choices=ReviewStatus.choices, default=ReviewStatus.PENDING, max_length=20
    )


    # identifierss
    image_stack = models.ForeignKey(
        ImageStack,
        on_delete=models.CASCADE,
        related_name="images"
    )
    style = models.CharField(max_length=100)
    image_file = models.ImageField(upload_to=image_upload_path)
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # generation
    prompt = models.TextField()
    reference_images = models.ManyToManyField(
        "self",
        blank=True,
        related_name="referenced_by",
    )
    parent_image = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    accuracy_score = models.IntegerField(
        null=True,
        blank=True,
    )
    review_note = models.TextField(
        blank=True,
    )
    upload_note = models.TextField(
        blank=True,
    )

    @property
    def generation_chain(self):
        # get every parent
        chain=[self]
        current = self
        while current.parent_image is not None:
            chain.append(current.parent_image)
            current = current.parent_image
        return chain[::-1]

    
    