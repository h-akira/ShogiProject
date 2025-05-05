from hads.urls import Path
from .views import index, explorer, create, edit

urlpatterns = [
  Path("index/{username}", index, name="index"),
  Path("explorer/{username}", explorer, name="explorer"),
  Path("create/{username}", create, name="create"),
  # Path("{username}/detail/{kid}", create, name="create"),
  Path("edit/{username}/{kid}", edit, name="edit")
  # Path("{username}/delete/{kid}", delete, name="create"),
]
