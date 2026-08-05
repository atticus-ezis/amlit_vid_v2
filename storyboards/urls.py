from django.urls import path
from . import views

urlpatterns = [
 path("accept/<int:pk>/", views.accept_image, name="accept_image"),
 path("rejected/<int:pk>/", views.reject_image, name="reject_image"),
 path("rejected-note/<int:pk>/", views.reject_description, name="reject_description"),
 path("regen-image/<int:pk>/", views.regen_image, name="regen_image")
]
