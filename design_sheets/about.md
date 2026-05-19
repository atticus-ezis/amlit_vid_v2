# Summary

Handle generation of Design Sheet images for characters and backgrounds from the Blueprint.
Character Design sheets will be bunched in groups of 5. Name pattern will be f"{project.title}\_character_design_sheet_v{i}.png"
Each Character obj from Blueprint will reference the group image they belong to.
Backgrounds are a simple 1 to 1. name is the background name from Blueprint

# Views

generate_design_sheets(blueprint_id):
build prompts from blueprint
use generate_images() from Images app
pop the b64 from 'data' and create the unique path + write
save Image with \*\*data
return Image Path url to be displayed in template

# Functions

get_character_images -> use range(0, len(characters), 5) -> get_character_designs_prompt -> generate_image -> save
get_background_images \* same pattern as above
