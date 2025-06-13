from hads.urls import Path
from .views import index, create, edit, delete

urlpatterns = [
  Path("{username}", index, name="index"),
  Path("{username}/create", create, name="create"),
  Path("{username}/edit/{tid}", edit, name="edit"),
  Path("{username}/delete/{tid}", delete, name="delete"),
]
