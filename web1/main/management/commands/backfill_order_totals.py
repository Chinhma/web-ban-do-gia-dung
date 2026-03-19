from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import Order, OrderItem


class Command(BaseCommand):
    help = 'Backfill order.total for completed orders when total is 0 or null by summing OrderItem prices.'

    def handle(self, *args, **options):
        qs = Order.objects.filter(status=Order.COMPLETED).order_by('id')
        total_updated = 0
        total_sum = 0
        self.stdout.write(f'Found {qs.count()} completed orders')
        for order in qs:
            try:
                if not order.total:
                    items = OrderItem.objects.filter(order=order)
                    computed = sum((it.price or 0) * (it.quantity or 0) for it in items)
                    with transaction.atomic():
                        order.total = computed
                        order.save(update_fields=['total'])
                    total_updated += 1
                    total_sum += computed
                    self.stdout.write(self.style.SUCCESS(f'Order {order.id} updated total={computed}'))
                else:
                    self.stdout.write(f'Order {order.id} already has total={order.total}')
            except Exception as e:
                self.stderr.write(f'Failed to update order {order.id}: {e}')

        self.stdout.write(self.style.SUCCESS(f'Updated {total_updated} orders, added sum {total_sum}'))
