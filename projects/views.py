from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProjectForm
from .models import Project


def project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            # redirect to story
            return redirect("add-story", project_pk=project.pk)
    else:
        form = ProjectForm()
    existing_projects = Project.objects.all().order_by('created_at')
    return render(request, "home.html", {"form": form, "existing_projects": existing_projects})


def project_detail(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    return render(request, "project_detail.html", {"project": project})

