from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("add/", views.add_product, name="add_product"),
    path("edit/<int:pk>/", views.edit_product, name="edit_product"),
    path("delete/<int:pk>/", views.delete_product, name="delete_product"),

    # cart / checkout
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:pk>/", views.update_cart_quantity, name="update_cart_quantity"),
    path("checkout/", views.checkout, name="checkout"),
    path("buy_now/<int:pk>/", views.buy_now, name="buy_now"),
    path("checkout_now/", views.checkout_now, name="checkout_now"),

    # orders
    path("orders/", views.order_list, name="orders"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/<int:pk>/<str:action>/", views.review_order, name="review_order"),
    path("stats/", views.stats, name="stats"),

    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
]
