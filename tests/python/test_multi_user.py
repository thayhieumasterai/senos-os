"""Multi-user workspaces (2026-11-22): added users, roles, and the server-side guard (users.py, users_guard.py).

    python tests/run.py multi_user      (no network)

The owner adds a "limited" user and a "full" user. This pins:
1. both sign in at the same /auth/login, each session knows who it is, /auth/status says role and pages;
2. a limited user gets a personal brain, sees only granted brains, reads a "read" brain but cannot write it, cannot
   reach a brain nobody granted, nor any admin route (models, settings, terminal, users...);
3. their chats are their own (list and direct access), and the owner still sees them;
4. agents and the inbox are filtered to what was granted;
5. a full user passes everything except the owner-only routes;
6. seats: SENOS_CLOUD_LIMITS max_users caps how many can be added;
7. the chat-turn permission level follows the brain level, and the hub hides the shell and owner-only tools.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import json
import os
import tempfile
from pathlib import Path

_ST = tempfile.mkdtemp(prefix="senos-multi-user-test-")
os.environ["SENOS_STATE_DIR"] = _ST
os.environ["BRAINS_DIR"] = str(Path(_ST) / "brains")       # never the repo's own brains/ folder
os.environ["SENOS_REQUIRE_LOGIN"] = "1"
os.environ.pop("SENOS_ADMIN_PASSWORD", None)
_LIM = Path(_ST) / "cloud_limits.json"
_LIM.write_text(json.dumps({"max_channels": None, "max_users": 2}), encoding="utf-8")
os.environ["SENOS_CLOUD_LIMITS"] = str(_LIM)

from fastapi.testclient import TestClient   # noqa: E402
import config as c   # noqa: E402
import main          # noqa: E402
import users         # noqa: E402

_fails = []


def check(name, cond, extra=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond or not extra else f"  [{extra}]"))
    if not cond:
        _fails.append(name)


def client():
    return TestClient(main.app, client=("127.0.0.1", 50000), base_url="http://localhost:7777")


owner = client()
r = owner.post("/auth/setup", data={"username": "chu", "password": "matkhau-chu-123"})
check("owner account set up", r.status_code == 200, r.text[:200])

# brains: the owner's default, a shared one, a secret one
shared = owner.post("/brains/new", data={"name": "Chung"}).json()
secret = owner.post("/brains/new", data={"name": "BiMat"}).json()
check("two extra brains", shared.get("ok") and secret.get("ok"))
(Path(shared["path"]) / "agents").mkdir(exist_ok=True)
for slug in ("ban-hang", "ke-toan"):
    (Path(shared["path"]) / "agents" / f"{slug}.md").write_text(f"---\nname: {slug}\n---\nbody\n", encoding="utf-8")
(Path(shared["path"]) / "note.md").write_text("# shared note\n", encoding="utf-8")
(Path(secret["path"]) / "secret.md").write_text("# secret\n", encoding="utf-8")

# ---- 1. add users
r = owner.post("/users", json={"username": "lan", "password": "matkhau-lan-1", "name": "Lan", "role": "limited",
                               "perms": {"brains": {shared["path"]: "read"}, "agents": {shared["path"]: ["ban-hang"]},
                                         "channels": ["acc-allowed"], "outside": False}})
check("owner adds a limited user", r.status_code == 200 and r.json().get("ok"), r.text[:300])
lan = r.json().get("user") or {}
check("the limited user got a personal brain folder", bool(lan.get("personal_brain")) and Path(lan["personal_brain"]).is_dir())
r = owner.post("/users", json={"username": "minh", "password": "matkhau-minh-1", "name": "Minh", "role": "full"})
check("owner adds a full user", r.status_code == 200 and r.json().get("ok"), r.text[:200])
r = owner.post("/users", json={"username": "thu3", "password": "matkhau-thu3-1", "role": "limited"})
check("seats: a third user is refused when max_users is 2", r.status_code == 400 and "tối đa 2" in r.json().get("error", ""), r.text[:200])
check("seats reported", owner.get("/users").json().get("seats") == {"used": 2, "max": 2, "left": 0})

L = client()
r = L.post("/auth/login", data={"username": "lan", "password": "matkhau-lan-1"})
check("limited user signs in at /auth/login", r.status_code == 200 and r.json().get("ok"), r.text[:200])
st = L.get("/auth/status").json()
check("status: role limited, own pages only", st.get("user", {}).get("role") == "limited" and "chat" in st.get("pages", [])
      and "models" not in st.get("pages", []), st)
check("status: the inbox page comes with a granted channel", "conversations" in st.get("pages", []))
check("owner status says owner", owner.get("/auth/status").json().get("is_owner") is True)
check("wrong password refused", client().post("/auth/login", data={"username": "lan", "password": "nope-nope"}).status_code == 401)

# ---- 2. brains
names = {b["path"] for b in L.get("/brains").json().get("brains", [])}
check("brain list: personal + granted only", lan["personal_brain"] in names and shared["path"] in names
      and secret["path"] not in names, names)
r = L.get("/files/list", params={"brain": shared["path"]})
check("can read a 'read' brain", r.status_code == 200, r.text[:200])
r = L.post("/files/write", data={"brain": shared["path"], "path": "x.md", "content": "hi"})
check("cannot write a 'read' brain", r.status_code == 403, r.text[:200])
r = L.get("/files/list", params={"brain": secret["path"]})
check("cannot reach an ungranted brain", r.status_code == 403, r.text[:200])
r = L.get("/files/list", params={"brain": "path:" + secret["path"]})
check("nor through a path: alias", r.status_code == 403)
r = L.get("/files/list")
check("no brain named = the personal brain (allowed)", r.status_code == 200, r.text[:200])
r = L.post("/files/write", data={"path": "mine.md", "content": "my note"})
check("writes go to the personal brain", r.status_code == 200 and (Path(lan["personal_brain"]) / "mine.md").is_file(),
      r.text[:200])
check("the owner's default brain got nothing", not (main._DEFAULT_BRAIN_DIR.get() / "mine.md").exists())

# ---- admin routes
_st = L.get("/settings")
_txt = _st.text.lower()
check("limited: settings read is the trimmed view, no credential fields", _st.status_code == 200
      and not any(w in _txt for w in ("api_key", "_key\"", "token", "secret", "telegram", "zalo_oa")), _st.text[:200])
for path, method in (("/settings", "POST"), ("/providers/save", "POST"), ("/mcp/connections", "GET"),
                     ("/users", "GET"), ("/auth/tokens", "GET"), ("/brains/new", "POST"), ("/update/apply", "POST"),
                     ("/plugins", "GET"), ("/auth/2fa/start", "POST")):
    r = L.request(method, path)
    check(f"limited: {method} {path} refused", r.status_code in (401, 403), f"{r.status_code} {r.text[:80]}")
try:
    with L.websocket_connect("/ws/terminal") as ws:
        ws.receive_text()
    check("limited: terminal socket refused", False)
except Exception:  # noqa: BLE001
    check("limited: terminal socket refused", True)

# ---- 3. chats
store = main.get_store()
users.CURRENT.set(users.get(lan["id"]))
mine = store.create_session(brain=lan["personal_brain"], title="cua lan")
users.CURRENT.set(users.OWNER)
theirs = store.create_session(brain="brain", title="cua chu")
_j = L.get("/sessions").json()
lst = {s["id"] for s in (_j.get("sessions") if isinstance(_j, dict) else _j)}
check("chat list: own chats only", mine in lst and theirs not in lst, lst)
check("cannot open another person's chat", L.get(f"/sessions/{theirs}/messages").status_code == 403)
check("can open own chat", L.get(f"/sessions/{mine}/messages").status_code == 200)
ol = owner.get("/sessions").json()
ol = {s["id"] for s in (ol.get("sessions") if isinstance(ol, dict) else ol)}
check("the owner still sees everyone's chats", mine in ol and theirs in ol)
users.CURRENT.set(users.get(lan["id"]))
check("socket: another's chat refused", main._ws_denied({"session_id": theirs, "brain": ""}) != "")
check("socket: an ungranted brain refused", main._ws_denied({"brain": secret["path"]}) != "")
check("socket: own chat in own brain allowed", main._ws_denied({"session_id": mine, "brain": ""}) == "")
check("socket: an ungranted agent refused", main._ws_denied({"brain": shared["path"], "agent": "ke-toan"}) != "")

# ---- 7. turn level and hub tools
check("turn level in a 'read' brain is suggest", main._muc_quyen_luot_chat({"brain": shared["path"]}) == "suggest")
check("turn level in the personal brain is auto (no outside actions)",
      main._muc_quyen_luot_chat({"brain": lan["personal_brain"]}) == "auto")
import asyncio  # noqa: E402
import mcp_hub  # noqa: E402
spec, route = asyncio.run(mcp_hub.discover_all("full", vault_root=lan["personal_brain"], include_ambient=False))
names_t = {t.get("fn") for t in spec} | set(route)
check("hub: no shell tools for a limited user", not (names_t & mcp_hub.LIMITED_CAM), names_t & mcp_hub.LIMITED_CAM)
check("hub: no owner-only tools for a limited user", not (names_t & mcp_hub.OWNER_ONLY_TOOLS))
users.CURRENT.set(users.OWNER)

# ---- 4. agents and inbox
ag = L.get("/agents", params={"brain": shared["path"], "prompt": 0}).json().get("agents", [])
slugs = {a.get("slug") or a.get("id") for a in ag}
check("agents: only the granted one", "ban-hang" in slugs and "ke-toan" not in slugs, slugs)
r = L.get("/conversations")
check("inbox list answers", r.status_code == 200, r.text[:200])
check("inbox: a conversation of an ungranted account is refused", L.get("/conversations/999999").status_code == 403)

# ---- 5. full user
F = client()
check("full user signs in", F.post("/auth/login", data={"username": "minh", "password": "matkhau-minh-1"}).status_code == 200)
minh_id = users.by_username("minh")["id"]
check("full user reaches settings", F.get("/settings").status_code != 403)
check("full user reaches the secret brain", F.get("/files/list", params={"brain": secret["path"]}).status_code == 200)
check("full user cannot manage users", F.get("/users").status_code == 403)
check("full user cannot see API tokens", F.get("/auth/tokens").status_code == 403)

# ---- attacks from the security review (2026-11-22)
ltok = L.cookies.get("senos_session")
try:
    with client().websocket_connect("/ws/terminal", headers={"cookie": f"senos_session=bogus; senos_session={ltok}"}) as ws:
        ws.receive_text()
    check("attack: duplicated cookie does not open the terminal", False)
except Exception:  # noqa: BLE001
    check("attack: duplicated cookie does not open the terminal", True)
import users_guard  # noqa: E402
check("attack: the guard reads the cookie the endpoint reads (last one)",
      users_guard._cookie({"headers": [(b"cookie", f"senos_session=bogus; senos_session={ltok}".encode())]}, "senos_session") == ltok)
r = L.post("/files/write", files=[("brain", (None, lan["personal_brain"])), ("brain", (None, secret["path"])),
                                  ("path", (None, "pwned.md")), ("content", (None, "x"))])
check("attack: duplicated multipart brain refused", r.status_code == 403 and not (Path(secret["path"]) / "pwned.md").exists())
r = L.post("/files/write", files=[("pad", (None, "x" * 250000)), ("brain", (None, secret["path"])),
                                  ("path", (None, "pwned2.md")), ("content", (None, "x"))])
check("attack: a brain after 250 KB of padding is still read", r.status_code == 403 and not (Path(secret["path"]) / "pwned2.md").exists())
r = L.post("/share/create", content=json.dumps({"brain": secret["path"], "path": "secret.md"}), headers={"content-type": "text/plain"})
check("attack: JSON without a JSON content type is still read", r.status_code == 403)
r = L.post("/share/chat", json={"session_id": theirs})
check("attack: cannot publish someone else's chat", r.status_code == 403)
check("attack: share list without a brain = own brain only",
      all(i.get("brain") in (None, "", lan["personal_brain"]) for i in L.get("/share/list").json().get("items", [])))
check("attack: POST /chat (owner's CLI turn) refused", L.post("/chat", data={"message": "hi"}).status_code == 403)
check("attack: running a workflow refused", L.get("/workflows/run", params={"brain": shared["path"], "slug": "x"}).status_code == 403)
check("attack: /graph?path= refused", L.get("/graph", params={"path": secret["path"]}).status_code == 403)
check("attack: project by id refused", L.get("/projects/abc").status_code == 403)
check("attack: owner usage refused", L.get("/usage/summary").status_code == 403)
check("full user cannot open the owner's chat", F.get(f"/sessions/{theirs}/messages").status_code == 403)
users.CURRENT.set(users.get(minh_id))
check("full user's chat list leaves out other people's chats", theirs not in {s["id"] for s in store.list_sessions(limit=200)})
users.CURRENT.set(users.OWNER)

# ---- own password
r = L.post("/auth/password", data={"current_password": "matkhau-lan-1", "password": "matkhau-lan-2"})
check("a user changes their own password", r.status_code == 200, r.text[:200])
check("the owner's password is untouched", c.verify_password("matkhau-chu-123"))

# ---- disable and delete
uid_lan = lan["id"]
owner.post(f"/users/{uid_lan}", json={"disabled": True})
check("a disabled user's session ends", L.get("/auth/status").json().get("authed") is False)
check("a disabled user cannot sign in", client().post("/auth/login", data={"username": "lan", "password": "matkhau-lan-2"}).status_code == 401)
check("delete works", owner.post(f"/users/{uid_lan}/delete").json().get("ok"))
check("seat freed", owner.get("/users").json()["seats"]["used"] == 1)

print("\nOK - test_multi_user" if not _fails else f"\nFAIL - test_multi_user: {len(_fails)}: {_fails}")
raise SystemExit(1 if _fails else 0)
