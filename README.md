# TKB PTIT tự động

Tự động đăng nhập QLDT PTIT, lấy thời khóa biểu, và hiển thị trên 1 trang web
riêng (GitHub Pages) — có thể mở trên điện thoại như 1 app.
Thông báo lịch học hằng ngày vào mỗi 6h sáng

## Cách cài đặt

### Bước 1: Thêm tài khoản QLDT vào GitHub Secrets

Vào repo trên GitHub → **Settings** → **Secrets and variables** → **Actions** →
**New repository secret**, thêm 2 secret:

- `QLDT_USERNAME` — tài khoản QLDT của bạn 
- `QLDT_PASSWORD` — mật khẩu QLDT của bạn

### Bước 2: Chạy thử workflow

Vào tab **Actions** trên GitHub → chọn workflow **"Cap nhat TKB PTIT"** →
bấm **"Run workflow"** để chạy thử ngay.

### Bước 3: Bật GitHub Pages

Vào **Settings** → **Pages** → mục **Source**, chọn nhánh `main` và thư mục
`/docs`. Sau vài phút, trang sẽ có địa chỉ dạng:
https://<tên-github-của-bạn>.github.io/TKB-QLDT/

---

### 🔔 Hướng dẫn cài đặt nhận thông báo trên Điện thoại
## 🛠️ Hướng Dẫn Cài Đặt & Vận Hành Bot Tự Động

Hệ thống sử dụng **GitHub Actions** để tự động cào thời khóa biểu từ cổng QLDT PTIT và gửi thông báo nhắc nhở về Discord hoàn toàn miễn phí.

---

### 1. Cấu hình GitHub Secrets (Bảo mật)

Để Bot có thể đăng nhập vào QLDT và gửi thông báo Discord, bạn cần thêm các thông tin đăng nhập vào phần **Secrets** của Repository (tránh bị lộ mật khẩu):

1. Vào Repository trên GitHub $\rightarrow$ **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**.
2. Bấm nút **New repository secret** và thêm lần lượt 3 biến sau:

| Tên Secret | Giá trị (Value) |
| :--- | :--- |
| `QLDT_USERNAME` | Mã sinh viên PTIT của bạn (ví dụ: `B21DCCNxxx`) |
| `QLDT_PASSWORD` | Mật khẩu đăng nhập trang QLDT |
| `DISCORD_WEBHOOK_URL` | Link Discord Webhook của kênh bạn muốn nhận thông báo |

---

### 4. Hướng dẫn lấy Link Discord Webhook (Nhận thông báo)

Để Bot có thể tự động bắn tin nhắn nhắc học vào ứng dụng Discord của bạn, hãy tạo Webhook theo các bước sau:

1. **Mở Discord** $\rightarrow$ Vào máy chủ (Server) của bạn $\rightarrow$ Chọn kênh chữ (Text Channel) bạn muốn nhận thông báo thời khóa biểu.
2. Bấm vào biểu tượng **Bánh răng ⚙️ (Edit Channel)** ngay bên cạnh tên kênh.
3. Chọn mục **Integrations (Tích hợp)** $\rightarrow$ Bấm chọn **Webhooks** (hoặc **Create Webhook**).
4. Bấm **New Webhook**, bạn có thể đổi tên Bot (ví dụ: *PTIT Bot TKB*) và thay ảnh đại diện cho Bot nếu muốn.
5. Bấm nút **Copy Webhook URL**.
6. Dán đường link vừa sao chép này vào phần **Secrets** của GitHub dưới tên biến `DISCORD_WEBHOOK_URL` (như hướng dẫn ở Mục 1).


