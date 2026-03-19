from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product, Category
from .models import CartItem, Order, OrderItem
from django.db import transaction, models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.contrib import messages
from django.shortcuts import render
from django.http import JsonResponse
import logging
import threading
import time

logger = logging.getLogger(__name__)


def _map_status_key(key):
    """Map URL/query status keys (english-like) to VN status strings stored in DB."""
    mapping = {
        'pending': Order.PENDING,
        'confirmed': Order.CONFIRMED,
        'approved': Order.CONFIRMED,
        'delivering': Order.DELIVERING,
        'shipping': Order.DELIVERING,
        'completed': Order.COMPLETED,
        'cancelled': Order.CANCELLED,
        'all': 'all'
    }
    return mapping.get(key, key)


def _compute_revenue_for_status(status_values, since=None):
    """Compute total revenue for orders whose status is in status_values.

    - Tries summing the DB `total` field first.
    - If that produces None/0 while completed orders exist, falls back to summing order items (price * quantity).
    - `status_values` may be a list/tuple of strings.
    Returns (orders_qs, total_revenue)
    """
    if not isinstance(status_values, (list, tuple)):
        status_values = [status_values]

    qs = Order.objects.filter(status__in=status_values).prefetch_related('items')
    if since:
        qs = qs.filter(created_at__gte=since)

    # Debug: list completed orders
    try:
        debug_list = list(qs.values('id', 'status', 'total'))
        print('DEBUG: Orders matching status candidates:', status_values)
        print('DEBUG: Orders:', debug_list)
    except Exception:
        print('DEBUG: Failed to list orders for statuses', status_values)

    # Try sum over DB total field
    total_sum = qs.aggregate(total=Sum('total'))['total']
    if total_sum:
        print('DEBUG: revenue from total field =', total_sum)
        return qs, total_sum

    # Fallback: compute from order items (price * quantity)
    try:
        expr = ExpressionWrapper(F('items__price') * F('items__quantity'), output_field=DecimalField())
        items_sum = Order.objects.filter(status__in=status_values).aggregate(total=Sum(expr))['total']
        total_sum = items_sum or 0
        print('DEBUG: revenue computed from items =', total_sum)
        return qs, total_sum
    except Exception:
        print('DEBUG: failed to compute revenue from items for', status_values)
        return qs, 0


def schedule_order_progression(order_id):
    """Background thread to automatically progress order status every 60s.

    Sequence: Chờ xác nhận -> Đã xác nhận -> Đang giao -> Hoàn thành
    If order is cancelled at any point, stops progressing.
    """
    def _run():
        try:
            # step 1: wait 60s then confirm
            time.sleep(60)
            order = Order.objects.filter(pk=order_id).first()
            if not order or order.status == Order.CANCELLED:
                return
            if order.status == Order.PENDING:
                order.status = Order.CONFIRMED
                from django.utils import timezone as _tz
                order.approved_at = _tz.now()
                order.save()

            # step 2: wait 60s then delivering
            time.sleep(60)
            order = Order.objects.filter(pk=order_id).first()
            if not order or order.status == Order.CANCELLED:
                return
            if order.status == Order.CONFIRMED:
                order.status = Order.DELIVERING
                order.save()

            # step 3: wait 60s then complete
            time.sleep(60)
            order = Order.objects.filter(pk=order_id).first()
            if not order or order.status == Order.CANCELLED:
                return
            if order.status == Order.DELIVERING:
                order.status = Order.COMPLETED
                from django.utils import timezone as _tz
                order.completed_at = _tz.now()
                # Ensure total is set: if total is 0 or falsy, compute from order items
                try:
                    if not order.total:
                        items = OrderItem.objects.filter(order=order)
                        computed = sum((it.price or 0) * (it.quantity or 0) for it in items)
                        order.total = computed
                except Exception:
                    logger.exception("Failed to compute total for order %s", order_id)
                order.save()
        except Exception:
            logger.exception("Error in order progression thread for order %s", order_id)

    t = threading.Thread(target=_run, daemon=True)
    t.start()

# ---------- CHECK ADMIN ----------
def is_admin(user):
    return user.is_staff

