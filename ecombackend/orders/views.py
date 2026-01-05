from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # force JWT auth

    def perform_create(self, serializer):
        # automatically attach the logged in user
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = self.perform_create(serializer)
        return Response(
            {"message": "Order placed successfully", "order_id": serializer.instance.order_id},
            status=status.HTTP_201_CREATED,
        )
