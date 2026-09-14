# TKB PTIT tự động

Tự động đăng nhập QLDT PTIT, lấy thời khóa biểu, và hiển thị trên 1 trang web
riêng (GitHub Pages) — có thể mở trên điện thoại như 1 app.
Thông báo lịch học hôm nay vào mỗi 6h sáng

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

Để đảm bảo thông báo từ Bot luôn nổ chuông và hiển thị màn hình khóa lúc 6:00 sáng, bạn cần kiểm tra 3 cài đặt sau:

#### 1. Cấu hình thông báo Kênh trên Discord (Mobile)
Mặc định Discord sẽ tắt tiếng các tin nhắn không tag `@mention`.
1. Mở ứng dụng Discord trên điện thoại $\rightarrow$ Truy cập kênh **`#lich-hoc`**.
2. Nhấp vào **Tên kênh `#lich-hoc`** ở góc trên cùng.
3. Chọn **Thông báo (Notifications)** $\rightarrow$ Chuyển sang **Tất cả các tin nhắn (All Messages)**.
4. Đảm bảo mục **Tắt âm máy chủ (Mute Server)** đang ở trạng thái Tắt.

#### 2. Cấp quyền Thông báo hệ điều hành (iOS / Android)
* **Đối với iPhone (iOS):**
  * Vào **Cài đặt (Settings)** điện thoại $\rightarrow$ **Thông báo** $\rightarrow$ **Discord**.
  * Bật **Cho phép thông báo** và tích đủ 3 kiểu cảnh báo: *Màn hình khóa, Trung tâm thông báo, Biểu ngữ*.
  * Kiểm tra và tắt chế độ **Không làm phiền (Do Not Disturb)** hoặc thêm Discord vào danh sách ngoại lệ của chế độ **Tập trung (Focus)**.
* **Đối với Android:**
  * Vào **Cài đặt** $\rightarrow$ **Ứng dụng** $\rightarrow$ **Discord** $\rightarrow$ **Thông báo** $\rightarrow$ Bật **Cho phép thông báo**.
  * Tắt chế độ **Tối ưu hóa pin (Tiết kiệm pin)** cho ứng dụng Discord để tránh Android dừng tiến trình chạy ngầm.

#### 3. Ép nổ thông báo bằng Tag `@everyone` (Tùy chọn)
Nếu muốn Bot phát âm thanh cảnh báo ngay cả khi đang mở ứng dụng, bổ sung dòng `"content": "@everyone"` vào `payload` trong file `scripts/fetch_tkb.py`:

```python
    payload = {
        "username": "TKB PTIT Bot",
        "content": "@everyone",  # Ép nổ chuông và đẩy notification lập tức
        "embeds": [...]
    }
