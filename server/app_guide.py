"""`senos_app_guide`: what SenOS's own screens are called today and what the user guides say about them.

The assistant used to answer "where is X" from the brain alone, which knows nothing about the app, so it guessed menu
names (2026-11-26: it sent a user to "Cài đặt" for the model, a page that is called "Thiết lập" and is not where the
model is). This reads the truth from the app itself:

- the sidebar: groups and pages in screen order from `dashboard/console.js` (RAIL_TOP, RAIL_GROUPS), each label and
  subtitle from `dashboard/i18n/<lang>.json`, so a renamed page is renamed here with no second list to keep in step;
- the user guides: `docs/*.md` (Vietnamese) or `docs/en/*.md` (English), cut at their headings and ranked against
  the question by word overlap (accents folded, so "cai dat" finds "cài đặt").

Read only, nothing leaves the machine. Results are cached until a source file changes.
"""
from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

import lang_registry

ROOT = Path(__file__).resolve().parent.parent
DASH = ROOT / "dashboard"
DOCS = ROOT / "docs"
MAX_HITS = 3
HIT_CHARS = 2500
_cache: dict = {}

# Words too common to rank a guide section by.
_STOP = set("""và của là có cho các một những được trong với không này đó để khi thì ở trên dưới ra vào tôi bạn mình
em anh chị nó gì sao nào đâu làm thế như cách hay hoặc rồi đã sẽ đang thể muốn cần the a an of to in on for and or is
are be it how what where do does can i my you your with from at this that which page trang mục nút""".split())


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


_STOP_FOLDED: set = set()


def _words(s: str) -> list:
    return [w for w in re.findall(r"[a-z0-9]+", _fold(s)) if len(w) > 1 and w not in _STOP_FOLDED]


_STOP_FOLDED.update(_fold(w) for w in _STOP)


# Each language SenOS ships a user guide in, and where it is. Labels come from dashboard/i18n/<code>.json.
_GUIDE_DIRS = {"vi": DOCS, "en": DOCS / "en"}
_TEXT = {
    "head": {"vi": "Thanh bên của SenOS, từ trên xuống (dùng đúng các tên này):",
             "en": "SenOS sidebar, top to bottom (use these exact names):"},
    "foot": {"vi": " (ghim ở đáy)", "en": " (pinned at the bottom)"},
    "hidden": {"vi": "Trang không nằm trên thanh bên (mở từ liên kết trong trang khác): ",
               "en": "Pages not on the sidebar (opened from links inside other pages): "},
    "guides": {"vi": "Các bài hướng dẫn (hỏi lại kèm câu hỏi để đọc): ",
               "en": "User guides (ask again with a question to read one): "},
    "nohit": {"vi": "Không có đoạn hướng dẫn nào khớp. Chỉ trả lời theo thanh bên ở trên, và nói rõ chỗ chưa xác nhận được.",
              "en": "No guide section matches. Answer from the sidebar above only, and say what you could not confirm."},
    "lag": {"vi": "Hướng dẫn có thể chậm hơn giao diện: chỗ nào tên trong hướng dẫn khác thanh bên ở trên thì theo thanh bên.",
            "en": "Guides can lag behind the screen: where a guide and the sidebar above disagree on a name, the sidebar is right."},
}


def _lang(lang: str) -> str:
    """The language whose labels and guides to use: the asked one when SenOS ships a guide in it, else the fallback."""
    return lang_registry.chon_ban_dich(lang or lang_registry.MAC_DINH, {code: code for code in _GUIDE_DIRS})


def _say(lang: str, key: str) -> str:
    return lang_registry.chon_ban_dich(lang or lang_registry.MAC_DINH, _TEXT[key])


def _stamp(*paths) -> tuple:
    out = []
    for p in paths:
        try:
            out.append(p.stat().st_mtime_ns)
        except OSError:
            out.append(0)
    return tuple(out)


