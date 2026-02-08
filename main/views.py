from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product, Category
from .models import CartItem, Order, OrderItem
from django.db import transaction, models
from django.contrib import messages
from django.shortcuts import render
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

# ---------- CHECK ADMIN ----------
def is_admin(user):
    return user.is_staff

# ---------- HOME ----------
def home(request):
    q = request.GET.get('q', '').strip()
    products = Product.objects.all()
    if q:
        products = products.filter(name__icontains=q)

    # sections for homepage: featured (first 4), newest (last 4), all products
    featured = products[:4]
    newest = products.order_by('-id')[:4]
    all_products = products

    return render(request, "main/home.html", {
        'products': all_products,
        'featured': featured,
        'newest': newest,
        'q': q,
    })


# ---------- PRODUCT DETAIL ----------
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'main/product_detail.html', {'product': product})

# ---------- DASHBOARD (ADMIN ONLY) ----------
@user_passes_test(is_admin)
def dashboard(request):
    products = Product.objects.all()
    return render(request, "main/dashboard.html", {"products": products})

# ---------- ADD PRODUCT ----------
@user_passes_test(is_admin)
def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        try:
            price = int(request.POST.get("price", 0))
        except ValueError:
            price = 0
        try:
            stock = int(request.POST.get("stock", 0))
        except ValueError:
            stock = 0
        category_id = request.POST.get("category")
        category = None
        if category_id:
            category = get_object_or_404(Category, pk=category_id)
        image = request.FILES.get('image')
        # validate image type
        if image:
            valid_mimes = ['image/jpeg', 'image/png']
            if getattr(image, 'content_type', None) not in valid_mimes:
                messages.error(request, 'Chỉ cho phép ảnh JPG hoặc PNG')
                return redirect('main:add_product')
        Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            category=category,
            image=image,
        )
        messages.success(request, "Sản phẩm đã được thêm.")
        return redirect("main:dashboard")

    categories = Category.objects.all()
    return render(request, "main/add_product.html", {"categories": categories})


# ---------- EDIT PRODUCT (ADMIN) ----------
@user_passes_test(is_admin)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.name = request.POST.get("name", product.name)
        product.price = int(request.POST.get("price", product.price))
        try:
            product.stock = int(request.POST.get("stock", product.stock))
        except ValueError:
            product.stock = product.stock
        category_id = request.POST.get('category')
        if category_id:
            product.category = get_object_or_404(Category, pk=category_id)
        img = request.FILES.get('image')
        if img:
            valid_mimes = ['image/jpeg', 'image/png']
            if getattr(img, 'content_type', None) not in valid_mimes:
                messages.error(request, 'Chỉ cho phép ảnh JPG hoặc PNG')
                return redirect('main:edit_product', pk=pk)
            product.image = img
        product.save()
        return redirect("main:dashboard")
    categories = Category.objects.all()
    return render(request, "main/edit_product.html", {"product": product, 'categories': categories})


# ---------- CART ----------
@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    qty = int(request.POST.get("quantity", 1)) if request.method == 'POST' else 1
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += qty
    else:
        cart_item.quantity = qty
    cart_item.save()
    messages.success(request, "Đã thêm vào giỏ hàng")
    return redirect("main:cart")


@login_required
def cart_view(request):
    items_qs = CartItem.objects.filter(user=request.user).select_related('product')
    items = []
    total = 0
    for item in items_qs:
        subtotal = item.product.price * item.quantity
        total += subtotal
        items.append({"item": item, "subtotal": subtotal})
    return render(request, "main/cart.html", {"items": items, "total": total})


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    item.delete()
    messages.info(request, "Đã xóa khỏi giỏ hàng")
    return redirect("main:cart")


