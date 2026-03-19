from django.core.management.base import BaseCommand
from main.models import Category, Product
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Seed database with sample categories, products and users'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Create categories for home goods
        categories_data = [
            'Dụng cụ nấu ăn',
            'Bát đĩa',
            'Đồ uống',
            'Lưu trữ',
            'Thiết bị điện'
        ]
        
        categories = {}
        for cat_name in categories_data:
            cat, created = Category.objects.get_or_create(name=cat_name)
            categories[cat_name] = cat
            if created:
                self.stdout.write(f'Created category: {cat_name}')

        # Create products (home goods store items)
        products_data = [
            # Cooking tools
            ('Máy Pha Cà Phê Espresso', 2500000, 8, 'Dụng cụ nấu ăn'),
            ('Bộ Dụng Cụ Nhà Bếp Cao Cấp', 450000, 12, 'Dụng cụ nấu ăn'),
            ('Nồi Cơm Điện Cao Cấp', 1200000, 10, 'Dụng cụ nấu ăn'),
            ('Máy Xay Sinh Tố', 800000, 15, 'Dụng cụ nấu ăn'),
            ('Bộ Dao Nhà Bếp Chuyên Nghiệp', 550000, 9, 'Dụng cụ nấu ăn'),
            
            # Dishes and Plates
            ('Bộ Nồi Inox 5 Món', 1200000, 7, 'Bát đĩa'),
            ('Bộ Chén Đĩa Síc Cao Cấp', 890000, 11, 'Bát đĩa'),
            ('Bộ Dụng Cụ Nấu Không Dính', 950000, 8, 'Bát đĩa'),
            ('Chén Ăn Cơm Gốm Sứ Cao Cấp', 150000, 20, 'Bát đĩa'),
            ('Bộ Ly Thủy Tinh Cao Cấp', 320000, 14, 'Bát đĩa'),
            
            # Drinks related
            ('Bình Nước Giữ Nhiệt Cao Cấp', 350000, 18, 'Đồ uống'),
            ('Máy Pha Trà Tự Động', 650000, 6, 'Đồ uống'),
            ('Bộ Cốc Uống Nước Gốm Sứ', 280000, 16, 'Đồ uống'),
            ('Nước Ấm Điện Tử Thông Minh', 420000, 10, 'Đồ uống'),
            
            # Storage
            ('Hộp Đựng Thực Phẩm 10 Món', 350000, 12, 'Lưu trữ'),
            ('Máy Xay Sinh Tố Đa Năng', 950000, 7, 'Lưu trữ'),
            ('Tủ Bếp Thông Minh Cao Cấp', 5200000, 3, 'Lưu trữ'),
            ('Kệ Tường Bếp Chắc Chắn', 750000, 9, 'Lưu trữ'),
            
            # Electrical appliances
            ('Bộ Đồ Dùng Nhà Bếp Thông Minh', 680000, 8, 'Thiết bị điện'),
            ('Quạt Cây Cao Cấp', 480000, 10, 'Thiết bị điện'),
            ('Máy Sấy Tóc Chuyên Nghiệp', 680000, 11, 'Thiết bị điện'),
            ('Lò Vi Sóng Hiện Đại', 3200000, 5, 'Thiết bị điện'),
            ('Bàn Ủi Hơi Nước Tự Động', 890000, 7, 'Thiết bị điện'),
        ]

        for product_name, price, stock, category_name in products_data:
            product, created = Product.objects.update_or_create(
                name=product_name,
                defaults={
                    'price': price,
                    'stock': stock,
                    'category': categories[category_name],
                }
            )
            if created:
                self.stdout.write(f'Created product: {product_name}')
            else:
                self.stdout.write(f'Updated product: {product_name}')

        # Create admin and test users
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user('testuser', 'test@example.com', 'test123')
            self.stdout.write(self.style.SUCCESS('Created test user'))

        self.stdout.write(self.style.SUCCESS('Seeding complete!'))

