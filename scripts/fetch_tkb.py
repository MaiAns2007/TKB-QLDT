"""
Script tu dong dang nhap QLDT PTIT va lay Thoi khoa bieu (TKB) toan hoc ky,
luu ra file JSON tinh de trang GitHub Pages doc va hien thi.

Bien moi truong can co (dat trong GitHub Actions Secrets):
    QLDT_USERNAME  - tai khoan QLDT (vd: n25dccn001b)
    QLDT_PASSWORD  - mat khau QLDT
"""

import base64
from datetime import datetime
import json
import os
import sys
from urllib.parse import urlparse, parse_qs, unquote

import requests

BASE_URL = "https://qldt.ptit.edu.vn"
LOGIN_PATH = "/api/pn-signin"
TKB_PATH = "/api/sch/w-locdstkbtuanusertheohocky"

# Hoc ky can lay TKB. Dinh dang: <nam bat dau><ky> vi du 20261 = HK1 nam hoc 2026-2027
HOC_KY = os.environ.get("QLDT_HOC_KY", "20261")


def b64_encode_json(obj: dict) -> str:
    """Base64-encode 1 dict thanh chuoi giong nhu website dang lam."""
    raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")


def b64_decode_json(s: str) -> dict:
    """Giai ma nguoc lai chuoi base64 thanh dict."""
    s = unquote(s)
    padding = "=" * (-len(s) % 4)
    raw = base64.b64decode(s + padding)
    return json.loads(raw.decode("utf-8"))


def login(username: str, password: str) -> dict:
    """
    Dang nhap QLDT, tra ve dict chua access_token va session.
    """
    session = requests.Session()

    payload = {
        "username": username,
        "password": password,
        "uri": f"{BASE_URL}/#/home",
        "vaitro": "",
    }
    code = b64_encode_json(payload)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"{BASE_URL}/"
    }

    resp = session.get(
        f"{BASE_URL}{LOGIN_PATH}",
        params={"code": code, "gopage": "", "mgr": "1"},
        headers=headers,
        allow_redirects=False,
        timeout=20,
    )

    print("--- DEBUG DANG NHAP QLDT ---", flush=True)
    print("Status code:", resp.status_code, flush=True)
    print("Header Location:", resp.headers.get("Location"), flush=True)
    print("Response text (300 ký tự đầu):", resp.text[:300], flush=True)
    print("----------------------------", flush=True)

    if resp.status_code not in (301, 302, 303, 307, 308):
        raise RuntimeError(
            f"Dang nhap that bai hoac sai dinh dang: HTTP {resp.status_code}"
        )

    location = resp.headers.get("Location") or resp.headers.get("location") or ""
    if not location:
        raise RuntimeError("Khong tim thay header Location sau khi dang nhap")

 # Xử lý cắt bỏ dấu '#' hoặc thay '#/home?' thành '?' để parse_qs đọc được query parameters
    target_url = location.replace("#/home?", "?").replace("#/", "?")
    parsed = urlparse(target_url)
    query = parse_qs(parsed.query)

    curr_user_list = query.get("CurrUser") or query.get("currUser")
    if not curr_user_list or not curr_user_list[0]:
        raise RuntimeError("Khong tim thay tham so CurrUser trong URL chuyen huong")

    curr_user_raw = curr_user_list[0]
    curr_user = b64_decode_json(curr_user_raw)
    if not curr_user.get("result"):
        raise RuntimeError(f"Dang nhap that bai: {curr_user}")

    access_token = curr_user.get("access_token")
    if not access_token:
        raise RuntimeError("Khong tim thay access_token trong du lieu dang nhap")

    return {
        "access_token": access_token,
        "session": session,
        "user_info": curr_user,
    }


