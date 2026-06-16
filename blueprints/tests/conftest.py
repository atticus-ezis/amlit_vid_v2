import pytest
from unittest.mock import patch
from blueprints.tests.blueprint_fixture import FAKE_BLUEPRINT


@pytest.fixture
def mock_api():
    """
    Patches blueprint_api_call so tests never hit the Anthropic API.
    The patch target must match where the name is *used*, not where it's
    defined — both get_blueprint and yaml_error_catch_reprompt call
    blueprint_api_call from within the same module.
    """
    with patch(
        "blueprints.generation.script.blueprint_api_call",
        return_value=FAKE_BLUEPRINT,
    ) as mock:
        yield mock
