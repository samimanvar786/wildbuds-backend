# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, UserDetailView, AddressViewSet

router = DefaultRouter()
router.register(r"addresses", AddressViewSet, basename="addresses")

urlpatterns = [
    # auth endpoints
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
    # user detail/update for the logged-in user
    path("me/", UserDetailView.as_view(), name="user-detail"),
    # billing address endpoints (list/create/retrieve/update/delete)
   
    path("", include(router.urls)),
]
