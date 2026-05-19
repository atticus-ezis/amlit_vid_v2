# Summary

After the Design Sheets have been generated and approved the Storyboards can be generated. Must be done one at a time since they are self referencing. Once one is approved the next is generated. Shows status like 0/10 in template

# Views

generate_scenes(blueprint_id) -> finds the earliest scene with no 'accepted' Image FK and constructs prompt + passes ref_images + store and save image -> return url to be displayed and completion count.
!!! Make sure the next generation isn't triggered until user updates 'status' of latest image.
