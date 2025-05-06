from hads.urls import Path
from .views import index, explorer, create, edit, detail, delete

urlpatterns = [
  Path("index/{username}", index, name="index"),
  Path("explorer/{username}", explorer, name="explorer"),
  Path("create/{username}", create, name="create"),
  Path("detail/{username}/{kid}", detail, name="detail"),
  Path("edit/{username}/{kid}", edit, name="edit"),
  Path("delete/{username}/{kid}", delete, name="delete")
]
