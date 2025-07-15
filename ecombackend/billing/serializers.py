from rest_framework import serializers
from .models import BillingDetail

class BillingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingDetail
        fields = '__all__'