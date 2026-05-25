import pytest
from pathlib import Path
from projects.models import Project
from stories.models import Story
from blueprints.models import Blueprint
from django.shortcuts import get_object_or_404

# create a test database
# create a project
# add story
# call generate function
# call validate function
# call review function 
# call save function

@pytest.mark.django_db
def test_blueprint_pipeline(client):
    response = client.post('', {
        "title": "Little Red Riding Hood"
    })
    assert response.status_code == 302
    assert Project.objects.filter(title="Little Red Riding Hood").exists()
    

    story_content = (Path(__file__).parent / "story.txt").read_text()
    story_response = client.post(response.url, {
        "content": story_content
    })
    assert story_response.status_code == 302
    assert Story.objects.filter(pk=1).exists()

    blueprint_response = client.post(story_response.url)
    
    # after review
    assert blueprint_response.status_code == 302



@pytest.mark.django_db
def test_blueprint_scripts():
    # build prompt
    # api call
    # validate + auto re-prompt
    # accept or re-prompt or manually edit
    pass