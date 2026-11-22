"""Lớp chặn quyền theo người dùng (2026-11-22), chạy SAU lớp xác thực trong main.py.

Chỉ chạm tới người không phải chủ:
- full    : qua hết, trừ các đường chỉ CHỦ được dùng (quản lý người dùng, 2FA, token API, thiết bị đăng nhập...), và
            chat của người khác (mỗi người thấy cuộc trò chuyện của mình, chủ thấy tất cả).
- limited : CHẶN MẶC ĐỊNH. Chỉ các đường trong ALLOW mới qua, và đi qua thêm các lớp kiểm:
    1. bộ não: mọi `brain` / `brain_name` / `/brains/<x>/...` (và `source` của /graph) trong URL, thân JSON hay form
       phải là bộ não người đó vào được; đổi dữ liệu (không phải GET) cần mức "write";
    2. Agent: `slug` / `agent` của các đường /agents, /resonance/agents phải là Agent được cấp;
    3. chat: `session` / `session_id` và /sessions/<id> phải là chat của chính người đó;
    4. kênh: /conversations/<id> phải thuộc một tài khoản kênh được cấp (danh sách bị ép về đúng các kênh đó).
Ẩn trang trên giao diện là cho gọn mắt; chặn thật là ở đây.

Đọc tham số theo ĐÚNG cách route đọc (bản rà bảo mật 2026-11-22): cookie trùng tên thì lấy cái cuối như Starlette;
form multipart đọc trọn bằng chính bộ phân tích của Starlette, mọi giá trị của mọi trường; thân trông như JSON thì đọc
dù content-type nói gì. Lệch một chỗ là route nhận giá trị khác giá trị đã kiểm.

Pure ASGI (không phải BaseHTTPMiddleware) vì phải đọc thân request rồi trả lại nguyên vẹn cho route.
"""
from __future__ import annotations

import json
import re
from typing import Callable, Optional
from urllib.parse import parse_qs, urlencode

import config as cfgmod
import users

# Đường chỉ CHỦ dùng được (kể cả "full" cũng không).
OWNER_ONLY = ("/users", "/auth/2fa", "/auth/disable", "/auth/tokens", "/auth/security", "/auth/sessions",
              "/auth/setup", "/auth/reset-help/open", "/profile")

# limited: (tiền tố, các method được phép). "*" = mọi method. Tiền tố kết thúc bằng "/" khớp cả cây con; không có "/"
# cuối thì khớp đúng đường đó và cây con của nó.
_GET = ("GET", "HEAD")
ALLOW = [
    # khung trang, tài nguyên tĩnh, thông tin chung không có bí mật
    ("/", _GET), ("/static/", _GET), ("/sw.js", _GET), ("/brand-theme.css", _GET), ("/brand-logo", _GET),
    ("/pet-icon", _GET), ("/favicon.ico", _GET), ("/robots.txt", _GET), ("/manifest", _GET), ("/config", _GET),
    ("/version", _GET), ("/app-version", _GET), ("/health", _GET), ("/changelog", _GET), ("/avatars/", _GET),
    ("/providers", _GET), ("/model/fast-state", _GET), ("/plan-limits", _GET), ("/runtime/muc", _GET),
    ("/runtime/prompt-size", _GET), ("/claude/status", _GET), ("/voice/options", _GET), ("/voice/brain-models", _GET),
    ("/tts", _GET), ("/ui/order", _GET), ("/pet/menu", _GET), ("/senos-core/model", _GET), ("/chat/route", _GET),
    ("/chat/plan", _GET), ("/chat/suggest", _GET), ("/slash/status", _GET), ("/lint", _GET), ("/vault/check", _GET),
    ("/brains/ties", _GET), ("/client-errors", ("POST",)), ("/seen", "*"), ("/settings", _GET),
    ("/provider/models", _GET), ("/voice/ear", _GET), ("/voice/call", _GET), ("/graph", _GET),
    ("/batch", ("POST",)), ("/diag/ws-drops", ("POST",)), ("/star-nudge/check", ("POST",)),
    # đăng nhập của chính mình
    ("/auth/status", "*"), ("/auth/logout", "*"), ("/auth/password", "*"), ("/auth/login", "*"),
    # trò chuyện với Sen: CHỈ qua khung chat (WebSocket /ws, khoá công cụ theo người). POST /chat, /chat/stream và
    # /chat/jobs là đường của CLI và token API, chạy lượt của chủ, nên không có ở đây.
    ("/stop", "*"), ("/sessions", "*"), ("/stt", "*"), ("/image/generate", "*"),
    ("/ws", "*"), ("/ws/voice-live", "*"), ("/ws/graph", "*"),
    # tài liệu và tri thức trong bộ não được cấp
    ("/files/", "*"), ("/upload", ("POST",)), ("/ingest-upload", "*"), ("/memory/", "*"), ("/brains", _GET),
    ("/brains/", _GET), ("/projects", _GET), ("/share/create", ("POST",)), ("/share/of", _GET),
    ("/share/list", _GET), ("/share/chat", "*"), ("/share/qr", _GET),
    # năng lực trong bộ não được cấp (xem, sửa; CHẠY quy trình thì không, xem DENY)
    ("/agents", "*"), ("/resonance/agents", "*"), ("/skills", "*"), ("/workflows", "*"),
    # Hộp thư bot của các kênh được cấp
    ("/conversations", "*"),
]
# Trong các tiền tố cho phép ở trên, những đường này vẫn là của chủ: chạy lệnh trên máy, mở tệp ngoài bộ não, chạy
# quy trình hay việc nền (chúng chạy với quyền của chủ), số liệu toàn workspace.
DENY = ("/ws/terminal", "/files/open-local", "/brains/export", "/brains/import", "/agents/import",
        "/conversations/zalo/", "/conversations/tags/", "/conversations/insights", "/conversations/stats",
        "/workflows/run", "/workflows/resume", "/workflows/runs", "/upload/raw", "/projects/")
