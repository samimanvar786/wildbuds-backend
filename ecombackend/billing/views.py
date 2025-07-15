from rest_framework import generics
from .models import BillingDetail
from .serializers import BillingDetailSerializer

class BillingDetailListCreateView(generics.ListCreateAPIView):
    queryset = BillingDetail.objects.all()
    serializer_class = BillingDetailSerializer