"""License kinds of store packs, and the SenOS Cloud rule that hides noncommercial ones.

A pack declares `license:` in its manifest (and the store index copies it). Three kinds matter to the owner:
  - "open": a permissive license (MIT, Apache-2.0, BSD...). Business use is fine, nothing to show.
  - "noncommercial": the license forbids commercial use (PolyForm Noncommercial, CC BY-NC...).
  - "custom": anything else (a vendor's own license, e.g. Remotion's). Read its terms before business use.

On SenOS Cloud (the SENOS_CLOUD_LIMITS file is set, see saas/runtime.py) a workspace is a paid service, so
noncommercial packs are hidden from the store and refused at install. The file can say
`"hide_noncommercial": false` to turn that off."""
import json
import os
import re

_OPEN = re.compile(r"^(mit|mit-0|isc|0bsd|unlicense|cc0(-1\.0)?|zlib|bsd-[0-9]-clause(-clear)?|apache-2\.0|"
                   r"mpl-2\.0|cc-by-4\.0|cc-by-sa-4\.0|python-2\.0|psf-2\.0|lgpl-[23]\.[01](-only|-or-later)?|"
                   r"gpl-[23]\.0(-only|-or-later)?|agpl-3\.0(-only|-or-later)?)$", re.I)
_NONCOMMERCIAL = re.compile(r"non-?commercial|\bnc\b|-nc-|-nc$", re.I)


def kind(license: str) -> str:
    """"open", "noncommercial", "custom", or "" when the pack declares no license."""
    s = (license or "").strip()
    if not s:
        return ""
    if _NONCOMMERCIAL.search(s):
        return "noncommercial"
    if _OPEN.match(s):
        return "open"
    return "custom"


def cloud_hides_noncommercial() -> bool:
    """True on SenOS Cloud unless the cloud limits file turns it off. Self-hosted SenOS shows every pack."""
    path = os.getenv("SENOS_CLOUD_LIMITS", "").strip()
    if not path:
        return False
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return d.get("hide_noncommercial", True) is not False
    except Exception:  # noqa: BLE001 - an unreadable file on a cloud box still means "this is the cloud"
        return True


def blocked(license: str) -> bool:
    return cloud_hides_noncommercial() and kind(license) == "noncommercial"
