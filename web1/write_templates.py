#!/usr/bin/env python
# Write clean templates

home_html = """{% extends 'main/layout.html' %}
{% block content %}

<section style="margin: 40px 0"><h2 style="font-size: 24px; margin-bottom: 20px; color: #333">Sản phẩm nổi bật</h2><div style="display: flex; flex-wrap: wrap; gap: 10px">{% for p in featured %}{% include 'main/_product_card.html' with product=p badge_text='Nổi bật' badge_class='badge-hot' %}{% empty %}<p>Không có sản phẩm</p>{% endfor %}</div></section>

<section style="margin: 40px 0"><h2 style="font-size: 24px; margin-bottom: 20px; color: #333">Sản phẩm mới</h2><div style="display: flex; flex-wrap: wrap; gap: 10px">{% for p in newest %}{% include 'main/_product_card.html' with product=p badge_text='Mới' badge_class='badge-new' %}{% empty %}<p>Không có sản phẩm</p>{% endfor %}</div></section>

<section style="margin: 40px 0"><h2 style="font-size: 24px; margin-bottom: 20px; color: #333">Tất cả sản phẩm</h2><div style="display: flex; flex-wrap: wrap; gap: 10px">{% for p in products %}{% include 'main/_product_card.html' with product=p %}{% empty %}<p>Không có sản phẩm</p>{% endfor %}</div></section>

{% endblock %}"""

card_html = """<div style="border: 1px solid #ddd; padding: 10px; width: 180px; display: inline-block; margin: 5px; background: white; border-radius: 8px"><div style="text-align: center; height: 130px; overflow: hidden; margin-bottom: 8px">{% if product.image %}<img src="{{ product.image.url }}" alt="{{ product.name }}" style="width: 100%; height: 100%; object-fit: cover">{% else %}<div style="width: 100%; height: 100%; background: #f0f0f0; display: flex; align-items: center; justify-content: center"><i class="fa-solid fa-image" style="color: #ccc; font-size: 32px"></i></div>{% endif %}</div>{% if badge_text %}<span style="background: {% if badge_class == 'badge-hot' %}#ff4444{% else %}#52c41a{% endif %}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px">{{ badge_text }}</span>{% endif %}<h4 style="margin: 8px 0; font-size: 13px; height: 32px; overflow: hidden"><a href="{% url 'main:product_detail' product.id %}" style="text-decoration: none; color: #333">{{ product.name }}</a></h4><p style="color: #ff4444; font-weight: bold; margin: 5px 0">{{ product.price }}đ</p><a href="{% url 'main:add_to_cart' product.id %}" style="background: #1890ff; color: white; padding: 6px; border-radius: 4px; text-decoration: none; display: inline-block; width: calc(100% - 12px); text-align: center; font-size: 12px"><i class="fa-solid fa-cart-plus"></i></a></div>"""

with open('main/templates/main/home.html', 'w', encoding='utf-8') as f:
    f.write(home_html)

with open('main/templates/main/_product_card.html', 'w', encoding='utf-8') as f:
    f.write(card_html)

print("✅ Templates written successfully!")
