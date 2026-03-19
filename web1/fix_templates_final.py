#!/usr/bin/env python3
# Fix Django templates - create clean version

home_content = """{% extends 'main/layout.html' %}
{% block content %}
<section style="margin: 40px 0">
  <h2 style="font-size: 24px; margin-bottom: 20px; color: #333">Sản phẩm nổi bật</h2>
  <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px">
  {% for product in featured %}
    {% include 'main/_product_card.html' with product=product badge_text="Nổi bật" badge_class="badge-hot" %}
  {% empty %}
    <p>Không có sản phẩm nổi bật</p>
  {% endfor %}
  </div>
</section>
<section style="margin: 40px 0">
  <h2 style="font-size: 24px; margin-bottom: 20px; color: #333">Sản phẩm mới</h2>
  <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px">
  {% for product in newest %}
    {% include 'main/_product_card.html' with product=product badge_text="Mới" badge_class="badge-new" %}
  {% empty %}
    <p>Không có sản phẩm mới</p>
  {% endfor %}
  </div>
</section>
<section style="margin: 40px 0">
  <h2 style="font-size: 24px; margin-bottom: 20px; color: #333">Tất cả sản phẩm</h2>
  <div style="display: flex; flex-wrap: wrap; gap: 10px">
  {% for product in products %}
    {% include 'main/_product_card.html' with product=product %}
  {% empty %}
    <p>Không có sản phẩm nào</p>
  {% endfor %}
  </div>
</section>
{% endblock %}"""

product_card = """{% if product.image %}<img src="{{ product.image.url }}" alt="{{ product.name }}" style="width: 100%; height: 150px; object-fit: cover">{% else %}<div style="width: 100%; height: 150px; background: #f0f0f0; display: flex; align-items: center; justify-content: center"><i class="fa-solid fa-image" style="color: #ccc"></i></div>{% endif %}<h4 style="margin: 8px 0">{{ product.name }}</h4><p style="color: #ff4444; font-weight: bold">{{ product.price }}đ</p><a href="{% url 'main:add_to_cart' product.id %}" style="background: #1890ff; color: white; padding: 6px; border-radius: 4px; text-decoration: none; display: inline-block">Thêm</a>"""

with open('main/templates/main/home.html', 'w', encoding='utf-8') as f:
    f.write(home_content)

with open('main/templates/main/_product_card.html', 'w', encoding='utf-8') as f:
    simple = '<div style="border: 1px solid #ddd; padding: 10px; width: 200px; display: inline-block; margin: 5px; background: white; border-radius: 8px">'
    simple += product_card
    simple += '</div>'
    f.write(simple)

print("✅ Templates fixed!")
