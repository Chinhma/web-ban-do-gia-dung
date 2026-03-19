from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("debug/", views.debug_view, name="debug"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("add/", views.add_product, name="add_product"),
    path("edit/<int:pk>/", views.edit_product, name="edit_product"),
    path("delete/<int:pk>/", views.delete_product, name="delete_product"),

    # cart / checkout
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/count/", views.get_cart_count, name="get_cart_count"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:pk>/", views.update_cart_quantity, name="update_cart_quantity"),
    path("checkout/", views.checkout, name="checkout"),
    path("buy_now/<int:pk>/", views.buy_now, name="buy_now"),
    path("checkout_now/", views.checkout_now, name="checkout_now"),
    path("checkout_success/", views.checkout_success, name="checkout_success"),

    # orders
    path("orders/", views.order_list, name="orders"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/<int:pk>/cancel/", views.cancel_order, name="cancel_order"),
    path("orders/<int:pk>/<str:action>/", views.review_order, name="review_order"),
    
    # admin panel
    path("admin-panel/", views.admin_panel, name="admin_panel"),
    path("admin-panel/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/products/", views.admin_products, name="admin_products"),
    path("admin-panel/product/add/", views.admin_product_add, name="admin_product_add"),
    path("admin-panel/categories/", views.admin_categories, name="admin_categories"),
    path("admin-panel/orders/", views.admin_orders, name="admin_orders"),
    path("admin-panel/order/<int:pk>/", views.admin_order_detail, name="admin_order_detail"),
    path("admin-panel/order/<int:pk>/update-status/", views.admin_update_order_status, name="admin_update_order_status"),
    path("admin-panel/customers/", views.admin_customers, name="admin_customers"),
    path("admin-panel/order/<int:pk>/<str:action>/", views.admin_review_order, name="admin_review_order"),
    
    path("stats/", views.stats, name="stats"),

    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", auth_views.PasswordResetView.as_view(
        template_name='main/forgot_password.html',
        email_template_name='main/password_reset_email.html',
        subject_template_name='main/password_reset_subject.txt',
        success_url=reverse_lazy('main:password_reset_done')
    ), name="forgot_password"),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='main/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='main/password_reset_confirm.html',
        success_url=reverse_lazy('main:password_reset_complete')
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='main/password_reset_complete.html'
    ), name='password_reset_complete'),
]