DENY_RX = re.compile(r"^/agents/[^/]+/(jobs|pulse|team|schedule)(/|$)")
# Đường "đổi dữ liệu" mà vẫn cho chạy ở bộ não chỉ đọc: chat (AI tự bị hạ xuống mức chỉ đọc), tìm kiếm.
CHAT_LIKE = ("/stop", "/sessions", "/stt", "/files/search", "/memory/items", "/share/chat")
# Danh sách không ghi bộ não thì trả MỌI bộ não; với người "limited" thì thiếu bộ não = bộ não riêng.
LIST_NEEDS_BRAIN = ("/share/list", "/projects", "/graph", "/ws/graph", "/files/search", "/memory/items")

BRAIN_KEYS = ("brain", "brain_name")
AGENT_KEYS = ("slug", "agent", "agent_slug")
SESSION_KEYS = ("session", "session_id")
_ALL_KEYS = BRAIN_KEYS + AGENT_KEYS + SESSION_KEYS + ("source", "path", "account_ids", "account_id")
_SESSION_WORDS = ("new", "search", "pin-order", "unread-summary")


def _match(path: str, prefix: str) -> bool:
    if prefix == "/":
        return path == "/"
    if prefix.endswith("/"):
        return path.startswith(prefix)
    return path == prefix or path.startswith(prefix + "/")


def owner_only(path: str) -> bool:
    return any(_match(path, p) for p in OWNER_ONLY)


def limited_allows(path: str, method: str) -> bool:
    if any(_match(path, d) for d in DENY) or DENY_RX.match(path):
        return False
    for prefix, methods in ALLOW:
        if _match(path, prefix) and (methods == "*" or method in methods):
            return True
    return False


def identify(scope) -> dict:
    """Who a WebSocket is, read exactly as the endpoint reads it (Starlette keeps the LAST duplicate cookie).
    A cookie that is there but not valid is never the owner while sign-in is on."""
    tok = _cookie(scope, "senos_session")
    if tok and cfgmod.valid_session(tok):
        return users.session_user(tok)
    if not cfgmod.gate_active():
        return users.OWNER
    return {"id": "", "role": "gone", "perms": {}, "personal_brain": ""}


