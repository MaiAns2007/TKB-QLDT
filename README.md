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

### 2. File Cấu Hình Workflow (`.github/workflows/fetch-tkb.yml`)

Đảm bảo file `.github/workflows/fetch-tkb.yml` trên repo của bạn có cấu hình `cron` chạy tự động hàng ngày và cho phép chạy thủ công (`workflow_dispatch`):

```yaml
name: Cap nhat TKB PTIT

on:
  schedule:
    # Chạy tự động lúc 04:21 AM giờ Việt Nam (21:21 UTC ngày hôm trước)
    - cron: "21 21 * * *"
  workflow_dispatch: {} # Cho phép bấm nút "Run workflow" chạy thủ công

permissions:
  contents: write

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Cài thư viện cần thiết
        run: pip install requests

      - name: Lấy TKB mới nhất & Gửi thông báo
        env:
          QLDT_USERNAME: ${{ secrets.QLDT_USERNAME }}
          QLDT_PASSWORD: ${{ secrets.QLDT_PASSWORD }}
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
        run: python scripts/fetch_tkb.py

