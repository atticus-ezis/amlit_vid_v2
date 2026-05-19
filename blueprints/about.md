# Summary

User can select from existing Blueprints or generate new.
Multiple API calls process the story in stages to get Blueprint dict.
This dict is checked for proper structure with Pydance (reprompted and recorded if failed. Limit to 3 re-tries)
When treatment passes save to DB return Blueprint ID

# Views

generate_blueprint(story_id)
return Blueprint ID

# Functions

story treatment (script logic + generation) -> steps (multiple api calls)
format_check -> pydance model checks + remprompt logic
save to DB -> parse the dict create Objs

# Models

Blueprints
Characters
Backgrounds
Scenes
Dialouge
