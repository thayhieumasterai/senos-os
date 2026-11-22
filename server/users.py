"""Người dùng của một workspace SenOS (2026-11-22): chủ + những người chủ thêm vào, mỗi người một vai trò.

Trước bản này một máy SenOS có đúng MỘT tài khoản (khối `auth` trong settings.json). Khối đó vẫn là CHỦ, không đổi gì,
nên mọi máy cũ chạy y nguyên. Người dùng thêm vào nằm ở STATE_DIR/users.json:

    {"users": [{"id": "u_ab12", "username": "lan", "name": "Lan", "role": "limited", "pw_hash": ..., "salt": ...,
                "disabled": false, "created_at": 1790000000, "personal_brain": "<đường dẫn bộ não riêng>",
                "perms": {"brains": {"<đường dẫn bộ não>": "read" | "write"},
                          "agents": {"<đường dẫn bộ não>": ["*"] | ["slug", ...]},
                          "channels": ["<id tài khoản kênh>", ...],
                          "outside": false}}]}

Vai trò:
- owner   : tài khoản gốc (khối `auth`), id "owner". Làm được mọi thứ, là người duy nhất quản lý người dùng.
- full    : như chủ, trừ quản lý người dùng.
- limited : chỉ những gì được cấp. Bộ não riêng (`personal_brain`) luôn là "write" và mọi Agent trong đó.

Ai đang gọi: lớp xác thực trong main.py đặt CURRENT cho mỗi request (contextvars, nên việc nền sinh ra trong request
mang theo luôn). Hàm chọn bộ não mặc định đọc nó để người "limited" không bao giờ rơi vào bộ não chung của chủ.

Số người dùng: SenOS Cloud ghi `max_users` (số người THÊM, không tính chủ) vào tệp SENOS_CLOUD_LIMITS, cùng tệp với
`max_channels`. Không có tệp hoặc null = không giới hạn (bản tự cài).
"""
from __future__ import annotations

import contextvars
import json
import os
import re
import secrets
import threading
import time
from pathlib import Path
from typing import Optional

import config as cfgmod

PATH = Path(cfgmod.STATE_DIR) / "users.json"
ROLES = ("full", "limited")
LEVELS = ("read", "write")
OWNER = {"id": "owner", "role": "owner", "name": "", "username": "", "perms": {}, "personal_brain": ""}
USERNAME_RX = re.compile(r"^[a-z0-9][a-z0-9._-]{1,31}$")
_LOCK = threading.RLock()

# Ai đang gọi request này (dict người dùng, hoặc OWNER). Mặc định là chủ: mã chạy ngoài request (vòng nền, bot)
# vẫn là việc của chủ như trước.
CURRENT: contextvars.ContextVar[dict] = contextvars.ContextVar("senos_user", default=OWNER)


# ---------------------------------------------------------------- lưu trữ
def _load() -> dict:
    try:
        d = json.loads(PATH.read_text(encoding="utf-8"))
        if isinstance(d, dict) and isinstance(d.get("users"), list):
            return d
    except Exception:  # noqa: BLE001
        pass
    return {"users": []}


def _save(d: dict) -> None:
    tmp = PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, PATH)
    try:
        os.chmod(PATH, 0o600)          # mật khẩu băm: chỉ chủ máy đọc (vô hại trên Windows)
    except Exception:  # noqa: BLE001
        pass


def public(u: dict) -> dict:
    """Bản không có mật khẩu băm, để trả cho giao diện."""
    return {k: v for k, v in u.items() if k not in ("pw_hash", "salt")}


def list_users() -> list:
    with _LOCK:
        return [public(u) for u in _load()["users"]]


def get(uid: str) -> Optional[dict]:
    if not uid or uid == "owner":
        return None
    with _LOCK:
        return next((u for u in _load()["users"] if u.get("id") == uid), None)


def by_username(name: str) -> Optional[dict]:
    n = (name or "").strip().lower()
    with _LOCK:
        return next((u for u in _load()["users"] if u.get("username") == n), None)


# ---------------------------------------------------------------- số chỗ
def max_users() -> Optional[int]:
    """Số người được thêm (không tính chủ). None = không giới hạn."""
    path = os.getenv("SENOS_CLOUD_LIMITS", "").strip()
    if not path:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            v = json.load(f).get("max_users")
        return None if v is None else max(0, int(v))
    except Exception:  # noqa: BLE001
        return None


def seats() -> dict:
    with _LOCK:
        used = sum(1 for u in _load()["users"] if not u.get("disabled"))
    cap = max_users()
    return {"used": used, "max": cap, "left": None if cap is None else max(0, cap - used)}


# ---------------------------------------------------------------- sửa
def _clean_perms(p) -> dict:
    p = p if isinstance(p, dict) else {}
    brains = {str(k): v for k, v in (p.get("brains") or {}).items() if v in LEVELS and k}
    agents = {}
    for k, v in (p.get("agents") or {}).items():
        if k and isinstance(v, list):
            agents[str(k)] = ["*"] if "*" in v else sorted({str(s) for s in v if s})[:500]
    chans = sorted({str(c) for c in (p.get("channels") or []) if c})[:500]
    return {"brains": brains, "agents": agents, "channels": chans, "outside": bool(p.get("outside"))}