# ---------- HOME ----------
def home(request):
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    products = Product.objects.all()
    
    if q:
        products = products.filter(name__icontains=q)
    
    if category_id:
        products = products.filter(category_id=category_id)

    # sections for homepage: featured (first 4), newest (last 4), all products
    featured = products[:4]
    newest = products.order_by('-id')[:4]
    all_products = products

    # DEBUG: In ra console để kiểm tra
    print("="*60)
    print("🔍 HOME VIEW DEBUG:")
    print(f"  featured count: {featured.count()}")
    print(f"  newest count: {newest.count()}")
    print(f"  all_products count: {all_products.count()}")
    
    # ✅ Sửa: dùng index [0] thay vì .first() trên queryset đã slice
    try:
        if len(featured) > 0:
            print(f"\n  Featured products: {[p.name for p in featured]}")
            print(f"  First featured image: {featured[0].image if featured[0].image else 'No image'}")
    except Exception as e:
        print(f"  Error on featured: {e}")
    
    try:
        if len(all_products) > 0:
            print(f"\n  All products: {[p.name for p in all_products[:3]]}...")
            print(f"  First product image: {all_products[0].image if all_products[0].image else 'No image'}")
        print(f"  Total in DB: {Product.objects.count()}")
    except Exception as e:
        print(f"  Error on products: {e}")
    
    print("="*60)

    return render(request, "main/home.html", {
        'products': all_products,
        'featured': featured,
        'newest': newest,
        'q': q,
        'categories': Category.objects.all(),
        'selected_category': category_id,
    })

# ---------- DEBUG VIEW ----------
def debug_view(request):
    featured = Product.objects.all()[:3]
    newest = Product.objects.all()[:3]
    products = Product.objects.all()[:3]
    
    return render(request, "main/debug.html", {
        'featured': featured,
        'newest': newest,
        'products': products,
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
        messages.success(request, 'Cập nhật sản phẩm thành công!')
        return redirect("main:admin_products")
    categories = Category.objects.all()
    return render(request, "main/admin_product_edit.html", {"product": product, 'categories': categories})


# ---------- CART ----------
def add_to_cart(request, pk):
    # For AJAX requests, check authentication and return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng đăng nhập để thêm vào giỏ hàng',
                'require_login': True
            }, status=401)
        
        product = get_object_or_404(Product, pk=pk)
        qty = int(request.POST.get("quantity", 1)) if request.method == 'POST' else 1
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += qty
        else:
            cart_item.quantity = qty
        cart_item.save()
        
        cart_count = CartItem.objects.filter(user=request.user).count()
        return JsonResponse({
            'success': True,
            'message': f'Đã thêm {product.name} vào giỏ hàng',
            'cart_count': cart_count,
            'product_name': product.name
        })
    
    # For regular requests, use login_required
    if not request.user.is_authenticated:
        return redirect('main:login')
    
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
def get_cart_count(request):
    """API endpoint to get the current cart item count"""
    if not request.user.is_authenticated:
        return JsonResponse({'cart_count': 0})
    cart_count = CartItem.objects.filter(user=request.user).count()
    return JsonResponse({'cart_count': cart_count})


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
    # For AJAX requests, check authentication and return JSON
    if request.method != 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid method'}, status=405)
        return redirect('main:cart')
    
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Vui lòng đăng nhập'}, status=401)
        return redirect('main:login')
    
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    item.delete()
    
    # For AJAX requests, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        items = CartItem.objects.filter(user=request.user).select_related('product')
        total = sum(i.product.price * i.quantity for i in items)
        cart_count = items.count()
        return JsonResponse({
            'success': True,
            'message': 'Đã xóa khỏi giỏ hàng',
            'total': total,
            'cart_count': cart_count
        })
    
    messages.info(request, "Đã xóa khỏi giỏ hàng")
    return redirect("main:cart")


