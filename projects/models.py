from pathlib import Path
from amlit_video import settings
from amlit_video.utils import slugify
from django.db import models


# Initiates project directory
# Stores path relative to MEDIA_ROOT
# Call paths with model functions
class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    root_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        if not self.pk:
            self.setup_directories()
        super().save(*args, **kwargs)

    def setup_directories(self):
        project_root=Path(settings.MEDIA_ROOT) / self.slug

        directories = [
            project_root / "design_sheets",
            project_root / "storyboard"
        ]
        for path in directories:
            path.mkdir(exist_ok=True, parents=True)

        self.root_path = str(project_root.relative_to(settings.MEDIA_ROOT))

    def get_root_path(self):
        return Path(settings.MEDIA_ROOT) / self.root_path
    
    def get_design_sheets_path(self) -> Path:
        return self.get_root_path() / "design_sheets"

    def get_storyboard_path(self) -> Path:
        return self.get_root_path() / "storyboard"