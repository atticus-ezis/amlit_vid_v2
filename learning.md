# Problem 1 - How to organize images
Detailed Problem: Each image belongs to only one 'target' specified by the blueprint. The program only needs one image for 'scene_1' and 'grandma's house' for instance. But for each 'target' there can be multiple generations. Furthermore each generation can be used to spawn multiple generations -> "image branching". 

Soltuion: This organization requires two layers. The 'target' layer that organizes all generated images. And the 'generation chain' layer that creates and traces a roadmap of every subsiquent generation all the way back to the original 'parent' image. 

To create the 'target' layer I will create a FK to a new model 'ImageStack' that will specify the blueprint object requested. This way I can group all images neatly by filtering by that FK. I can also handle batch character logic here. 

To create the 'generation chain' I need a 'parent' FK that is self referencing and uses 'children' as the related name. The parent will have 'None' for this value and all childrenn will have one parent. Because the images allow for branching (multiple children for one parent) I need a OneToMany instead of a OneToOne relationship. To get the generation chain for each image I can simply collect every 'parent' until that value is 'None' 
Example: "Send all images generations for 'forest' background" to the frontend ->


forest_background = Background(...)

forest_stack = ImageStack(background=forest_background)
forest_stack_images = Images.objects.get(image_stack=forest_stack)

