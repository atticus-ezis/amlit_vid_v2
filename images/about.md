# Summary

This is for operations shared by Design Sheets and Scenes...
Includes Image Generation, Write to Path, Save to DB
and shared accept / reject logic (reprompt + upload)

# Views

image_review(accepted: Boolean, score: int, review_note: str)
regenerate_image(old_image: Images, new_prompt: str)
user_upload_image(old_image: Images, uploaded_image: ImageFile)

# Functions (for export)

generate_image # return data and pop b64
save_image_locally(name: str, image_typ: MultipleChoice, image_b64: str) [

make unique path, open and write image_b64, return Path
add relative path to 'data' dict ]
save_to_db # just use \*\*data in the specific view

# Template

<form method="POST" action="{% url 'review_image' image.id %}">
    {% csrf_token %}
    
    <label>
        <input type="radio" name="accepted" value="true"> Accept
    </label>
    <label>
        <input type="radio" name="accepted" value="false"> Reject
    </label>

    <button type="submit">Submit</button>

</form>

<!-- hidden until reject is selected -->
<div id="reprompt-form" style="display:none">
    <form method="POST" action="{% url 'reprompt_image' image.id %}">
        {% csrf_token %}
        <textarea name="notes" placeholder="What needs to change?"></textarea>
        <button type="submit">Re-prompt</button>
    </form>
</div>

<script>
    document.querySelectorAll('input[name="accepted"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('reprompt-form').style.display =
                e.target.value === 'false' ? 'block' : 'none';
        });
    });
</script>
