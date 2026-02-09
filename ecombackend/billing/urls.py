from django.urls import path
from .views import BillingDetailListCreateView


urlpatterns = [
    path("billing/", BillingDetailListCreateView.as_view(), name="billing")
]
