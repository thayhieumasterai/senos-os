"""Store pack licenses (2026-11-22): SenOS Cloud does not offer noncommercial packs; cards note restrictive licenses.

    python tests/run.py pack_license      (no network)

The owner sells SenOS Cloud, a paid service, so a pack whose license forbids commercial use (GitNexus, PolyForm
Noncommercial) must not be offered or installed there. Self-hosted SenOS keeps every pack. A vendor's own license
(Remotion License) stays installable everywhere but the card says to read its terms. This pins:
1. pack_license.kind sorts licenses into open / noncommercial / custom;
2. the store catalog keeps the `license` field (packs_store._lam_sach used to drop it);
3. only on the cloud (SENOS_CLOUD_LIMITS) is a noncommercial pack blocked, and the file can turn that off;
4. pack_install.cai refuses a noncommercial pack on the cloud and installs it self-hosted.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import io
import json
import os
import tempfile
import zipfile
from pathlib import Path

_ST = tempfile.mkdtemp(prefix="senos-pack-license-")
os.environ["SENOS_STATE_DIR"] = _ST
os.environ.pop("SENOS_CLOUD_LIMITS", None)

import pack_install   # noqa: E402
import pack_license   # noqa: E402
import packs_store    # noqa: E402

_fails = []


def check(name, cond, them=""):
    print(("ok   " if cond else "FAIL ") + name + (f"  [{them}]" if them and not cond else ""))
    if not cond:
        _fails.append(name)


# ---- 1. kinds ----
for lic, want in (("MIT", "open"), ("Apache-2.0", "open"), ("BSD-3-Clause", "open"), ("", ""),
                  ("PolyForm-Noncommercial-1.0.0", "noncommercial"), ("CC-BY-NC-4.0", "noncommercial"),
                  ("Remotion License", "custom"), ("Proprietary", "custom")):
    check(f"kind({lic!r}) = {want!r}", pack_license.kind(lic) == want, pack_license.kind(lic))

# ---- 2. the catalog keeps the license ----
check("store catalog keeps `license`", packs_store._lam_sach({"id": "javis.x", "license": "Remotion License"})["license"]
      == "Remotion License")

# ---- 3. only the cloud blocks ----
check("self-hosted: noncommercial not blocked", not pack_license.blocked("PolyForm-Noncommercial-1.0.0"))
lim = Path(_ST) / "cloud_limits.json"
lim.write_text(json.dumps({"max_channels": 3}), encoding="utf-8")
os.environ["SENOS_CLOUD_LIMITS"] = str(lim)
check("cloud: noncommercial blocked", pack_license.blocked("PolyForm-Noncommercial-1.0.0"))
check("cloud: custom license still allowed", not pack_license.blocked("Remotion License"))
check("cloud: MIT allowed", not pack_license.blocked("MIT"))
lim.write_text(json.dumps({"hide_noncommercial": False}), encoding="utf-8")
check("cloud file can turn the rule off", not pack_license.blocked("PolyForm-Noncommercial-1.0.0"))
lim.write_text(json.dumps({}), encoding="utf-8")


# ---- 4. the installer ----
def goi(pid, lic):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("senos-pack.yaml", f"format: senos-pack\nspec: 1\nid: {pid}\nversion: 1.0.0\nname: {pid}\n"
                                      f"license: {lic}\nprovides:\n  skills: [demo]\n")
        z.writestr("skills/demo/SKILL.md", "---\nname: demo\ndescription: demo\n---\nDemo.\n")
    return b.getvalue()


brain = Path(tempfile.mkdtemp(prefix="brain-license-"))
s = pack_install.soi(goi("javis.nc-demo", "PolyForm-Noncommercial-1.0.0"), "x.zip")
check("preview of a noncommercial pack works", s.get("ok"), s)
r = pack_install.cai(s["staging_id"], s["sha256"], brain_root=str(brain))
check("cloud refuses to install it, saying why", not r.get("ok") and "Cloud" in (r.get("error") or ""), r)
s2 = pack_install.soi(goi("javis.custom-demo", "Remotion License"), "y.zip")
r2 = pack_install.cai(s2["staging_id"], s2["sha256"], brain_root=str(brain))
check("cloud installs a custom-license pack", r2.get("ok"), r2)
os.environ.pop("SENOS_CLOUD_LIMITS", None)
s3 = pack_install.soi(goi("javis.nc-demo", "PolyForm-Noncommercial-1.0.0"), "x.zip")
r3 = pack_install.cai(s3["staging_id"], s3["sha256"], brain_root=str(brain))
check("self-hosted installs the noncommercial pack", r3.get("ok"), r3)

print("\nOK" if not _fails else f"\n{len(_fails)} FAIL")
raise SystemExit(1 if _fails else 0)
