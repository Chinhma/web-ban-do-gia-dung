from django.core.management.base import BaseCommand
from main.models import Category, Product
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Seed database with sample categories, products and users'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # create categories
        cat_names = ['Gia dụng', 'Điện tử', 'Nhà bếp']
        cats = []
        for name in cat_names:
            c, _ = Category.objects.get_or_create(name=name)
            cats.append(c)

        # create products
        sample = [
            ('Nồi cơm điện', 1200000, 10, cats[2]),
            ('Máy xay sinh tố', 800000, 8, cats[2]),
            ('Quạt cây', 450000, 15, cats[0]),
            ('Bộ nồi inox', 2000000, 5, cats[0]),
            ('Tivi 43 inch', 7000000, 3, cats[1]),
        ]
        for name, price, stock, cat in sample:
            Product.objects.update_or_create(name=name, defaults={'price': price, 'stock': stock, 'category': cat})

        # create users
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
        if not User.objects.filter(username='user').exists():
            User.objects.create_user('user', 'user@example.com', 'userpass')

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