@login_required
def update_cart_quantity(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    try:
        qty = int(request.POST.get('quantity', request.POST.get('qty', item.quantity)))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid quantity'}, status=400)
    if qty <= 0:
        item.delete()
        # recompute total
        items = CartItem.objects.filter(user=request.user).select_related('product')
        total = sum(i.product.price * i.quantity for i in items)
        return JsonResponse({'deleted': True, 'total': total})
    item.quantity = qty
    item.save()
    # compute subtotal and total
    items = CartItem.objects.filter(user=request.user).select_related('product')
    subtotal = item.product.price * item.quantity
    total = sum(i.product.price * i.quantity for i in items)
    return JsonResponse({'deleted': False, 'subtotal': subtotal, 'total': total})


# ---------- CHECKOUT ----------
@login_required
def checkout(request):
    items = CartItem.objects.filter(user=request.user).select_related('product')
    if not items.exists():
        messages.error(request, "Giỏ hàng rỗng")
        return redirect("main:cart")

    # GET -> show checkout form; POST -> process order with provided shipping info
    if request.method == 'GET':
        total = sum(it.product.price * it.quantity for it in items)
        return render(request, 'main/checkout.html', {'items': [{'item': it, 'subtotal': it.product.price * it.quantity} for it in items], 'total': total})

    # POST -> read shipping info then create order
    full_name = request.POST.get('full_name')
    address = request.POST.get('address')
    phone = request.POST.get('phone')
    note = request.POST.get('note', '')
    if not (full_name and address and phone):
        messages.error(request, 'Vui lòng nhập thông tin giao hàng')
        return redirect('main:checkout')

    with transaction.atomic():
        total = 0
        # lock involved product rows to avoid race conditions and verify stock
        product_ids = [it.product_id for it in items]
        locked_products = {p.id: p for p in Product.objects.select_for_update().filter(pk__in=product_ids)}
        # check availability and prepare adjustments if needed
        adjustments = {}  # product_id -> adjusted_qty (when stock < requested but >0)
        for it in items:
            p = locked_products.get(it.product_id)
            if p is None:
                messages.error(request, f"Sản phẩm không tồn tại: {it.product_id}")
                logger.error("Checkout failed: missing product id=%s user=%s", it.product_id, request.user.id)
                return redirect('main:cart')
            if p.stock is not None and p.stock < it.quantity:
                logger.warning("Checkout stock insufficient: user=%s product=%s requested=%s stock=%s",
                               request.user.id, p.id, it.quantity, p.stock)
                if p.stock > 0:
                    adjustments[it.product_id] = p.stock
                else:
                    messages.error(request, f"Sản phẩm {p.name} đã hết hàng")
                    return redirect('main:cart')

        # create pending order and reserve stock immediately
        order = Order.objects.create(
            user=request.user,
            status='pending',
            recipient_name=full_name,
            address=address,
            phone=phone,
            note=note,
        )
        adjusted_messages = []
        for it in items:
            p = locked_products[it.product_id]
            qty_to_use = adjustments.get(it.product_id, it.quantity)
            if qty_to_use != it.quantity:
                adjusted_messages.append(f"{p.name}: yêu cầu {it.quantity} -> đặt {qty_to_use}")
            # decrement stock to reserve for this order
            if p.stock is not None:
                p.stock = max(0, p.stock - qty_to_use)
                p.save()
            OrderItem.objects.create(order=order, product=p, quantity=qty_to_use, price=p.price)
            total += p.price * qty_to_use
        order.total = total
        order.save()
        # clear cart
        items.delete()
        if adjusted_messages:
            messages.warning(request, 'Một số sản phẩm được điều chỉnh số lượng: ' + '; '.join(adjusted_messages))

    messages.success(request, "Thanh toán thành công. Đơn hàng đã được tạo.")
    return redirect("main:orders")


# ---------- BUY NOW (one-step purchase flow) ----------
@login_required
def buy_now(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method != 'POST':
        return redirect('main:home')
    try:
        qty = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        qty = 1
    request.session['buy_now'] = {'product_id': product.id, 'quantity': qty}
    return redirect('main:checkout_now')


@login_required
def checkout_now(request):
    data = request.session.get('buy_now')
    if not data:
        messages.error(request, "Không có sản phẩm để mua ngay")
        return redirect('main:home')
    product = get_object_or_404(Product, pk=data['product_id'])
    qty = int(data.get('quantity', 1))
    if request.method == 'POST':
        # simple stock check before creating a pending order
        # use row locking to prevent races and reserve stock immediately
        with transaction.atomic():
            p = Product.objects.select_for_update().get(pk=product.pk)
            if p.stock is not None and p.stock < qty:
                logger.warning("Checkout_now stock insufficient: user=%s product=%s requested=%s stock=%s session=%s",
                               request.user.id, p.id, qty, p.stock, request.session.get('buy_now'))
                if p.stock > 0:
                    adjusted_qty = p.stock
                    messages.warning(request, f"Số lượng cho sản phẩm {p.name} được điều chỉnh: {qty} -> {adjusted_qty}")
                    qty = adjusted_qty
                else:
                    messages.error(request, "Sản phẩm không đủ số lượng")
                    return redirect('main:home')
            # deduct stock to reserve for this pending order
            p.stock = max(0, p.stock - qty) if p.stock is not None else p.stock
            p.save()
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        note = request.POST.get('note', '')
        if not (full_name and address and phone):
            messages.error(request, 'Vui lòng nhập thông tin nhận hàng')
            return redirect('main:checkout_now')
        with transaction.atomic():
            order = Order.objects.create(user=request.user, status='pending', total=0, recipient_name=full_name, address=address, phone=phone, note=note)
            OrderItem.objects.create(order=order, product=p, quantity=qty, price=p.price)
            total = p.price * qty
            order.total = total
            order.save()
        # clear session
        try:
            del request.session['buy_now']
        except KeyError:
            pass
        messages.success(request, "Thanh toán thành công. Đơn hàng đã được tạo.")
        return redirect('main:orders')

    return render(request, 'main/checkout_now.html', {'product': product, 'quantity': qty})


# ---------- ORDERS ----------
@login_required
def order_list(request):
    if request.user.is_staff:
        orders = Order.objects.all().select_related('user').prefetch_related('items__product')
    else:
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, "main/orders.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if not request.user.is_staff and order.user != request.user:
        messages.error(request, "Bạn không có quyền xem đơn hàng này.")
        return redirect('main:orders')
    items_qs = order.items.select_related('product').all()
    items = []
    for it in items_qs:
        subtotal = (it.price or 0) * (it.quantity or 0)
        items.append({'item': it, 'subtotal': subtotal})
    return render(request, 'main/order_detail.html', {'order': order, 'items': items})


@user_passes_test(is_admin)
def review_order(request, pk, action):
    order = get_object_or_404(Order, pk=pk)
    if request.method != 'POST':
        messages.error(request, 'Yêu cầu phải là POST')
        return redirect('main:order_detail', pk=pk)

    if action not in ('approve', 'reject'):
        messages.error(request, 'Hành động không hợp lệ')
        return redirect('main:order_detail', pk=pk)
    if action == 'approve':
        # try reduce stock and mark approved
        with transaction.atomic():
            # check stock availability for all items
            for it in order.items.select_related('product').all():
                if it.product and it.product.stock is not None and it.product.stock < it.quantity:
                    messages.error(request, f"Sản phẩm {it.product.name} không đủ số lượng để duyệt đơn.")
                    return redirect('main:order_detail', pk=pk)
            # deduct
            for it in order.items.select_related('product').all():
                if it.product and it.product.stock is not None:
                    it.product.stock = max(0, it.product.stock - it.quantity)
                    it.product.save()
            order.status = 'approved'
            from django.utils import timezone as _tz
            order.approved_at = _tz.now()
            # optional review note
            rn = request.POST.get('review_note', '')
            if rn:
                order.review_note = rn
            order.save()
            messages.success(request, 'Đã duyệt đơn hàng')
    else:
        order.status = 'rejected'
        rn = request.POST.get('review_note', '')
        if rn:
            order.review_note = rn
        order.save()
        messages.info(request, 'Đã từ chối đơn hàng')
    return redirect('main:orders')


@user_passes_test(is_admin)
def stats(request):
    # summary
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='approved').aggregate(models.Sum('total'))['total__sum'] or 0
    # daily breakdown
    from django.db.models.functions import TruncDate
    daily = (
        Order.objects.filter(status='approved')
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=models.Count('id'), revenue=models.Sum('total'))
        .order_by('-day')
    )
    return render(request, 'main/stats.html', {'total_orders': total_orders, 'total_revenue': total_revenue, 'daily': daily})

# ---------- DELETE ----------
@user_passes_test(is_admin)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect("main:dashboard")

# ---------- AUTH ----------
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )
        if user:
            login(request, user)
            return redirect("main:home")
    return render(request, "main/login.html")

def register_view(request):
    if request.method == "POST":
        User.objects.create_user(
            username=request.POST["username"],
            password=request.POST["password"]
        )
        return redirect("main:login")
    return render(request, "main/register.html")

def logout_view(request):
    logout(request)
    return redirect("main:home")