@login_required
def update_cart_quantity(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Vui lòng đăng nhập'}, status=401)
        return redirect('main:login')
    
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
    payment_method = request.POST.get('payment_method', 'cod')  # 'cod' or 'online'
    member_type = request.POST.get('member_type', 'regular')  # 'regular', 'member', or 'vip'
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
            status=Order.PENDING,
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
        # schedule automatic progression (background thread)
        try:
            schedule_order_progression(order.id)
        except Exception:
            logger.exception("Failed to schedule progression for order %s", order.id)
        # clear cart
        items.delete()
        if adjusted_messages:
            messages.warning(request, 'Một số sản phẩm được điều chỉnh số lượng: ' + '; '.join(adjusted_messages))

    # Redirect based on payment method
    if payment_method == 'online':
        messages.info(request, "Vui lòng hoàn thành thanh toán online")
        return redirect("main:checkout_fail")  # For demo, or redirect to payment gateway
    else:
        # COD (Cash on Delivery)
        messages.success(request, "Thanh toán thành công. Đơn hàng sẽ được giao tới nhà bạn.")
        return redirect("main:checkout_success")


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
        # Get form data
        full_name = request.POST.get('customer_name')
        address = request.POST.get('customer_address')
        address_detail = request.POST.get('customer_address_detail', '')
        phone = request.POST.get('customer_phone')
        customer_notes = request.POST.get('customer_notes', '')
        delivery_method = request.POST.get('delivery_method', 'standard')
        payment_method = request.POST.get('payment_method', 'cod')
        
        # Validate required fields
        if not (full_name and address and phone):
            messages.error(request, 'Vui lòng nhập thông tin nhận hàng')
            return redirect('main:checkout_now')
        
        # Stock check and reservation
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
            # Deduct stock
            p.stock = max(0, p.stock - qty) if p.stock is not None else p.stock
            p.save()
        
        # Build note with all information
        note_parts = []
        if customer_notes:
            note_parts.append(f"Ghi chú: {customer_notes}")
        note_parts.append(f"Địa chỉ chi tiết: {address_detail}" if address_detail else "")
        note_parts.append(f"Hình thức giao hàng: {'Giao hàng nhanh (25.000đ)' if delivery_method == 'express' else 'Giao hàng tiêu chuẩn (Miễn phí)'}")
        note_parts.append(f"Phương thức thanh toán: {'Thanh toán trực tuyến' if payment_method == 'online' else 'Thanh toán khi nhận hàng (COD)'}")
        note = "\n".join([n for n in note_parts if n])
        
        # Calculate total with shipping fee
        subtotal = p.price * qty
        shipping_fee = 25000 if delivery_method == 'express' else 0
        total_amount = subtotal + shipping_fee
        
        # Create order
        with transaction.atomic():
            order = Order.objects.create(
                    user=request.user,
                    status=Order.PENDING,
                    total=total_amount,
                    recipient_name=full_name,
                    address=f"{address}\n{address_detail}" if address_detail else address,
                    phone=phone,
                    note=note
                )
            OrderItem.objects.create(order=order, product=p, quantity=qty, price=p.price)

        # schedule automatic progression
        try:
            schedule_order_progression(order.id)
        except Exception:
            logger.exception("Failed to schedule progression for order %s", order.id)
        
        # Clear session
        try:
            del request.session['buy_now']
        except KeyError:
            pass
        
        messages.success(request, "✓ Đặt hàng thành công! Đơn hàng đang chờ xử lý.")
        return redirect('main:checkout_success')

    subtotal = product.price * qty
    return render(request, 'main/checkout_now.html', {'product': product, 'quantity': qty, 'subtotal': subtotal})


@login_required
def checkout_success(request):
    """Display order success page"""
    from django.utils import timezone
    return render(request, 'main/checkout_success.html', {'now': timezone.now()})


# ---------- ORDERS ----------
@login_required
def order_list(request):
    # Get all orders for current user or all if staff
    if request.user.is_staff:
        orders = Order.objects.all().select_related('user').prefetch_related('items__product').order_by('-created_at')
    else:
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    
    # Handle status filtering (map query keys to VN status strings)
    status_key = request.GET.get('status', 'all')
    status_mapped = _map_status_key(status_key)
    filtered_orders = orders
    if status_mapped != 'all':
        filtered_orders = orders.filter(status=status_mapped)
    
    return render(request, "main/orders.html", {
        "orders": orders,
        "filtered_orders": filtered_orders,
        # keep the original query key so templates can highlight tabs (e.g., 'pending', 'confirmed')
        "status": status_key
    })


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


@login_required
def cancel_order(request, pk):
    """Allow users to cancel their own pending orders"""
    order = get_object_or_404(Order, pk=pk)
    
    # Check permissions - user can only cancel their own orders
    if order.user != request.user:
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền huy đơn hàng này.'}, status=403)
        messages.error(request, "Bạn không có quyền hủy đơn hàng này.")
        return redirect('main:orders')
    
    # Only allow cancelling pending orders
    if order.status != Order.PENDING:
        if request.method == 'POST':
            return JsonResponse({'success': False, 'message': 'Chỉ có thể hủy đơn hàng đang chờ xác nhận.'}, status=400)
        messages.error(request, "Chỉ có thể hủy đơn hàng đang chờ xác nhận.")
        return redirect('main:order_detail', pk=pk)
    
    if request.method == 'POST':
        # Update order status to cancelled
        order.status = Order.CANCELLED
        order.save()
        
        # Return JSON response for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Đơn hàng đã bị hủy thành công.'})
        
        messages.success(request, 'Đơn hàng đã được hủy thành công.')
        return redirect('main:orders')
    
    # GET request - show confirmation
    return redirect('main:order_detail', pk=pk)


@user_passes_test(is_admin)
def review_order(request, pk, action):
    # Admin manual approve/reject is disabled; system auto-processes orders.
    messages.error(request, 'Hệ thống tự động xử lý đơn hàng; admin không cần duyệt.')
    return redirect('main:order_detail', pk=pk)


@user_passes_test(is_admin)
def admin_panel(request):
    """Admin panel to review pending orders"""
    # Get all orders (for display)
    all_orders = Order.objects.prefetch_related('items__product').order_by('-created_at')

    # Get summary stats
    total_pending = Order.objects.filter(status=Order.PENDING).count()
    total_orders = Order.objects.count()
    # Try to compute revenue for completed orders. Support both 'Hoàn thành' and 'completed' DB values.
    status_candidates = [Order.COMPLETED, 'completed']
    _, total_revenue = _compute_revenue_for_status(status_candidates)

    return render(request, 'main/admin_panel.html', {
        'pending_orders': all_orders,
        'total_pending': total_pending,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    })


@user_passes_test(is_admin)
def admin_review_order(request, pk, action):
    """Admin approves or rejects an order"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Chỉ POST được phép'}, status=400)
    
    # Admin manual approve/reject is disabled in this flow.
    return JsonResponse({'success': False, 'message': 'Admin không thể thay đổi trạng thái. Hệ thống tự động xử lý.'}, status=400)


@user_passes_test(is_admin)
def stats(request):
    # summary
    total_orders = Order.objects.count()
    # compute revenue for completed orders (support multiple DB representations)
    status_candidates = [Order.COMPLETED, 'completed']
    orders_qs, total_revenue = _compute_revenue_for_status(status_candidates)

    # daily breakdown (group by created date) using the best-known total field
    from django.db.models.functions import TruncDate
    # If orders_qs is empty, try alternate status string
    daily_qs = orders_qs
    daily = (
        daily_qs.annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=models.Count('id'), revenue=models.Sum('total'))
        .order_by('-day')
    )
    return render(request, 'main/stats.html', {'total_orders': total_orders, 'total_revenue': total_revenue, 'daily': daily})

# ---------- DELETE ----------
@user_passes_test(is_admin)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product_name = product.name
    product.delete()
    messages.success(request, f'Sản phẩm "{product_name}" đã được xóa!')
    return redirect("main:admin_products")

# ---------- AUTH ----------
def login_view(request):
    if request.user.is_authenticated:
        return redirect("main:home")
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        
        if not username or not password:
            messages.error(request, "Vui lòng nhập tên đăng nhập và mật khẩu!")
            return render(request, "main/login.html")
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Chào mừng {user.username}!")
            return redirect("main:home")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác!")
    
    return render(request, "main/login.html")

def register_view(request):
    if request.user.is_authenticated:
        return redirect("main:home")
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()
        email = request.POST.get("email", "").strip()
        
        # Validation
        if not username or not password:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin!")
            return render(request, "main/register.html")
        
        if len(username) < 5:
            messages.error(request, "Tên đăng nhập phải có ít nhất 5 ký tự!")
            return render(request, "main/register.html")
        
        if len(password) < 6:
            messages.error(request, "Mật khẩu phải có ít nhất 6 ký tự!")
            return render(request, "main/register.html")
        
        if password != confirm_password:
            messages.error(request, "Xác nhận mật khẩu không trùng khớp!")
            return render(request, "main/register.html")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại! Vui lòng chọn tên khác.")
            return render(request, "main/register.html")
        
        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Email này đã được đăng ký!")
            return render(request, "main/register.html")
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            messages.success(request, "Đăng ký thành công! Vui lòng đăng nhập.")
            return redirect("main:login")
        except Exception as e:
            messages.error(request, f"Lỗi đăng ký: {str(e)}")
            return render(request, "main/register.html")
    
    return render(request, "main/register.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Đã đăng xuất thành công!")
    return redirect("main:home")

def forgot_password_view(request):
    """Handle forgot password requests"""
    if request.user.is_authenticated:
        return redirect("main:home")
    
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        
        if not email:
            messages.error(request, "Vui lòng nhập email!")
            return render(request, "main/forgot_password.html")
        
        try:
            user = User.objects.get(email=email)
            # In production, you would send an actual reset email here
            # For now, we'll just show a success message
            messages.success(request, f"Hướng dẫn đặt lại mật khẩu đã được gửi đến {email}")
            return render(request, "main/forgot_password.html")
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(request, "Nếu email này tồn tại trong hệ thống, bạn sẽ nhận được email hướng dẫn.")
            return render(request, "main/forgot_password.html")
    
    return render(request, "main/forgot_password.html")


# ========== ADMIN DASHBOARD VIEWS ==========

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with stats and charts"""
    from django.utils import timezone as tz
    
    # Calculate stats
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    
    # Monthly revenue
    current_month = tz.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # compute monthly revenue for completed orders (support 'Hoàn thành' and 'completed')
    status_candidates = [Order.COMPLETED, 'completed']
    _, monthly_revenue = _compute_revenue_for_status(status_candidates, since=current_month)
    
    # Recent orders
    recent_orders = Order.objects.prefetch_related('items__product').order_by('-created_at')[:5]
    
    return render(request, 'main/admin_dashboard.html', {
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'monthly_revenue': monthly_revenue,
        'recent_orders': recent_orders,
    })


@user_passes_test(is_admin)
def admin_products(request):
    """Manage products list"""
    products = Product.objects.all().order_by('-id')
    
    return render(request, 'main/admin_products.html', {
        'products': products,
    })


@user_passes_test(is_admin)
def admin_product_add(request):
    """Add new product"""
    if request.method == 'POST':
        try:
            category_id = request.POST.get('category')
            if not category_id:
                messages.error(request, 'Vui lòng chọn danh mục!')
                return render(request, 'main/admin_product_add.html', {
                    'categories': Category.objects.all(),
                })
            
            category = get_object_or_404(Category, id=category_id)
            
            product = Product.objects.create(
                name=request.POST.get('name'),
                price=int(request.POST.get('price', 0)),
                category=category,
                stock=int(request.POST.get('stock', 0))
            )
            
            if 'image' in request.FILES:
                product.image = request.FILES['image']
                product.save()
            
            messages.success(request, f'Sản phẩm "{product.name}" đã được thêm thành công!')
            return redirect('main:admin_products')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return render(request, 'main/admin_product_add.html', {
                'categories': Category.objects.all(),
            })
    
    categories = Category.objects.all()
    return render(request, 'main/admin_product_add.html', {
        'categories': categories,
    })


@user_passes_test(is_admin)
def admin_categories(request):
    """Manage product categories"""
    categories = Category.objects.all()
    
    return render(request, 'main/admin_categories.html', {
        'categories': categories,
    })


@user_passes_test(is_admin)
def admin_orders(request):
    """Manage all orders with filtering"""
    orders = Order.objects.prefetch_related('items__product').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        mapped = _map_status_key(status_filter)
        if mapped != 'all':
            orders = orders.filter(status=mapped)

    # Get counts for stats (use VN status constants)
    pending_count = Order.objects.filter(status=Order.PENDING).count()
    shipping_count = Order.objects.filter(status=Order.DELIVERING).count()
    completed_count = Order.objects.filter(status=Order.COMPLETED).count()
    cancelled_count = Order.objects.filter(status=Order.CANCELLED).count()
    
    return render(request, 'main/admin_orders.html', {
        'orders': orders,
        'pending_count': pending_count,
        'shipping_count': shipping_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'current_status': status_filter,
    })


@user_passes_test(is_admin)
def admin_order_detail(request, pk):
    """View order details"""
    order = get_object_or_404(Order, pk=pk)
    
    return render(request, 'main/admin_order_detail.html', {
        'order': order,
    })


@user_passes_test(is_admin)
def admin_update_order_status(request, pk):
    """Update order status"""
    # Admin is not allowed to manually change status; system will auto-progress orders.
    messages.error(request, 'Admin không thể thay đổi trạng thái. Hệ thống tự động xử lý đơn hàng.')
    return redirect('main:admin_orders')


@user_passes_test(is_admin)
def admin_customers(request):
    """Manage customers"""
    customers = User.objects.filter(is_staff=False).order_by('-date_joined')
    
    return render(request, 'main/admin_customers.html', {
        'customers': customers,
    })

