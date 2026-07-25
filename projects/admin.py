# Register your models here.
from django.contrib import admin

from projects.models import Project
from stories.models import Story
from blueprints.models import Blueprint, Character, ImageStack
from storyboards.models import Image

# Register your models here.


class CharacterInline(admin.TabularInline):
    model = Character


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Blueprint)
class BlueprintAdmin(admin.ModelAdmin):
    inlines = [
        CharacterInline,
    ]
    pass


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass

@admin.register(ImageStack)
class ImageStackAdmin(admin.ModelAdmin):
    pass
