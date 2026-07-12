import pytest
from pathlib import Path
from projects.models import Project
from stories.models import Story
from blueprints.models import Blueprint


@pytest.mark.django_db
class TestBlueprint:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.story = (Path(__file__).parent / "story.txt").read_text()
        self.prompt = (
            Path(__file__).parent.parent / "generation" / "prompt.md"
        ).read_text()

    def test_blueprint_pipeline(self, client, mock_api):
        response = client.post("", {"title": "Little Red Riding Hood"})
        assert response.status_code == 302
        assert Project.objects.filter(title="Little Red Riding Hood").exists()

        story_response = client.post(response.url, {"content": self.story})
        assert story_response.status_code == 302
        assert Story.objects.filter(pk=1).exists()

        blueprint_response = client.post(story_response.url)

        # after review
        assert blueprint_response.status_code == 302
        assert len(Blueprint.objects.all()) == 1
