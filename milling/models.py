from django.db import models
from django.utils import timezone

# Create your models here.
class LocalMilling(models.Model):
    kgs = models.CharField(max_length=50,
                           help_text="eg, 1kgs, 5kgs, 9kgs")
    unga_grade = models.CharField(max_length=50,
                                  help_text="grade 1, grade 2")
    total_cost = models.DecimalField(max_digits=12,
                                     decimal_places=2,
                                     help_text="The cost of money collected")
    date_milled = models.DateField(default=timezone.now)

class SchoolMillRecords(models.Model):
    name_of_school = models.CharField(max_length=500,
                                      help_text="Name of the school")
    number_of_bags = models.PositiveIntegerField(help_text="The number of bags milled for the school")
    total_value = models.DecimalField(max_digits=12,
                                      decimal_places=2,
                                      help_text="the value of the money collceted")
    date_milled = models.DateField(default=timezone.now)