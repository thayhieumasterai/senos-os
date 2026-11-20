"""Windows mở SenOS như một app - bản đối xứng của bộ launcher macOS (PR #3).

    python tests/run.py windows_launcher

Không chạy được .bat/.ps1 trên CI Linux nên đây là test TĨNH: canh các bất biến mà
vi phạm là hành vi hỏng thật, không canh câu chữ trang trí.

Bất biến quan trọng nhất: "SenOS.bat" phải THĂM DÒ /health TRƯỚC khi gọi
start-senos.vbs - vì vbs đó LUÔN kill instance cũ trước khi bật. Thiếu bước thăm dò
là double-click lần hai (mở lại cửa sổ) thành restart server, giết sạch việc nền
đang chạy dở. Đó là loại lỗi bấm thấy chạy được ngay nên không ai nghi ngờ.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import sys

_fails = []


def check(ten, cond, them=""):
    print(("ok   " if cond else "FAIL ") + ten + (("  [" + str(them) + "]") if them and not cond else ""))
    if not cond:
        _fails.append(ten)


BAT = ROOT / "SenOS.bat"
AS_BAT = ROOT / "senos-autostart.bat"
AS_PS1 = ROOT / "senos-autostart.ps1"

check("có SenOS.bat ở gốc repo (đối xứng SenOS.app bên Mac)", BAT.exists())
check("có senos-autostart.bat + .ps1", AS_BAT.exists() and AS_PS1.exists())

bat = BAT.read_text(encoding="utf-8")
ps1 = AS_PS1.read_text(encoding="utf-8")
as_bat = AS_BAT.read_text(encoding="utf-8")

# ---- SenOS.bat ----
i_health = bat.find("/health")
i_vbs = bat.find("wscript //nologo start-senos.vbs")   # dòng GỌI thật, không phải comment nhắc tên
check("CANARY: thăm dò /health TRƯỚC khi gọi start-senos.vbs (vbs kill instance cũ - "
      "thiếu bước này là double-click lần hai giết việc nền đang chạy)",
      0 < i_health < i_vbs)
check("tôn trọng SENOS_PORT, không hardcode một cổng", "SENOS_PORT" in bat)
check("mở dạng cửa sổ app (--app=), không chỉ mở tab trần", "--app=" in bat)
check("có fallback trình duyệt mặc định khi không có Edge/Chrome", 'start "" %URL%' in bat)
check("máy thiếu curl vẫn mở được (Windows cũ)", "where curl" in bat)
check("chờ server lên có GIỚI HẠN, không xoay vô hạn", "gtr 45" in bat or "gtr 40" in bat)
check("cd /d về thư mục script trước (không tin working directory kế thừa - "
      "cùng bài học với start-senos.vbs)", 'cd /d "%~dp0"' in bat)

# ---- autostart ----
# 0.306.0: autostart ghi CHUNG một mục với nút trong dashboard (HKCU Run "SenOS"), không còn shortcut trong
# Startup: hai mục cùng bật là lúc đăng nhập hai bản SenOS giành nhau cổng 7777.
check("autostart ghi HKCU Run (không cần admin), cùng tên với dashboard",
      "CurrentVersion\\Run" in ps1 and '$Name = "SenOS"' in ps1)
check("lệnh trỏ wscript + start-senos.vbs /open (chạy nền rồi mở dashboard)",
      "wscript.exe //nologo" in ps1 and "start-senos.vbs" in ps1 and '`" /open"' in ps1)
check("có đủ ba việc install/uninstall/status", all(k in ps1 for k in ("install", "uninstall", "status")))
check("uninstall xoá mục Run và dọn shortcut kiểu cũ", "Remove-ItemProperty -Path $RunKey -Name $Name" in ps1 and "Remove-Item $Lnk" in ps1)
check("wrapper .bat gọi ps1 với ExecutionPolicy Bypass (máy user mặc định chặn ps1)",
      "ExecutionPolicy Bypass" in as_bat)

# ---- README hai thứ tiếng đều chỉ tới launcher ----
vi = (ROOT / "docs" / "i18n" / "vi" / "README.md").read_text(encoding="utf-8")
en = (ROOT / "README.md").read_text(encoding="utf-8")
check("README (vi) nhắc SenOS.bat", "SenOS.bat" in vi and "senos-autostart.bat" in vi)
check("README (en) nhắc SenOS.bat", "SenOS.bat" in en and "senos-autostart.bat" in en)

# ---- không em dash (luật repo, TTS khựng) ----
for ten, s in (("SenOS.bat", bat), ("senos-autostart.ps1", ps1), ("senos-autostart.bat", as_bat)):
    check(f"{ten} không dùng em dash", "—" not in s)

print()
if _fails:
    print(f"{len(_fails)} test HỎNG: " + ", ".join(_fails))
    sys.exit(1)
print("Tất cả test windows_launcher đã qua.")
