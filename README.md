I. GIỚI THIỆU CHUNG

Dự án xây dựng website bán đồ gia dụng trực tuyến sử dụng Django, hỗ trợ đầy đủ các chức năng:

Xem sản phẩm

Đăng ký / đăng nhập người dùng

Phân quyền User / Admin

Đặt hàng và quản lý đơn hàng

Dashboard cho Admin

Upload ảnh sản phẩm

Thống kê cơ bản

Website hướng tới mô phỏng một hệ thống bán hàng thực tế, có nghiệp vụ rõ ràng và phân quyền đầy đủ theo yêu cầu học phần PAD341.

II. PHÂN QUYỀN NGƯỜI DÙNG (ROLE)
🔹 1. Guest (Chưa đăng nhập)

Xem danh sách sản phẩm

Tìm kiếm sản phẩm theo tên / danh mục

Không được đặt hàng

🔹 2. User (Đã đăng nhập)

Xem sản phẩm

Thêm sản phẩm vào giỏ hàng

Mua ngay / thanh toán

Xem đơn hàng của bản thân

Đăng xuất

🔹 3. Admin

Đăng nhập với tài khoản is_staff = True

Thêm / sửa / xóa sản phẩm

Upload ảnh sản phẩm

Xem Dashboard Admin

Xem danh sách đơn hàng

Thống kê tổng đơn hàng, doanh thu

⚠️ Dashboard Admin chỉ hiển thị khi đăng nhập bằng tài khoản Admin

III. CÁC THỰC THỂ (MODEL)

Dự án hiện có tối thiểu 5 thực thể có quan hệ, đáp ứng yêu cầu đề tài:

User (Django auth)

Category

Product

Order

OrderItem

🔗 Quan hệ chính

User — Order (1-n)

Order — OrderItem (1-n)

Category — Product (1-n)

Product — OrderItem (1-n)

IV. NGHIỆP VỤ CHÍNH (BUSINESS LOGIC)

1.  Đặt hàng

User chọn sản phẩm → nhập thông tin giao hàng

Hệ thống kiểm tra số lượng tồn kho

Tạo đơn hàng với trạng thái pending

2.  Quản lý đơn hàng

Admin xem danh sách đơn

Có thể duyệt / từ chối đơn hàng

Trạng thái: pending / approved / rejected

V. THỐNG KÊ – BÁO CÁO

Trong Dashboard Admin có:

Tổng số đơn hàng

Tổng doanh thu

Danh sách đơn hàng gần nhất

Đáp ứng yêu cầu thống kê – báo cáo của đề PAD341.

VI. UPLOAD ẢNH SẢN PHẨM

Sử dụng ImageField

Upload ảnh từ form Admin

Lưu trữ trong thư mục /media/

Chỉ cho phép định dạng ảnh hợp lệ (jpg, png…)

VII. CẤU TRÚC THƯ MỤC
web1/
│
├── main/
│ ├── migrations/
│ ├── templates/
│ │ └── main/
│ │ ├── home.html
│ │ ├── cart.html
│ │ ├── checkout.html
│ │ ├── checkout_now.html
│ │ ├── dashboard.html
│ │ ├── add_product.html
│ │ ├── edit_product.html
│ │ └── layout.html
│ │
│ ├── static/
│ │ └── main/
│ │ ├── css/
│ │ ├── js/
│ │ └── images/
│ │
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ └── forms.py
│
├── media/
├── db.sqlite3
├── manage.py
└── README.md
VIII. HƯỚNG DẪN CHẠY DỰ ÁN
🔧 1. Cài môi trường
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
🔧 2. Migration database
python manage.py makemigrations
python manage.py migrate
🔧 3. Tạo tài khoản Admin
python manage.py createsuperuser
▶️ 4. Chạy server
python manage.py runserver 8888
Truy cập:

Website: http://127.0.0.1:8888

Admin: http://127.0.0.1:8888/admin
IX. KẾT LUẬN

Dự án đã đáp ứng đầy đủ yêu cầu của học phần PAD341:

Có nghiệp vụ rõ ràng

Phân quyền chuẩn

Dữ liệu đầy đủ

Giao diện hoàn chỉnh

Có khả năng mở rộng thêm thanh toán online, biểu đồ nâng cao
