import razorpay
from django.conf import settings

print(settings.RAZORPAY_KEY_ID)
print(settings.RAZORPAY_KEY_SECRET)
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)
