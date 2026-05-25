from django.db import models

class Image(models.Model):

    class DeviceType(models.TextChoices):
        PHONE = "Phone", "phone"
        DESKTOP = "Desktop", "desktop"

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

    character = models.ForeignKey('blueprints.Character', null=True, blank=True, on_delete=models.CASCADE, related_name="images")
    background = models.ForeignKey('blueprints.Background', null=True, blank=True, on_delete=models.CASCADE, related_name="images")
    scene = models.ForeignKey('blueprints.Scene', null=True, blank=True, on_delete=models.CASCADE, related_name="images")
    ##### 

    key = models.SlugField()

    relative_path = models.CharField()

    ai_model = models.CharField(
        max_length=100,
        choices=AIModels.choices
    )

    prompt = models.TextField()

    reference_images = models.ManyToManyField(
        "self",
        blank=True,
    )
    
    device_type = models.CharField(
	    choices=DeviceType.choices,
    )

    accuracy_score = models.IntegerField(
        null=True,
        blank=True,
    )

    review_status = models.CharField(
		choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )

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

	# describe why it was rejected or got the score it did
    review_note = models.TextField(
        blank=True,
    ) 
    
    # describe what youy did to generate the photo created outside the app
    upload_note = models.TextField(
	    blank=True,
	  )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(character__isnull=False, background__isnull=True, scene__isnull=True) |
                    models.Q(character__isnull=True, background__isnull=False, scene__isnull=True) |
                    models.Q(character__isnull=True, background__isnull=True, scene__isnull=False)
                ),
                name='image_belongs_to_exactly_one_owner'
            ),
            models.CheckConstraint(
                condition=models.Q(generation_type='user_upload') | models.Q(upload_note__isnull=True),
                name='upload_note_required_when_user_uploads'
            ),
            models.CheckConstraint(
                condition=models.Q(generation_type='user_upload') | models.Q(prompt__isnull=False),
                name='prompt_not_required_for_user_upload'
            ),
        ]


    @property
    def image_type(self):
        if self.character_id:
            return "character"
        elif self.background_id:
            return "background"
        return "scene"

    def serialize_reference(self):
        return {
            "id": self.id,
            "key": self.key,
            "image_type": self.image_type,
            "accuracy": self.accuracy_score
        }
    
    def serialize_reference_list(self):
        return [
            ref.serialize_reference()
            for ref in self.reference_images.all()
        ]
        
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
            "reference_images": self.serialize_reference_list()
        }
        if self.generation_type == self.GenerationType.USER_UPLOAD:
            data["upload_note"] = self.upload_note

        if self.review_note:
            data["review_note"] = self.review_note
          
		     
    def is_root_generation(self):
        return self.previous_generation is None

    def get_root_generation(self):
        current = self
        while not current.is_root_generation():
            current = current.previous_generation
        return current

    def build_generation_chain(self):

        records = []

        current = self

        if not self.is_root_generation():

            raise ValueError(
                "build_generation_chain() "
                "can only be called on root images."
            )

        while True:

            next_gen = (
                Image.objects
                .filter(previous_generation=current)
                .prefetch_related("reference_images")
                .first()
            )

            if next_gen is None:
                break

            records.append(
                next_gen.serialize_image(),
            )

            if next_gen.review_status == self.ReviewStatus.APPROVED:
                break

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
                "reference_images": self.serialize_reference_list()
            },

            "generation_chain": records,
        }
