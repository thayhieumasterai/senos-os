"""Names the outside world still spells "javis" (SenOS is a fork of javis-os).

The store (blogminhquy/javis-store), its packs and the Zalo CLI (blogminhquy/javis-zalo) are upstream's and keep their
own names. Most of that is handled where it is read (pack ids, manifest names, format markers, the CLI's package name
and environment). This module holds the one piece that has to sit in the request path:

Plugins from upstream packs (Javis Gate) check the owner's sign-in by reading the cookie `javis_session`, while SenOS
sets `senos_session`. For plugin routes only (`/ext/...`), the request is given the same token under the old name
too. Nothing is ever set in the browser, and a request that already carries `javis_session` is left alone.
"""
from __future__ import annotations

OLD_COOKIE = b"javis_session"
NEW_COOKIE = b"senos_session"


def _with_old_cookie(headers):
    out, changed = [], False
    for k, v in headers:
        if k == b"cookie" and NEW_COOKIE + b"=" in v and OLD_COOKIE + b"=" not in v:
            for part in v.split(b";"):
                part = part.strip()
                if part.startswith(NEW_COOKIE + b"="):
                    v = v + b"; " + OLD_COOKIE + b"=" + part[len(NEW_COOKIE) + 1:]
                    changed = True
                    break
        out.append((k, v))
    return out if changed else None


class PluginSessionCookie:
    """ASGI middleware: mirror `senos_session` as `javis_session` on requests to `/ext/...` (plugin pages and APIs)."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") in ("http", "websocket") and str(scope.get("path") or "").startswith("/ext/"):
            h = _with_old_cookie(scope.get("headers") or [])
            if h is not None:
                scope = dict(scope, headers=h)
        await self.app(scope, receive, send)
