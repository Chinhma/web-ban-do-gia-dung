#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web1.settings')
django.setup()

from main.models import Category

# Create default categories
categories = [
    'Dụng cụ nấu ăn',
    'Bát đĩa',
    'Đồ uống',
    'Lưu trữ',
    'Thiết bị điện'
]

print("Creating categories...")
for cat_name in categories:
    cat, created = Category.objects.get_or_create(name=cat_name)
    if created:
        print(f'✅ Created: {cat_name}')
    else:
        print(f'⚠️ Already exists: {cat_name}')

print(f'\n📊 Total categories: {Category.objects.count()}')
