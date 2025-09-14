from wambda.urls import Path
from .views import submit, inquire

urlpatterns = [
  Path("submit", submit, name="submit"),
  Path("inquire/{aid}", inquire, name="inquire")
]
