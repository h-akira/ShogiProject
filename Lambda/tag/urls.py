from wambda.urls import Path
from .views import index, create, edit, delete, detail

urlpatterns = [
  Path("{username}", index, name="index"),
  Path("{username}/create", create, name="create"),
  Path("{username}/edit/{tid}", edit, name="edit"),
  Path("{username}/delete/{tid}", delete, name="delete"),
  Path("{username}/detail/{tid}", detail, name="detail"),
]
