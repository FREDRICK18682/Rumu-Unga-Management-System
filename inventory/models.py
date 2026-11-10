from django.db import models

# Create your models here.
# to create the table for the unga bales
class UngaBale(models.Model):
    number_of_bales = models.IntegerField(help_text="Total count of bales")
    packets_kg = models.CharField(max_length=100,
                                  help_text="eg, 2kg, 1kg 5kg")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.number_of_bales} bales ({self.packets_kg})"

# to create the table for the company owned machines
class CompanyMachinery(models.Model):
    STATUS_CHOICES = (
        ('Operational', 'Operational'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Damaged', 'Damaged'),
    )
    machinery_name = models.CharField(max_length=350)
    status = models.CharField(max_length=100,
                              choices=STATUS_CHOICES,
                              default="Operational")
    def __srt__(self):
        return f"{self.machinery_name} - {self.status}"