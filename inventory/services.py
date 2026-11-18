from .models import UngaBale

#The Function to handel reducing of bales stock when bales are sold
def reduce_stock(bales_count):
    try:
        inventory = UngaBale.objects.first()
        if inventory:
            inventory.number_of_bales -= int(bales_count)
            inventory.save()
            return True
    except Exception as e:
        print(f"Error reducing bale stock: {e}")
        return False