class UserGuard:
    """ASGI middleware. `resolve_brain(name) -> path` dùng đúng cách main.py chọn bộ não; `conv_account(id)` trả id
    tài khoản kênh của một hội thoại (hoặc None); `session_owner(id)` trả "owner" | id người dùng | None."""

    def __init__(self, app, resolve_brain: Callable[[str], str], conv_account: Callable[[str], Optional[str]],
                 session_owner: Callable[[str], Optional[str]] = lambda s: None):
        self.app = app
        self.resolve_brain = resolve_brain
        self.conv_account = conv_account
        self.session_owner = session_owner

    async def __call__(self, scope, receive, send):
        if scope.get("type") not in ("http", "websocket"):
            return await self.app(scope, receive, send)
        if scope["type"] == "websocket":
            # @app.middleware("http") never sees a WebSocket, so the auth guard did not say who this is.
            users.CURRENT.set(identify(scope))
        u = users.CURRENT.get()
        if users.is_owner(u):
            return await self.app(scope, receive, send)
        path = scope.get("path") or "/"
        method = scope.get("method", "GET") if scope["type"] == "http" else "GET"
        if u.get("role") == "gone":
            return await _deny(scope, send, 401, "Tài khoản này đã bị gỡ hoặc tạm khoá.")
        if owner_only(path):
            return await _deny(scope, send, 403, "Chỉ chủ workspace dùng được mục này.")
        limited = not users.is_admin(u)
        if limited and not limited_allows(path, method):
            return await _deny(scope, send, 403, "Tài khoản của bạn chưa được cấp quyền dùng mục này.")
        body = b""
        if scope["type"] == "http" and method not in _GET:
            body, receive = await _buffer(receive)
        params = await _params(scope, body)

        # chats: everyone but the owner sees only their own (full users too)
        sids = [v for k in SESSION_KEYS for v in params.get(k, [])]
        seg = path.split("/")
        if path.startswith("/sessions/") and len(seg) > 2 and seg[2] not in _SESSION_WORDS:
            sids.append(seg[2])
        for sid in sids:
            if sid and self.session_owner(sid) not in (None, u.get("id")):
                return await _deny(scope, send, 403, "Cuộc trò chuyện này không phải của bạn.")
        if not limited:
            return await self.app(scope, _replay(body, receive) if body else receive, send)

        # ---- limited
        # 1. bộ não
        graph = path.startswith(("/graph", "/ws/graph"))
        if graph and params.get("path"):
            return await _deny(scope, send, 403, "Bản đồ chỉ mở được bộ não bạn được cấp.")
        brains = [v for k in BRAIN_KEYS + (("source",) if graph else ()) for v in params.get(k, [])]
        if path.startswith("/brains/") and path.count("/") >= 3:
            brains.append(path.split("/")[2])
        if not brains and any(_match(path, p) for p in LIST_NEEDS_BRAIN):
            own = u.get("personal_brain") or ""
            _set_query(scope, "source" if graph else "brain", own)
            brains = [own]
        if graph and any(b in ("all", "vault", "") for b in brains):
            return await _deny(scope, send, 403, "Bản đồ chỉ mở được bộ não bạn được cấp.")
        mutating = method not in _GET and not any(_match(path, c) for c in CHAT_LIKE)
        for b in brains:
            lv = users.brain_level(u, self.resolve_brain(b))
            if lv is None:
                return await _deny(scope, send, 403, "Bạn chưa được cấp quyền vào bộ não này.")
            if mutating and lv != "write":
                return await _deny(scope, send, 403, "Bộ não này bạn chỉ được xem.")
        # 2. Agent
        if path.startswith("/agents") or path.startswith("/resonance/agents"):
            slugs = [v for k in AGENT_KEYS for v in params.get(k, [])]
            if path.startswith("/agents/") and len(seg) > 2 and seg[2] not in ("", "import", "groups", "tags"):
                slugs.append(seg[2])
            real = self.resolve_brain(brains[0] if brains else "")
            for s in slugs:
                if s and not users.can_agent(u, real, s):
                    return await _deny(scope, send, 403, "Bạn chưa được cấp quyền điều khiển Agent này.")
        # 3. kênh: the list only ever covers the granted accounts (none granted = nothing)
        if path == "/conversations" and scope["type"] == "http":
            allowed = sorted(users.channels_allowed(u) or set())
            asked = [a for v in params.get("account_ids", []) for a in v.split(",") if a.strip()]
            keep = [a for a in asked if a in allowed] if asked else allowed
            _set_query(scope, "account_ids", ",".join(keep) or "__none__")
            _set_query(scope, "account_id", "")
        if path == "/conversations/tags" and method not in _GET:
            return await _deny(scope, send, 403, "Chỉ chủ workspace sửa được danh sách tag.")
        if path.startswith("/conversations/"):
            cid = seg[2]
            allowed = users.channels_allowed(u) or set()
            if cid not in ("insights", "stats", "channels") and self.conv_account(cid) not in allowed:
                return await _deny(scope, send, 403, "Hội thoại này thuộc kênh bạn chưa được cấp.")
        return await self.app(scope, _replay(body, receive) if body else receive, send)


