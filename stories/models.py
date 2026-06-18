from django.db import models
from projects.models import Project

class Story(models.Model):
    content=models.TextField(max_length=100000)
    project=models.OneToOneField(Project, related_name="story", on_delete=models.CASCADE)

    def __str__(self):
        return f"Story for {self.project.title}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.content = self.content.strip()
        super().save(*args, **kwargs)
