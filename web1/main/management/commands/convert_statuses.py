from django.core.management.base import BaseCommand
from main.models import Order

class Command(BaseCommand):
    help = 'Convert existing English order status values to Vietnamese values used by the model'

    MAPPING = {
        'pending': Order.PENDING,
        'approved': Order.CONFIRMED,
        'shipping': Order.DELIVERING,
        'delivering': Order.DELIVERING,
        'review': Order.COMPLETED,
        'rejected': Order.CANCELLED,
    }

    def handle(self, *args, **options):
        updated = 0
        for eng, vn in self.MAPPING.items():
            qs = Order.objects.filter(status=eng)
            count = qs.update(status=vn)
            if count:
                self.stdout.write(self.style.SUCCESS(f"Converted {count} orders from '{eng}' to '{vn}'"))
                updated += count
        if not updated:
            self.stdout.write('No orders needed conversion.')
        else:
            self.stdout.write(self.style.SUCCESS(f'Total converted: {updated}'))
