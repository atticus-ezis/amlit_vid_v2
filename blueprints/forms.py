import yaml
from django import forms
from pydantic import ValidationError as PydanticValidationError
from blueprints.schema import BlueprintSchema


class BlueprintDetailForm(forms.Form):
    yaml_content = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 30,
            "class": "form-control font-monospace",
            "style": "white-space: pre; overflow-wrap: normal; overflow-x: scroll;",
        }),
        label="Blueprint YAML",
    )

    def clean_yaml_content(self):
        text = self.cleaned_data["yaml_content"]
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise forms.ValidationError(f"Invalid YAML: {e}")
        if not isinstance(data, dict):
            raise forms.ValidationError("YAML must be a mapping at the top level.")
        try:
            BlueprintSchema.model_validate(data)
        except PydanticValidationError as e:
            raise forms.ValidationError(f"Schema validation failed:\n{e}")
        return text


class BlueprintRepromptForm(forms.Form):
    re_prompt = forms.CharField(max_length=500, required=True)
