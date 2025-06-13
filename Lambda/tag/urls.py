from hads.urls import Path
from .views import index, create, edit

urlpatterns = [
  Path("{username}", index, name="index"),
  Path("{username}/create", create, name="create"),
  Path("{username}/edit/{tag_name}", edit, name="edit"),
]