def _strings(lang: str) -> dict:
    try:
        return json.loads((DASH / "i18n" / f"{lang}.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def rail() -> dict:
    """{'top': [page ids], 'groups': [{id, pages, foot}], 'hidden': [page ids]} read from console.js."""
    src = DASH / "console.js"
    key = ("rail", _stamp(src))
    if key in _cache:
        return _cache[key]
    try:
        js = src.read_text(encoding="utf-8")
    except OSError:
        js = ""
    ids = lambda s: re.findall(r'"([a-z_]+)"', s)  # noqa: E731
    top = re.search(r"const RAIL_TOP\s*=\s*\[([^\]]*)\]", js)
    hidden = re.search(r"const RAIL_AN\s*=\s*new Set\(\[([^\]]*)\]", js)
    block = re.search(r"const RAIL_GROUPS\s*=\s*\[(.*?)\n\s*\];", js, re.S)
    groups = []
    for m in re.finditer(r'\{\s*id:\s*"([a-z_]+)".*?ids:\s*\[([^\]]*)\]([^}]*)\}', block.group(1) if block else "", re.S):
        groups.append({"id": m.group(1), "pages": ids(m.group(2)), "foot": "foot: true" in m.group(3)})
    out = {"top": ids(top.group(1)) if top else [], "groups": groups, "hidden": ids(hidden.group(1)) if hidden else []}
    _cache[key] = out
    return out


def page_map(lang: str = "") -> str:
    lang = _lang(lang)
    t, r = _strings(lang), rail()
    label = lambda pid: t.get(f"page.{pid}.label") or pid  # noqa: E731

    def line(pid):
        sub = (t.get(f"page.{pid}.sub") or "").strip()
        return f"- {label(pid)}" + (f": {sub}" if sub else "")

    out = [_say(lang, "head")]
    out += [line(p) for p in r["top"]]
    for g in r["groups"]:
        name = t.get(f"nav.group.{g['id']}") or g["id"]
        where = _say(lang, "foot") if g["foot"] else ""
        out.append(f"{name}{where}:")
        out += ["  " + line(p) for p in g["pages"]]
    if r["hidden"]:
        out.append(_say(lang, "hidden") + ", ".join(label(p) for p in r["hidden"]))
    return "\n".join(out)


def _guide_files(lang: str) -> list:
    base = _GUIDE_DIRS.get(lang, DOCS)
    return sorted(p for p in base.glob("[0-9][0-9]-*.md"))


def _sections(lang: str) -> list:
    files = _guide_files(lang)
    key = ("sec", lang, _stamp(*files))
    if key in _cache:
        return _cache[key]
    out = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), f.stem)
        for part in re.split(r"\n(?=#{2,3} )", text):
            head = part.split("\n", 1)[0].lstrip("#").strip() if part.startswith("#") else title
            body = part.strip()
            if len(body) < 40:
                continue
            toks = _words(head + " " + body)
            out.append({"file": f.relative_to(DOCS).as_posix(), "guide": title,
                        "heading": head, "text": body, "tf": Counter(toks), "len": len(toks),
                        "pairs": set(zip(toks, toks[1:])), "head_words": set(_words(head + " " + title))})
    _cache[key] = out
    return out


def search(query: str, lang: str = "") -> list:
    """BM25 over guide sections: rare words count most, a long section does not win by size, a word in the heading
    counts again, and two query words found side by side count again (Vietnamese words are single syllables, so
    "bản đồ" or "đổi model" mean more together than apart)."""
    words = list(dict.fromkeys(_words(query)))
    if not words:
        return []
    secs = _sections(_lang(lang))
    n = len(secs) or 1
    avg = sum(s["len"] for s in secs) / n or 1
    idf = {w: math.log(1 + (n - df + 0.5) / (df + 0.5))
           for w in words for df in [sum(1 for s in secs if w in s["tf"])]}
    order = _words(query)
    pairs = list(zip(order, order[1:]))
    scored = []
    for s in secs:
        score = 0.0
        for w in words:
            f = s["tf"].get(w, 0)
            if f:
                score += idf[w] * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * s["len"] / avg))
            if w in s["head_words"]:
                score += idf[w]
        score += sum(idf[a] + idf[b] for a, b in pairs if (a, b) in s["pairs"])
        if score > 0:
            scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[0][0] if scored else 0
    return [s for score, s in scored[:MAX_HITS] if score >= top * 0.5]


def guide(query: str = "", lang: str = "") -> str:
    lang = _lang(lang)
    out = [page_map(lang)]
    query = (query or "").strip()
    if not query:
        titles = sorted({s["guide"] for s in _sections(lang)})
        out.append(_say(lang, "guides") + "; ".join(titles))
        return "\n\n".join(out)
    hits = search(query, lang)
    if not hits:
        out.append(_say(lang, "nohit"))
    for s in hits:
        text = s["text"] if len(s["text"]) <= HIT_CHARS else s["text"][:HIT_CHARS] + " …"
        out.append(f"--- {s['guide']} > {s['heading']} (docs/{s['file']})\n{text}")
    out.append(_say(lang, "lag"))
    return "\n\n".join(out)
