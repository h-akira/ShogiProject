from wambda.urls import Path
from .views import index, explorer, create, edit, detail, delete, share

urlpatterns = [
  Path("index/{username}", index, name="index"),
  Path("explorer/{username}", explorer, name="explorer"),
  Path("explorer/{username}/{slug_base64}", explorer, name="explorer_with_slug_base64"),
  Path("create/{username}", create, name="create"),
  Path("detail/{username}/{kid}", detail, name="detail"),
  Path("edit/{username}/{kid}", edit, name="edit"),
  Path("delete/{username}/{kid}", delete, name="delete"),
  Path("share/{share_code}", share, name="share")
]
