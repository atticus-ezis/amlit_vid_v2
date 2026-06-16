"""
URL configuration for amlit_video project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from projects.views import project_view, project_detail
from stories.views import story_view
from blueprints.views import blueprint_view, blueprint_detail
from storyboards.views import storyboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', project_view, name="home"),
    path('project/<int:project_pk>/', project_detail, name="project-detail"),
    path('project/<int:project_pk>/add-story', story_view, name="add-story"),
    path('story/<int:story_pk>/blueprint/', blueprint_view, name="blueprint"),
    path('blueprint/<int:blueprint_pk>/', blueprint_detail, name="blueprint-detail"),
    path('blueprint/<int:blueprint_pk>/storybaord/', storyboard_view, name="storyboard"),
]
