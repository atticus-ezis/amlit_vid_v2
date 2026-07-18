# Create your models here.
from django.db import models


def image_upload_path(instance, filename):
    blueprint_slug = instance.blueprint.story.project.slug
    return f"{blueprint_slug}/{instance.image_type}/{instance.generation_type}/{filename}"


class Image(models.Model):
    class DeviceType(models.TextChoices):
        PHONE = "phone", "Phone"
        DESKTOP = "desktop", "Desktop"

    class SizeChoice(models.TextChoices):
        LANDSCAPE = ("1536x1024",)
        PORTRAIT = ("1024x1536",)

    class GenerationType(models.TextChoices):
        INITIAL = "initial", "Initial"
        RE_PROMPT = "re_prompt", "Re-Prompt"
        USER_UPLOAD = "user_upload", "User Upload"

    class ImageType(models.TextChoices):
        CHARACTER_DESIGN = "character_design_sheet"
        BACKGROUND_DESIGN = "background_design_sheet"
        STORYBOARD = "storyboard"

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class AIModels(models.TextChoices):
        GPT_IMAGE_1 = "gpt-image-1"

    # can use - blueprint
    characters = models.ManyToManyField(
        "blueprints.Character", blank=True, related_name="images"
    )
    background = models.ForeignKey(
        "blueprints.Background",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="images",
    )
    scene = models.ForeignKey(
        "blueprints.Scene",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="images",
    )

    key = models.SlugField()

    image_file = models.ImageField(upload_to=image_upload_path)

    ai_model = models.CharField(max_length=100, choices=AIModels.choices)

    prompt = models.TextField()

    reference_images = models.ManyToManyField(
        "self",
        blank=True,
    )

    size = models.CharField(
        choices=SizeChoice.choices,
        default=SizeChoice.LANDSCAPE.value,
        max_length=20,
    )

    review_status = models.CharField(
        choices=ReviewStatus.choices, default=ReviewStatus.PENDING, max_length=20
    )

    image_type = models.CharField(choices=ImageType.choices, max_length=23)

    previous_generation = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="next_generation",
    )

    generation_type = models.CharField(
        max_length=50,
        choices=GenerationType.choices,
        default=GenerationType.INITIAL,
    )

    style = models.CharField(max_length=100)

    accuracy_score = models.IntegerField(
        null=True,
        blank=True,
    )

    # describe why it was rejected or got the score it did
    review_note = models.TextField(
        blank=True,
    )

    # describe what you did to generate the photo created outside the app
    upload_note = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    @property
    def blueprint(self):
        if self.scene:
            return self.scene.blueprint

        if self.background:
            return self.background.blueprint

        first_character = self.characters.first()
        if first_character:
            return first_character.blueprint

        raise ValueError("Image has no associated blueprint")

    @property
    def generation_chain(self):
        root = self.get_root_generation()
        chain = []
        current = root
        while current is not None:
            chain.append(current)
            if hasattr(current, "next_generation"):
                current = current.next_generation
            else:
                current = None
        return chain


    def serialize_reference(self):
        return {
            "id": self.id,
            "key": self.key,
            "image_type": self.image_type,
            "accuracy": self.accuracy_score,
        }

    def serialize_reference_list(self):
        return [ref.serialize_reference() for ref in self.reference_images.all()]

    def serialize_image(self):
        data = {
            "id": self.id,
            "key": self.key,
            "image_type": self.image_type,
            "accuracy_score": self.accuracy_score,
            "status": self.review_status,
            "generation_type": self.generation_type,
            "model": self.ai_model,
            "prompt": self.prompt,
            "reference_images": self.serialize_reference_list(),
        }
        if self.generation_type == self.GenerationType.USER_UPLOAD:
            data["upload_note"] = self.upload_note

        if self.review_note:
            data["review_note"] = self.review_note

    @property
    def is_root_generation(self):
        return self.previous_generation is None

    def get_root_generation(self):
        current = self
        while not current.is_root_generation:
            current = current.previous_generation
        return current

    def build_generation_chain(self):

        records = []

        current = self

        if not self.is_root_generation():
            raise ValueError(
                "build_generation_chain() can only be called on root images."
            )

        while current.review_status != self.ReviewStatus.APPROVED:
            next_gen = (
                Image.objects.filter(previous_generation=current)
                .prefetch_related("reference_images")
                .first()
            )

            if next_gen is None:
                break

            records.append(
                next_gen.serialize_image(),
            )

            current = next_gen

        return {
            "root_image": {
                "id": self.id,
                "key": self.name,
                "image_type": self.image_type,
                "accuracy_score": self.accuracy_score,
                "status": self.review_status,
                "model": self.ai_model,
                "prompt": self.prompt,
                "reference_images": self.serialize_reference_list(),
            },
            "generation_chain": records,
        }

    # def clean(self):
    #     super().clean()

    #     has_characters = self.characters.exists() if self.pk else bool(self.characters.all())
    #     has_background = self.background is not None
    #     has_scene = self.scene is not None

    #     generation_count = sum([has_characters, has_background, has_scene])
    #     if generation_count != 1:
    #         raise ValidationError(f"Image must belong to exactly 1 not {generation_count} type of either 'characters' 'background' or 'scene'")

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     self.full_clean()
