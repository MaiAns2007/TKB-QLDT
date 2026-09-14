"""
Script tu dong dang nhap QLDT PTIT va lay Thoi khoa bieu (TKB) toan hoc ky,
luu ra file JSON tinh de trang GitHub Pages doc va hien thi.

Bien moi truong can co (dat trong GitHub Actions Secrets):
    QLDT_USERNAME  - tai khoan QLDT (vd: n25dccn001b)
    QLDT_PASSWORD  - mat khau QLDT

Chay thu o may local (khong khuyen khich luu mat khau ra file .env commit len git):
    QLDT_USERNAME=xxx QLDT_PASSWORD=xxx python scripts/fetch_tkb.py
"""

import base64
import json
import os
import sys
from urllib.parse import urlparse, parse_qs, unquote

import requests

BASE_URL = "https://qldt.ptit.edu.vn"
LOGIN_PATH = "/api/pn-signin"
TKB_PATH = "/api/sch/w-locdstkbtuanusertheohocky"

# Hoc ky can lay TKB. Dinh dang: <nam bat dau><ky> vi du 20261 = HK1 nam hoc 2026-2027
# Neu muon tu dong lay hoc ky hien tai, co the mo rong bang cach goi them
# API "w-locdshockytkbuser" (danh sach hoc ky) va chon phan tu dau tien.
HOC_KY = os.environ.get("QLDT_HOC_KY", "20261")


def b64_encode_json(obj: dict) -> str:
    """Base64-encode 1 dict thanh chuoi giong nhu website dang lam."""
    raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    return base64.b64encode(raw).decode("utf-8")


def b64_decode_json(s: str) -> dict:
    """Giai ma nguoc lai chuoi base64 thanh dict."""
    # Chuoi tren URL co the da bi urlencode, giai ma truoc khi base64-decode
    s = unquote(s)
    # bu them padding '=' neu thieu (base64 yeu cau do dai chia het cho 4)
    padding = "=" * (-len(s) % 4)
    raw = base64.b64decode(s + padding)
    return json.loads(raw.decode("utf-8"))


def login(username: str, password: str) -> dict:
    """
    Dang nhap QLDT, tra ve dict chua it nhat:
        - access_token: JWT dung cho header Authorization
        - session (requests.Session da luu cac cookie xsrf-*, .uat can thiet)
    """
    session = requests.Session()

    payload = {
        "username": username,
        "password": password,
        "uri": f"{BASE_URL}/#/home",
        "vaitro": "",
    }
    code = b64_encode_json(payload)

    resp = session.get(
        f"{BASE_URL}{LOGIN_PATH}",
        params={"code": code, "gopage": "", "mgr": "1"},
        allow_redirects=False,  # QUAN TRONG: khong tu dong theo redirect,
                                 # vi thong tin can lay nam trong header Location
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

    location = resp.headers.get("Location", "")
    if not location:
        # Thêm 2 dòng này trước dòng raise RuntimeError
        print("--- DEBUG BẮT ĐẦU ---")
        print("URL phản hồi:", res.url)
        print("Nội dung phản hồi từ QLDT:", res.text[:1000]) # In 1000 ký tự đầu của trang web
        print("--- DEBUG KẾT THÚC ---")

        raise RuntimeError("Khong tim thay tham so CurrUser trong URL chuyen huong")
        raise RuntimeError("Khong tim thay header Location sau khi dang nhap")

    parsed = urlparse(location)
    query = parse_qs(parsed.query)

    curr_user_raw = query.get("CurrUser", [None])[0]
    if not curr_user_raw:
        raise RuntimeError("Khong tim thay tham so CurrUser trong URL chuyen huong")

    curr_user = b64_decode_json(curr_user_raw)

    if not curr_user.get("result"):
        raise RuntimeError(f"Dang nhap that bai: {curr_user}")

    access_token = curr_user.get("access_token")
    if not access_token:
        raise RuntimeError("Khong tim thay access_token trong du lieu dang nhap")

    return {
        "access_token": access_token,
        "session": session,  # da mang san cac cookie xsrf-*, .uat
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
    Rut gon du lieu tho thanh cau truc de trang web hien thi,
    chi giu lai cac truong thuc su can dung.
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
                    "ngay_hoc": mon.get("ngay_hoc", "")[:10],  # chi lay YYYY-MM-DD
                    "thu": mon.get("thu_kieu_so"),  # 2=Thu2 ... 8=CN (kieu PTIT)
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


if __name__ == "__main__":
    main()
