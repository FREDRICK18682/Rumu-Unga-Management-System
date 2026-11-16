
from django.db import models
from django.utils import timezone

# Create your models here.
class PaidBalesRecords(models.Model):
    unga_bale_size = models.CharField(
        max_length = 50,
        help_text= "eg, Unga Bale (12 X 2kg), Unga Bale (24 X 1kg)"
    )
    number_of_bales = models.PositiveIntegerField(
        help_text="Number of bales soled"
    )
    money_collected = models.DecimalField(max_digits=12, decimal_places=2, 
                                          help_text="Total Money collected from the sales")
    payment_method = models.CharField(max_length=100,
                                      help_text="payment method used to pay")
    date_bought = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.number_of_bales} bales sold"
            f"(cost:{self.money_collected})"
        )
        
class RecordsOfUnpaidBales(models.Model):
    unga_bale_size = models.CharField(
        max_length=50,
        help_text = "eg, Unga Bale (12 X 2kg), Unga Bale (24 X 1kg)"
    )
    number_of_bales = models.PositiveIntegerField(help_text="Number of Unpaid Bales")
    total_value = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total value of unpaid money")
    date_bought = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return (
            f"{self.number_of_bales} bales unpaid"
            f"(cost{self.total_value})"
        )
