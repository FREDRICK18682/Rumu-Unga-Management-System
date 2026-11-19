from django.db import transaction
from .models import UngaBale


def get_available_bales():
    inventory = UngaBale.objects.first()
    return inventory.number_of_bales if inventory else 0


# The Function to handle reducing of bales stock when bales are sold
def reduce_stock(bales_count):
    try:
        bales_to_reduce = int(bales_count)
        if bales_to_reduce <= 0:
            return False

        with transaction.atomic():
            inventory = UngaBale.objects.select_for_update().first()
            if not inventory or inventory.number_of_bales < bales_to_reduce:
                return False

            inventory.number_of_bales -= bales_to_reduce
            inventory.save(update_fields=["number_of_bales"])
            return True
    except Exception as e:
        print(f"Error reducing bale stock: {e}")
        return False