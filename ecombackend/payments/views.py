import json
import hmac, hashlib, json
from django.http import JsonResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .razorpay_client import razorpay_client
from .models import Order, OrderItem
from .serializers import OrderSerializer
import uuid
import random
from datetime import datetime

def generate_amazon_order_id():
    uid = uuid.uuid4().hex.upper()[0:12]
    return f"AMZ-{uid}"

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        data = request.data
        items = data.get("items", [])

        user = request.user  # <-- VERIFIED USER HERE
        print("LOGGED-IN USER:", user, "ID:", user.id)

        if not items:
            return Response({"error": "No items selected"}, status=400)

        # Calculate subtotal
        subtotal = sum(float(item["price"]) * int(item["quantity"]) for item in items)

        if subtotal <= 0:
            return Response({"error": "Invalid amount"}, status=400)

        cgst = subtotal * 0.09
        sgst = subtotal * 0.09
        shipping = 99  # example shipping

        total_amount = subtotal + cgst + sgst + shipping
        amount_paise = int(total_amount * 100)

        # Razorpay order creation
        razorpay_order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1,
        })

        # Save order with Authenticated user
        order = Order.objects.create(
            user=user,
            razorpay_order_id=razorpay_order["id"],
            total_amount=amount_paise,
            currency="INR",
            status="created",
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item["product_id"],
                name=item["name"],
                price=item["price"],
                quantity=item["quantity"]
            )

        return Response({
            "order_id": razorpay_order["id"],
            "amount": amount_paise,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@csrf_exempt
def verify_payment(request):
    data = json.loads(request.body)

    rp_order_id = data["razorpay_order_id"]
    rp_payment_id = data["razorpay_payment_id"]
    rp_signature = data["razorpay_signature"]

    body = f"{rp_order_id}|{rp_payment_id}".encode()
    expected_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if expected_signature == rp_signature:
        Order.objects.filter(razorpay_order_id=rp_order_id).update(status="paid")
        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "failed"}, status=400)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def orders(request):
    user = request.user.id  # authenticated user
    orders = Order.objects.filter(user=user).order_by("-created_at")

    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)
