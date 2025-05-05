from hads.urls import Path
from .views import index, explorer, create, edit

urlpatterns = [
  Path("{username}", index, name="index"),
  Path("{username}/explorer", explorer, name="explorer"),
  Path("{username}/create", create, name="create"),
  # Path("{username}/detail/{kid}", create, name="create"),
  Path("{username}/edit/{kid}", edit, name="edit")
  # Path("{username}/delete/{kid}", delete, name="create"),
]
