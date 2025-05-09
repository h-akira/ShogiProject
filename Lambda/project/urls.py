from hads.urls import Path, Router
from .views import home

urlpatterns = [
  # Path("AAA/MMM/NNN", "AAAFunction", name="AAA"),
  # Path("", index, name="home"),
  # Path("home", index, name="home2"),
  # Path("sample/{parameter}", sample, name="sample"),
  # Path("logout", logout, name="logout"),
  Path("", home, name="home"),
  Router("accounts", "accounts.urls", name="accounts"),
  Router("analysis", "analysis.urls", name="analysis"),
  Router("tag", "tag.urls", name="tag"),
  Router("", "kifu.urls", name="kifu")
]
