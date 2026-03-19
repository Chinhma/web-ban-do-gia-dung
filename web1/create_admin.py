import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web1.settings')
django.setup()

from django.contrib.auth.models import User

# Check if admin exists
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_user('admin', 'admin@homestore.com', 'admin123')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print("✓ Admin user created: username=admin, password=admin123")
else:
    print("✓ Admin user already exists")

# List all users
print("\n--- All Users ---")
for user in User.objects.all():
    print(f"  {user.username} - is_staff={user.is_staff}")
