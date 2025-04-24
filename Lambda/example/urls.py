from hads.urls import Path
from .views import index

urlpatterns = [
  Path("home", index, name="home")
]
