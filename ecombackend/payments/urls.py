from django.urls import path, include
from .views import create_order,verify_payment,orders

urlpatterns = [
    path("create-order/", create_order, name="create_order"),
    path("verify-payment/", verify_payment),
    path("orders/", orders, name="orders"),
]
