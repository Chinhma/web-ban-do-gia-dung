#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web1.settings')
django.setup()

from django.template.loader import render_to_string
from main.models import Product
import re

products = Product.objects.all()[:3]
context = {'featured': products, 'newest': products, 'products': products}

output = render_to_string('main/home.html', context)

# Check for image URLs
img_tags = re.findall(r'<img[^>]+src="([^"]+)"', output)
print(f'Found {len(img_tags)} img tags')
if img_tags:
    print('\nImage URLs:')
    for url in img_tags[:3]:
        print(f'  - {url}')

# Check for product info
print('\n\nProduct Details:')
for p in products[:1]:
    print(f'Product: {p.name}')
    print(f'  Price: {p.price}đ')
    print(f'  Image field: {p.image}')
    if p.image:
        print(f'  Image.url: {p.image.url}')

# Check if featured products are being included
if 'featured' in output or 'Nổi bật' in output:
    print('\n✓ Featured section rendered')
else:
    print('\n✗ Featured section NOT found')

# Check if template tag errors appear
if 'TemplateDoesNotExist' in output or 'VariableDoesNotExist' in output:
    print('\n⚠ Template errors found')
else:
    print('\n✓ No template errors')
