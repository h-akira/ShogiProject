from hads.urls import Path
from .views import index

urlpatterns = [
  Path("{username}", index, name="index")
]
