from django.db import models
from django.utils import timezone

# Create your models here.
class MaizeProcurement(models.Model):
    #To track maize purchases
    number_of_bags =models.PositiveIntegerField(
        help_text="Number of bags of maize bought"
    )
    cost = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total cost for bags"
    )
    date_bought=models.DateField(default=timezone.now)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return(
            f"{self.number_of_bags} Bags of Maize bought on {self.date_bought}"
            f"(cost:{self.cost})"
        )

class PackagingProcurement(models.Model):
    # TAble to track packaging papers and bag purchases
    number_of_papers= models.PositiveIntegerField(
        help_text="Number of Packaging papers bought"
    )
    number_of_bags= models.PositiveIntegerField(
        help_text="Number of Parkaging bags bought"
    )
    cost_of_papers= models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total Cost for the papers bought"
    )
    cost_of_bags= models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total cost of bag bought"
    )
    date_bought = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.number_of_papers} Packaging item bought on"
            f"{self.date_bought} (cost: {self.cost})"
        )