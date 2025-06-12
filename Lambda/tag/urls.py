from hads.urls import Path
from .views import index, create

urlpatterns = [
  Path("{username}", index, name="index"),
  Path("{username}/create", create, name="create"),
]
