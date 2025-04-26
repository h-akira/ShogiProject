from hads.urls import Path
from .views import logout

urlpatterns = [
  Path("logout", logout, name="logout")
]
