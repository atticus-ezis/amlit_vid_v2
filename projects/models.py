from amlit_video import settings
from amlit_video.utils import slugify
from django.db import models


# Initiates project directory
# Stores path relative to MEDIA_ROOT
# Call paths with model functions
class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.pk:
            self.root_path.mkdir(exist_ok=True, parents=True)
        super().save(*args, **kwargs)

    @property
    def root_path(self):
        return settings.MEDIA_ROOT / self.slug

    def __str__(self):
        return self.title
