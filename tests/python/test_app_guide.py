"""senos_app_guide (server/app_guide.py): the assistant answers "where is X in SenOS" from the app itself.

2026-11-26: asked to change the model, the assistant guessed "Cài đặt", a page that is called "Thiết lập" and is not
where models are. The page list must come from what the sidebar really draws, in the user's language, and the tool
must be offered to every brain.
"""
import asyncio
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "server"))
import app_guide  # noqa: E402

failed = []


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else f"  {detail}"))
    if not cond:
        failed.append(name)


vi = json.loads((ROOT / "dashboard/i18n/vi.json").read_text(encoding="utf-8"))
en = json.loads((ROOT / "dashboard/i18n/en.json").read_text(encoding="utf-8"))
rail = app_guide.rail()
pages = rail["top"] + [p for g in rail["groups"] for p in g["pages"]]
check("rail read from console.js: Hội thoại on top, five groups, Admin pinned at the bottom",
      rail["top"] == ["chat"] and len(rail["groups"]) == 5 and rail["groups"][-1]["foot"]
      and "models" in rail["groups"][-1]["pages"], rail)
check("every sidebar page has a label in both languages",
      all(vi.get(f"page.{p}.label") and en.get(f"page.{p}.label") for p in pages), pages)

m_vi, m_en = app_guide.page_map("vi"), app_guide.page_map("en")
for pid in ("home", "models", "settings", "packs", "mcp"):
    check(f"page map names {pid} as the screen does", vi[f"page.{pid}.label"] in m_vi and en[f"page.{pid}.label"] in m_en)
check("old Javis-era names are not in the page map", not re.search(r"Mạng nơ-ron|Javis|Kho cài đặt", m_vi + m_en))
check("the group a page sits in comes before it", m_vi.index(vi["nav.group.he_thong"]) < m_vi.index(vi["page.models.label"]))

hits = app_guide.search("đổi model AI như thế nào", "vi")
check("a Vietnamese question finds how to pick or change the model",
      hits and "model" in hits[0]["heading"].lower() and any("10-models" in h["file"] for h in hits),
      [(h["file"], h["heading"]) for h in hits])
hits = app_guide.search("connect Zalo", "en")
check("an English question reads the English guides", hits and all(h["file"].startswith("en/") for h in hits), hits[:1])
check("accents are folded: 'mat khau' finds the password section",
      any("14-bao-mat" in h["file"] for h in app_guide.search("dat lai mat khau", "vi")))
check("a question with nothing to match returns no section", app_guide.search("là gì", "vi") == [])

out = app_guide.guide("đổi model", "vi")
check("an answer carries the page map, the matching guide and the rule that the sidebar wins",
      m_vi in out and "model" in out.split("--- ", 1)[-1].lower() and "theo thanh bên" in out)
check("no query lists the guides instead", "Các bài hướng dẫn" in app_guide.guide("", "vi"))
check("long sections are cut", all(len(b) <= app_guide.HIT_CHARS + 2000 for b in out.split("\n\n--- ")))

hub = (ROOT / "server/mcp_hub.py").read_text(encoding="utf-8")
check("the hub offers senos_app_guide as a read tool", 'add("senos_app_guide"' in hub and "app_guide.guide" in hub)
check("not owner-only: a bot may answer where things are",
      '"senos_app_guide"' not in hub[hub.index("OWNER_ONLY_TOOLS"):hub.index("def _audit_append")])
prompt = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
check("the system prompt tells the assistant to look it up, not guess", "senos_app_guide" in prompt)


async def via_tool():
    import importlib
    hubmod = importlib.import_module("mcp_hub")
    return hubmod
try:
    asyncio.run(via_tool())
    check("mcp_hub imports with the new tool", True)
except Exception as e:  # noqa: BLE001
    check("mcp_hub imports with the new tool", False, repr(e)[:300])

if failed:
    print(f"\nFAIL {len(failed)} test: " + ", ".join(failed))
    sys.exit(1)
print("\nOK - test_app_guide: tất cả pass")
