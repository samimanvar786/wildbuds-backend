from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class BillingDetail(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='billing_details')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=150, blank=True)
    address = models.CharField(max_length=255)
    house_number_street_name = models.CharField(max_length=255)
    town_city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postcode_zip = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20)
    email_address = models.EmailField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'