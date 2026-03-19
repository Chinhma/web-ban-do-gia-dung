# HomeStore — Hướng dẫn sử dụng (Tiếng Việt)

Phiên bản: bản nội bộ (local dev)

---

1. Giới thiệu

---

HomeStore là dự án mẫu bán hàng trực tuyến xây dựng bằng Django. Ứng dụng hỗ trợ: quản lý sản phẩm, giỏ hàng, đặt hàng, quản trị (Admin dashboard) và quản lý trạng thái đơn hàng theo luồng thực tế (Chờ xác nhận → Đã xác nhận → Vận chuyển → Đang giao → Hoàn thành / Bị từ chối).

2. Yêu cầu hệ thống

---

- Python 3.8+ (khuyến nghị 3.10+)
- SQLite (mặc định) hoặc cơ sở dữ liệu khác (Postgres, MySQL)
- Pip

3. Cài đặt nhanh (local)

---

1. Clone repository và chuyển thư mục dự án:

   git clone <repo-url>
   cd web1

2. Tạo virtualenv và cài phụ thuộc:

   python -m venv venv
   venv\Scripts\activate # Windows
   pip install -r requirements.txt

3. Áp dụng migrations:

   python manage.py migrate

4. Tạo tài khoản Admin (superuser):

   python manage.py createsuperuser

5. Khởi động ứng dụng:

   python manage.py runserver

   Mở trình duyệt: http://127.0.0.1:8000

6. Cấu trúc chính của dự án

---

- `main/` : app chính chứa models, views, templates, static
- `media/` : nơi lưu ảnh sản phẩm upload
- `db.sqlite3` : database (local)
- `manage.py` : lệnh điều hành Django

5. Mô tả chức năng quan trọng

---

- Sản phẩm (Product): có tên, giá, tồn kho, ảnh, danh mục
- Đơn hàng (Order): lưu trạng thái và thông tin giao hàng
- Luồng trạng thái đơn hàng (gợi ý hiện tại):
  - `pending` — Chờ xác nhận (mặc định khi khách đặt)
  - `approved` — Đã xác nhận (sau khi admin xác nhận / hệ thống tự chuyển khi thanh toán thành công)
  - `shipping` — Chuẩn bị vận chuyển
  - `delivering` — Đang giao
  - `review` — Chờ đánh giá / Hoàn thành
  - `rejected` — Bị từ chối / Hủy

6. Hướng dẫn admin (cách vận hành đơn hàng)

---

- Truy cập Admin Dashboard: `/admin-panel/` (hoặc trang Django admin `/admin`)
- Ở trang quản lý đơn hàng (Admin orders), quy trình gợi ý:
  1.  Đơn mới sẽ ở trạng thái **Chờ xác nhận** (`pending`).
  2.  Admin có thể **Xác nhận** (không gọi là “Duyệt” nữa) — hệ thống kiểm tra tồn kho và trừ tồn.
  3.  Sau khi xác nhận, admin hoặc hệ thống chuyển sang **Chuẩn bị vận chuyển** (`shipping`), rồi **Đang giao** (`delivering`), rồi **Hoàn thành** (`review`).
  4.  Admin chỉ can thiệp khi có lỗi (hết hàng, thanh toán thất bại, thông tin không hợp lệ).

Gợi ý cho developer: nếu muốn hệ thống tự động chuyển trạng thái (như Shopee), bạn có thể:

- Tạo task nền (cron / Celery) kiểm tra thanh toán và tồn kho, rồi cập nhật `order.status` tương ứng.

7. Cài đặt media & static

---

- Trong môi trường dev, Django phục vụ `MEDIA` và `STATIC` nếu `DEBUG = True`.
- Ảnh sản phẩm upload lưu trong `media/products/`.

8. Migrations & seed dữ liệu

---

- Tạo migration khi thay đổi model:

  python manage.py makemigrations
  python manage.py migrate

- Nếu có script seed (ví dụ `seed_categories.py`), chạy để thêm dữ liệu mẫu.

9. Chạy test (nếu có)

---

Nếu dự án có tests, chạy:

    python manage.py test

10. Vấn đề thường gặp

---

- Lỗi không tìm thấy media: kiểm tra `MEDIA_ROOT` và `MEDIA_URL` trong `web1/settings.py`.
- Lỗi CSRF trên các form AJAX: đảm bảo token được gửi trong header `X-CSRFToken` hoặc trường `csrfmiddlewaretoken`.

11. Ghi chú & tiếp theo

---

12. Cấu hình gửi email (SMTP) — gửi thật (production)

---

Mặc định trong `settings.py` đang dùng `console.EmailBackend` để dễ phát triển (email được in ra console).
Để gửi email thật (SMTP), cấu hình các biến môi trường trước khi chạy server.

Biến môi trường cần thiết:

- `DJANGO_EMAIL_BACKEND`: (tuỳ chọn) ví dụ `django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST`: ví dụ `smtp.gmail.com`
- `EMAIL_PORT`: ví dụ `587`
- `EMAIL_USE_TLS`: `True` hoặc `False`
- `EMAIL_HOST_USER`: email dùng để gửi (tên đăng nhập SMTP)
- `EMAIL_HOST_PASSWORD`: mật khẩu SMTP (với Gmail, dùng app password)
- `DEFAULT_FROM_EMAIL`: địa chỉ From trong email (ví dụ `no-reply@yourdomain.com`)

Ví dụ (.env hoặc export):

Windows PowerShell:

```powershell
$env:DJANGO_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
$env:EMAIL_HOST = 'smtp.gmail.com'
$env:EMAIL_PORT = '587'
$env:EMAIL_USE_TLS = 'True'
$env:EMAIL_HOST_USER = 'youremail@gmail.com'
$env:EMAIL_HOST_PASSWORD = 'your_app_password'
$env:DEFAULT_FROM_EMAIL = 'no-reply@yourdomain.com'
python manage.py runserver
```

Linux / macOS:

```bash
export DJANGO_EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
export EMAIL_HOST='smtp.gmail.com'
export EMAIL_PORT='587'
export EMAIL_USE_TLS='True'
export EMAIL_HOST_USER='youremail@gmail.com'
export EMAIL_HOST_PASSWORD='your_app_password'
export DEFAULT_FROM_EMAIL='no-reply@yourdomain.com'
python manage.py runserver
```

Gmail notes:

- Google yêu cầu tạo "App Password" cho ứng dụng hoặc bật cấu hình OAuth/SMTP relay; thường không dùng mật khẩu chính.

Kiểm tra flow quên mật khẩu (test):

1. Mở `/forgot-password/`, nhập email đã đăng ký.
2. Nếu cấu hình SMTP đúng — email chứa link reset sẽ được gửi tới địa chỉ đó.
3. Nếu còn dùng `console` backend, email sẽ được in ra console nơi `runserver` chạy (dễ debug).

Nếu muốn, tôi sẽ:

- A: Thêm ví dụ `.env.example` và hướng dẫn dùng `python-dotenv` hoặc `django-environ` để load biến môi trường, hoặc
- B: Cấu hình gửi email qua Gmail (thêm hướng dẫn tạo App Password và bảo mật), hoặc
- C: Tự cấu hình SMTP cho bạn (bạn cung cấp thông tin host/port và tôi cập nhật `settings.py` tạm thời).
