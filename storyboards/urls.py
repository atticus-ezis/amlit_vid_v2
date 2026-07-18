from django.urls import path
from . import views

urlpatterns = [
 path("accept/<int:pk>/", views.accept_image, name="accept_image"),
]