def _owner_username() -> str:
    try:
        return str((cfgmod.read_settings().get("auth") or {}).get("username") or "").strip().lower()
    except Exception:  # noqa: BLE001
        return ""


def create(username: str, password: str, name: str = "", role: str = "limited", perms=None,
           personal_brain: str = "") -> dict:
    """Thêm một người. Trả {"ok": True, "user": ...} hoặc {"ok": False, "error": ...}."""
    username = (username or "").strip().lower()
    if not USERNAME_RX.match(username):
        return {"ok": False, "error": "Tên đăng nhập 2-32 ký tự, chữ thường không dấu, số, dấu chấm, gạch."}
    if username == _owner_username():
        return {"ok": False, "error": "Tên này đang là tên đăng nhập của chủ."}
    password = cfgmod.clean_password(password)
    if len(password) < 8:
        return {"ok": False, "error": "Mật khẩu tối thiểu 8 ký tự."}
    if role not in ROLES:
        role = "limited"
    with _LOCK:
        d = _load()
        if any(u.get("username") == username for u in d["users"]):
            return {"ok": False, "error": "Tên đăng nhập đã có người dùng."}
        s = seats()
        if s["max"] is not None and s["used"] >= s["max"]:
            return {"ok": False, "seats": s,
                    "error": f"Gói hiện tại cho tối đa {s['max']} người dùng. Mua thêm người dùng ở trang Gói & tín dụng."}
        h, salt = cfgmod.hash_password(password)
        u = {"id": "u_" + secrets.token_hex(4), "username": username, "name": (name or username).strip()[:80],
             "role": role, "pw_hash": h, "salt": salt, "disabled": False, "created_at": int(time.time()),
             "personal_brain": personal_brain, "perms": _clean_perms(perms)}
        d["users"].append(u)
        _save(d)
    return {"ok": True, "user": public(u)}


def update(uid: str, **fields) -> dict:
    with _LOCK:
        d = _load()
        u = next((x for x in d["users"] if x.get("id") == uid), None)
        if not u:
            return {"ok": False, "error": "Không tìm thấy người dùng."}
        if "name" in fields and fields["name"] is not None:
            u["name"] = str(fields["name"]).strip()[:80] or u["username"]
        if fields.get("role") in ROLES:
            u["role"] = fields["role"]
        if "perms" in fields and fields["perms"] is not None:
            u["perms"] = _clean_perms(fields["perms"])
        if "disabled" in fields and fields["disabled"] is not None:
            want = bool(fields["disabled"])
            if u.get("disabled") and not want:        # bật lại cũng phải còn chỗ
                s = seats()
                if s["max"] is not None and s["used"] >= s["max"]:
                    return {"ok": False, "error": f"Gói chỉ cho {s['max']} người dùng đang hoạt động."}
            u["disabled"] = want
        if fields.get("password"):
            pw = cfgmod.clean_password(fields["password"])
            if len(pw) < 8:
                return {"ok": False, "error": "Mật khẩu tối thiểu 8 ký tự."}
            u["pw_hash"], u["salt"] = cfgmod.hash_password(pw)
        if fields.get("personal_brain"):
            u["personal_brain"] = str(fields["personal_brain"])
        _save(d)
    if fields.get("disabled") or fields.get("password") or "perms" in fields or fields.get("role"):
        end_sessions(uid)        # quyền đổi: phiên cũ đăng nhập lại để nhận quyền mới
    return {"ok": True, "user": public(u)}


def delete(uid: str) -> dict:
    with _LOCK:
        d = _load()
        n = len(d["users"])
        d["users"] = [u for u in d["users"] if u.get("id") != uid]
        if len(d["users"]) == n:
            return {"ok": False, "error": "Không tìm thấy người dùng."}
        _save(d)
    end_sessions(uid)
    return {"ok": True}


def verify(username: str, password: str) -> Optional[dict]:
    u = by_username(username)
    if not u or u.get("disabled") or not cfgmod.clean_password(password):
        cfgmod.hash_password(str(password or "x"), "00" * 16)     # same cost either way: no username probing by timing
        return None
    for cand in dict.fromkeys((str(password), cfgmod.clean_password(password))):
        h, _ = cfgmod.hash_password(cand, u.get("salt"))
        if secrets.compare_digest(h, u.get("pw_hash") or ""):
            return u
    return None


# ---------------------------------------------------------------- phiên
# Which added user a session belongs to, by token digest. Kept apart from config.SESSION_META on purpose (security
# review 2026-11-22): that file is written loosely and reads back as {} when damaged, and a session with no user there
# is the owner's. This one is written atomically, so a damaged device list never turns a user's session into the owner's.
_SESS_PATH = Path(cfgmod.STATE_DIR) / "user_sessions.json"


def _digest(token: str) -> str:
    import hashlib
    return hashlib.sha256(str(token or "").encode("utf-8")).hexdigest()


