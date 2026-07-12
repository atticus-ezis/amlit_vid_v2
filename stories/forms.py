from django import forms
from .models import Story


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"style": "width:100%;height:80vh;resize:none;"}
            )
        }