def fetch_tkb(auth: dict, hoc_ky: str) -> dict:
    """Goi API lay TKB toan hoc ky bang access_token va session da dang nhap."""
    session: requests.Session = auth["session"]
    headers = {
        "Authorization": f"Bearer {auth['access_token']}",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
    }
    payload = {
        "filter": {"hoc_ky": int(hoc_ky), "ten_hoc_ky": ""},
        "additional": {
            "paging": {"limit": 100, "page": 1},
            "ordering": [{"name": None, "order_type": None}],
        },
    }

    resp = session.post(
        f"{BASE_URL}{TKB_PATH}",
        json=payload,
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    if not data.get("result"):
        raise RuntimeError(f"API tra ve loi: {data}")

    return data["data"]


def simplify_tkb(raw_data: dict) -> dict:
    """
    Rut gon du lieu tho thanh cau truc de trang web hien thi.
    """
    ds_tiet = {
        t["tiet"]: {"bat_dau": t["gio_bat_dau"], "ket_thuc": t["gio_ket_thuc"]}
        for t in raw_data.get("ds_tiet_trong_ngay", [])
    }

    tuan_list = []
    for tuan in raw_data.get("ds_tuan_tkb", []):
        buoi_hoc = []
        for mon in tuan.get("ds_thoi_khoa_bieu", []):
            buoi_hoc.append(
                {
                    "ma_mon": mon.get("ma_mon"),
                    "ten_mon": (mon.get("ten_mon") or "").strip(),
                    "nhom": mon.get("ma_nhom"),
                    "giang_vien": mon.get("ten_giang_vien"),
                    "phong": mon.get("ma_phong"),
                    "ngay_hoc": mon.get("ngay_hoc", "")[:10],
                    "thu": mon.get("thu_kieu_so"),
                    "tiet_bat_dau": mon.get("tiet_bat_dau"),
                    "so_tiet": mon.get("so_tiet"),
                    "la_day_bu": mon.get("is_day_bu", False),
                }
            )
        tuan_list.append(
            {
                "tuan": tuan.get("tuan_hoc_ky"),
                "thong_tin": tuan.get("thong_tin_tuan"),
                "ngay_bat_dau": tuan.get("ngay_bat_dau"),
                "ngay_ket_thuc": tuan.get("ngay_ket_thuc"),
                "buoi_hoc": buoi_hoc,
            }
        )

    return {"ds_tiet_trong_ngay": ds_tiet, "ds_tuan": tuan_list}

def send_discord_notification(simplified_data: dict):
    """Gui thong bao lich hoc ngay hom nay ve Discord Webhook."""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Chua cau hinh DISCORD_WEBHOOK_URL, bo qua gui thong bao.")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    mon_hom_nay = []

    # Loc mon hoc theo ngay hien tai
    for tuan in simplified_data.get("ds_tuan", []):
        for mon in tuan.get("buoi_hoc", []):
            if mon.get("ngay_hoc") == today_str:
                mon_hom_nay.append(mon)

    # Soan noi dung Embed
    if not mon_hom_nay:
        description = "🎉 **Hom nay ban khong co lich hoc! Thoa suc nghi ngoi.**"
        color = 3066993  # Xanh la
    else:
        description = ""
        for idx, m in enumerate(mon_hom_nay, 1):
            description += (
                f"**{idx}. {m['ten_mon']}**\n"
                f"⏱ **Tiet:** {m['tiet_bat_dau']} ({m['so_tiet']} tiet)\n"
                f"🏫 **Phong:** {m['phong']}\n"
                f"👨‍🏫 **GV:** {m['giang_vien'] or 'Chua cap nhat'}\n\n"
            )
        color = 15158332  # Cam/Do

    payload = {
        "username": "TKB PTIT Bot",
        "embeds": [
            {
                "title": f"📅 LỊCH HỌC HÔM NAY ({today_str})",
                "description": description,
                "color": color,
                "footer": {"text": "Tu dong cap nhat tu QLDT PTIT"}
            }
        ]
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        print("Da gui thong bao Discord thanh cong!")
    except Exception as e:
        print(f"Loi gui thong bao Discord: {e}")

def main():
    username = os.environ.get("QLDT_USERNAME")
    password = os.environ.get("QLDT_PASSWORD")

    if not username or not password:
        print("Thieu bien moi truong QLDT_USERNAME / QLDT_PASSWORD", file=sys.stderr)
        sys.exit(1)

    print("Dang dang nhap QLDT...")
    auth = login(username, password)
    print(f"Dang nhap thanh cong: {auth['user_info'].get('name')}")

    print(f"Dang lay TKB hoc ky {HOC_KY}...")
    raw = fetch_tkb(auth, HOC_KY)

    simplified = simplify_tkb(raw)

    out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "tkb.json")
    out_path = os.path.abspath(out_path)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)

    print(f"Da luu TKB vao {out_path}")
print(f"Da luu TKB vao {out_path}")

    # Gửi thông báo đến Discord (THÊM DÒNG NÀY)
send_discord_notification(simplified)


if __name__ == "__main__":
    main()