def _sess_load() -> dict:
    try:
        d = json.loads(_SESS_PATH.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except FileNotFoundError:
        return {}
    except Exception:  # noqa: BLE001
        return {"__broken__": True}


def _sess_save(d: dict) -> None:
    tmp = _SESS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(d), encoding="utf-8")
    os.replace(tmp, _SESS_PATH)
    try:
        os.chmod(_SESS_PATH, 0o600)
    except Exception:  # noqa: BLE001
        pass


def bind_session(token: str, uid: str) -> None:
    with _LOCK:
        d = _sess_load()
        d.pop("__broken__", None)
        d[_digest(token)] = uid
        live = {_digest(t) for t in cfgmod.SESSIONS}
        _sess_save({k: v for k, v in d.items() if k in live})


def session_user(token: str) -> dict:
    """Người dùng của một phiên đăng nhập. Phiên không ghi ai (mọi phiên trước bản này) là của chủ."""
    with _LOCK:
        d = _sess_load()
    if d.get("__broken__") and PATH.exists():
        return {"id": "", "role": "gone", "perms": {}, "personal_brain": ""}   # unreadable: fail closed
    uid = d.get(_digest(token)) if token else None
    uid = uid or ((cfgmod.SESSION_META.get(token) or {}).get("user") if token else None)
    if not uid or uid == "owner":
        return OWNER
    u = get(uid)
    if not u or u.get("disabled"):
        return {"id": uid, "role": "gone", "perms": {}, "personal_brain": ""}
    return u


def end_sessions(uid: str) -> int:
    with _LOCK:
        d = _sess_load()
    mine = {k for k, v in d.items() if v == uid}
    toks = [t for t, m in list(cfgmod.SESSION_META.items()) if (m or {}).get("user") == uid]
    toks += [t for t in list(cfgmod.SESSIONS) if _digest(t) in mine and t not in toks]
    for t in toks:
        cfgmod.drop_session(t)
    return len(toks)


# ---------------------------------------------------------------- quyền
def is_owner(u: dict) -> bool:
    return (u or OWNER).get("role") == "owner"


def is_admin(u: dict) -> bool:
    """Chủ hoặc toàn quyền: không bị chặn gì (trừ quản lý người dùng, xem is_owner)."""
    return (u or OWNER).get("role") in ("owner", "full")


def _norm(p: str) -> str:
    try:
        return str(Path(p).resolve()).lower() if p else ""
    except Exception:  # noqa: BLE001
        return str(p).lower()


def brain_level(u: dict, brain_path: str) -> Optional[str]:
    """"write" | "read" | None cho một bộ não (đường dẫn thư mục)."""
    u = u or OWNER
    if is_admin(u):
        return "write"
    if u.get("role") != "limited":
        return None
    b = _norm(brain_path)
    if b and b == _norm(u.get("personal_brain") or ""):
        return "write"
    for k, v in ((u.get("perms") or {}).get("brains") or {}).items():
        if _norm(k) == b:
            return v
    return None


def brains_allowed(u: dict) -> dict:
    """{đường dẫn: mức} của mọi bộ não người này vào được (không dùng cho admin: admin vào hết)."""
    out = {}
    if (u or {}).get("personal_brain"):
        out[u["personal_brain"]] = "write"
    for k, v in ((u.get("perms") or {}).get("brains") or {}).items():
        out.setdefault(k, v)
    return out


def can_agent(u: dict, brain_path: str, slug: str) -> bool:
    u = u or OWNER
    if is_admin(u):
        return True
    if brain_level(u, brain_path) is None:
        return False
    if _norm(brain_path) == _norm(u.get("personal_brain") or ""):
        return True
    for k, v in ((u.get("perms") or {}).get("agents") or {}).items():
        if _norm(k) == _norm(brain_path):
            return "*" in v or slug in v
    return False


def channels_allowed(u: dict) -> Optional[set]:
    """None = mọi kênh (admin); set = chỉ các tài khoản kênh này."""
    u = u or OWNER
    if is_admin(u):
        return None
    return set((u.get("perms") or {}).get("channels") or [])


def outside_actions(u: dict) -> bool:
    """AI được hành động ra ngoài (gửi tin, tạo đơn qua kết nối) khi người này chat."""
    u = u or OWNER
    return is_admin(u) or bool((u.get("perms") or {}).get("outside"))


# Trang của dashboard một người "limited" thấy. Trang quản trị (mô hình, thiết lập, ứng dụng, tiện ích, chợ, dòng
# lệnh, phiên bản, phiên đăng nhập, webhook...) không bao giờ có ở đây; máy chủ cũng chặn route của chúng.
LIMITED_PAGES = ("chat", "home", "files", "workspace", "skills", "account")


def pages(u: dict) -> Optional[list]:
    """None = mọi trang; list = chỉ các trang này."""
    u = u or OWNER
    if is_admin(u):
        return None
    p = list(LIMITED_PAGES)
    if channels_allowed(u):
        p.append("conversations")
    return p
