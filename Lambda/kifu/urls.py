from hads.urls import Path
from .views import index, explorer

urlpatterns = [
  Path("{username}", index, name="index"),
  Path("{username}/explorer", exploler, name="exploler"),
]
