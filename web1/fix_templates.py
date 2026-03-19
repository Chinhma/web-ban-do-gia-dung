#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Fix home.html
print("Fixing home.html...")
with open('main/templates/main/home.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all instances of template tags on same line with newlines
content = content.replace(
    "    {% for product in featured %} {% include 'main/_product_card.html' with\n    product=product badge_text=\"Nổi bật\" badge_class=\"badge-hot\" %} {% empty %}",
    "    {% for product in featured %}\n      {% include 'main/_product_card.html' with product=product badge_text=\"Nổi bật\" badge_class=\"badge-hot\" %}\n    {% empty %}"
)

content = content.replace(
    "    {% for product in newest %} {% include 'main/_product_card.html' with\n    product=product badge_text=\"Mới\" badge_class=\"badge-new\" %} {% empty %}",
    "    {% for product in newest %}\n      {% include 'main/_product_card.html' with product=product badge_text=\"Mới\" badge_class=\"badge-new\" %}\n    {% empty %}"
)

content = content.replace(
    "    {% for product in products %} {% include 'main/_product_card.html' with\n    product=product %} {% empty %}",
    "    {% for product in products %}\n      {% include 'main/_product_card.html' with product=product %}\n    {% empty %}"
)

# Fix the opening line
content = content.replace(
    "{% extends 'main/layout.html' %} {% block content %}",
    "{% extends 'main/layout.html' %}\n{% block content %}"
)

with open('main/templates/main/home.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Fixed home.html")

# Fix _product_card.html
print("Fixing _product_card.html...")
with open('main/templates/main/_product_card.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the endif and if badge_text on same line
content = content.replace(
    "    {% endif %} {% if badge_text %}\n    <span class=\"product-badge {{ badge_class }}\">{{ badge_text }}</span>\n    {% endif %}",
    "    {% endif %}\n    {% if badge_text %}\n      <span class=\"product-badge {{ badge_class }}\">{{ badge_text }}</span>\n    {% endif %}"
)

with open('main/templates/main/_product_card.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ Fixed _product_card.html")

print("\n✓ All templates fixed!")
