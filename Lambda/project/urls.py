from hads.urls import Path, Router
from .views import index, sample, logout

urlpatterns = [
  # Path("AAA/MMM/NNN", "AAAFunction", name="AAA"),
  Path("", index, name="home"),
  Path("home", index, name="home2"),
  Path("sample/{parameter}", sample, name="sample"),
  Path("logout", logout, name="logout"),
  Router("example", "example.urls", name="example")
]
