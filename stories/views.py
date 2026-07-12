from django.shortcuts import render, redirect, get_object_or_404
from .forms import StoryForm
from projects.models import Project

# Create your views here.


def story_view(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == "POST":
        form = StoryForm(request.POST)
        if form.is_valid():
            story = form.save(commit=False)
            story.project = project
            story.save()
            return redirect("blueprint", story_pk=story.pk)

    else:
        form = StoryForm()
    return render(request, "story.html", {"form": form, "project": project})
