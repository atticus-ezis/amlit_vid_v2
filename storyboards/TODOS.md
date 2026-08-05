1. Handle regen logic in backend 'regen_image' pk 
2. Handle review note in backend 

"{% url 'reject_description' pk=image.pk%}"
                body: JSON.stringify({
                    review_note: content,
                })
"{% url 'regen_image' pk=image.pk %}"
                    body: JSON.stringify({
                        reprompt: reprompt,
                        reference_images: selectedReferenceImages (IDs)
                    })
