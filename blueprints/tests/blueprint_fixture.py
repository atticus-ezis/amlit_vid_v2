"""
Fake API response for use in tests. Matches BlueprintSchema exactly so
save_blueprint() and yaml_error_catch_reprompt() both accept it.
"""

FAKE_BLUEPRINT = {
    "story_title": "Little Red Riding Hood",
    "design_sheets": {
        "characters": {
            "red": "Little Red Riding Hood",
            "wolf": "Big Bad Wolf",
            "grandma": "Grandmother",
        },
        "backgrounds": {
            "forest_path": "Sunny forest path with tall trees",
            "grandmas_cottage": "Cozy cottage in the woods",
        },
    },
    "scenes": [
        {
            "sequence": 1,
            "key": "scene_intro",
            "duration": 8,
            "narration": "Once upon a time, Little Red Riding Hood set off through the forest.",
            "image_prompt": "A cheerful girl in a red cloak walking along a forest path.",
            "video_prompt": "Pan across a sunlit forest path as Red skips forward.",
            "reference_image_keys": ["red", "forest_path"],
            "dialogue": {"red": "I'm off to Grandma's house!"},
        },
        {
            "sequence": 2,
            "key": "scene_wolf_meets",
            "duration": 10,
            "narration": "Deep in the forest she met the Big Bad Wolf.",
            "image_prompt": "A large grey wolf blocking the forest path, grinning.",
            "video_prompt": "Wolf steps out from behind a tree.",
            "reference_image_keys": ["wolf", "forest_path", "scene_intro"],
            "dialogue": {"wolf": "Where are you going, little girl?"},
        },
        {
            "sequence": 3,
            "key": "scene_wolf_races",
            "duration": 7,
            "narration": "The wolf raced ahead to Grandmother's cottage.",
            "image_prompt": "The wolf running through trees toward a cottage.",
            "video_prompt": "Fast zoom through the forest toward the cottage.",
            "reference_image_keys": ["wolf", "grandmas_cottage"],
            "dialogue": {"wolf": "I'll get there first!"},
        },
        {
            "sequence": 4,
            "key": "scene_grandma_door",
            "duration": 8,
            "narration": "The wolf knocked on Grandmother's door.",
            "image_prompt": "Wolf knocking at a wooden cottage door.",
            "video_prompt": "Close-up of wolf's paw knocking on the door.",
            "reference_image_keys": ["wolf", "grandmas_cottage"],
            "dialogue": {"grandma": "Who's there?"},
        },
        {
            "sequence": 5,
            "key": "scene_wolf_inside",
            "duration": 9,
            "narration": "The wolf crept inside and disguised himself.",
            "image_prompt": "Wolf tucked into bed wearing a bonnet.",
            "video_prompt": "Wolf pulls blanket up to chin and smiles.",
            "reference_image_keys": ["wolf", "grandmas_cottage"],
            "dialogue": {"wolf": "Just your sweet grandchild!"},
        },
        {
            "sequence": 6,
            "key": "scene_red_arrives",
            "duration": 10,
            "narration": "Red Riding Hood arrived at the cottage.",
            "image_prompt": "Red knocking on the cottage door, basket in hand.",
            "video_prompt": "Red walks up the garden path to the cottage door.",
            "reference_image_keys": ["red", "grandmas_cottage"],
            "dialogue": {"red": "Grandma, I've brought you some treats!"},
        },
        {
            "sequence": 7,
            "key": "scene_big_eyes",
            "duration": 10,
            "narration": "Red noticed something strange about Grandma.",
            "image_prompt": "Red looking puzzled at the wolf in bed.",
            "video_prompt": "Camera slowly zooms in on wolf's big eyes.",
            "reference_image_keys": ["red", "wolf", "grandmas_cottage"],
            "dialogue": {
                "red": "Grandma, what big eyes you have!",
                "wolf": "All the better to see you with!",
            },
        },
        {
            "sequence": 8,
            "key": "scene_rescued",
            "duration": 12,
            "narration": "A woodcutter heard the commotion and saved the day.",
            "image_prompt": "Woodcutter bursting through the door, axe raised.",
            "video_prompt": "Door flies open, light floods in, wolf flees.",
            "reference_image_keys": ["grandma", "grandmas_cottage"],
            "dialogue": {
                "grandma": "Help! Help!",
                "red": "Thank you!",
            },
        },
    ],
}