def _cookie(scope, name: str) -> str:
    from starlette.requests import cookie_parser
    raw = "; ".join(v.decode("latin-1") for k, v in (scope.get("headers") or []) if k == b"cookie")
    return cookie_parser(raw).get(name, "") if raw else ""


def _set_query(scope, key: str, value: str) -> None:
    q = parse_qs((scope.get("query_string") or b"").decode("latin-1"), keep_blank_values=True)
    q.pop(key, None)
    if value:
        q[key] = [value]
    scope["query_string"] = urlencode(q, doseq=True).encode("latin-1")


async def _params(scope, body: bytes) -> dict:
    """Every value of the keys the guard checks, from the query, the JSON body and the form, all duplicates kept."""
    out: dict = {}
    for k, v in parse_qs((scope.get("query_string") or b"").decode("latin-1"), keep_blank_values=True).items():
        out.setdefault(k, []).extend(v)
    if not body:
        return out
    ctype = ""
    for k, v in scope.get("headers") or []:
        if k == b"content-type":
            ctype = v.decode("latin-1").lower()
    stripped = body.lstrip()[:1]
    if stripped in (b"{", b"["):
        try:
            d = json.loads(body.decode("utf-8"))
            for item in (d if isinstance(d, list) else [d]):
                if isinstance(item, dict):
                    for k in _ALL_KEYS:
                        v = item.get(k)
                        if isinstance(v, (str, int)):
                            out.setdefault(k, []).append(str(v))
                        elif isinstance(v, list):
                            out.setdefault(k, []).extend(str(x) for x in v if isinstance(x, (str, int)))
        except Exception:  # noqa: BLE001
            pass
    if "multipart/form-data" in ctype or "x-www-form-urlencoded" in ctype:
        try:
            from starlette.requests import Request
            req = Request(scope, _replay(body, None))
            form = await req.form(max_files=1000, max_fields=10000)
            try:
                for k in _ALL_KEYS:
                    for v in form.getlist(k):
                        if isinstance(v, str):
                            out.setdefault(k, []).append(v)
            finally:
                await form.close()
        except Exception:  # noqa: BLE001
            out.setdefault("brain", []).append("\x00unreadable")   # a body the guard cannot read is refused
    return out


async def _buffer(receive):
    chunks, more = [], True
    while more:
        msg = await receive()
        if msg["type"] != "http.request":
            break
        chunks.append(msg.get("body", b""))
        more = msg.get("more_body", False)
    return b"".join(chunks), receive


def _replay(body: bytes, receive):
    sent = [False]

    async def replay():
        if not sent[0]:
            sent[0] = True
            return {"type": "http.request", "body": body, "more_body": False}
        if receive is None:
            return {"type": "http.disconnect"}
        return await receive()
    return replay


async def _deny(scope, send, status: int, msg: str):
    if scope["type"] == "websocket":
        await send({"type": "websocket.close", "code": 4403})
        return
    data = json.dumps({"ok": False, "error": msg, "forbidden": True}, ensure_ascii=False).encode("utf-8")
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json; charset=utf-8"),
                            (b"content-length", str(len(data)).encode())]})
    await send({"type": "http.response.body", "body": data})
