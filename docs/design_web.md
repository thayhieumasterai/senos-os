# DESIGN_WEB.md — Hướng dẫn thiết kế giao diện cho Agos, Zero, BizOS

> **Dành cho AI coding agent trong VS Code (Copilot, Claude Code, Cursor, Codex…).**
> Đọc toàn bộ file này TRƯỚC khi viết bất kỳ dòng UI nào. Mọi quy tắc ở đây ưu tiên hơn thói quen mặc định của bạn.
> Mục tiêu: giao diện hiện đại, có chủ đích, trông như do một đội product design có kinh nghiệm làm ra. Khách hàng nhìn vào **không được** nhận ra đây là sản phẩm "vibe code".

---

## 0. Cách dùng file này

1. Đặt file ở thư mục gốc mỗi repo (Agos, Zero, BizOS).
2. Trỏ agent tới nó:
   - GitHub Copilot: tạo `.github/copilot-instructions.md` với dòng `Luôn tuân thủ design_web.md ở thư mục gốc khi làm UI.`
   - Claude Code: thêm cùng dòng đó vào `CLAUDE.md`.
   - Cursor / Codex / agent khác: thêm vào `AGENTS.md` hoặc `.cursor/rules`.
3. Mỗi khi giao việc UI, nhắc: *"Làm theo design_web.md, chạy checklist mục 14 trước khi báo xong."*

---

## 1. Vì sao giao diện AI bị nhận ra ngay

AI sinh UI bằng cách lấy **trung bình cộng** của hàng triệu landing page. Kết quả là một bộ mặc định ai cũng từng thấy. Khách hàng không cần biết thiết kế, họ chỉ cảm thấy: *"trang này giống trang kia"*, *"rẻ"*, *"template"*.

Ta thắng bằng 3 thứ AI mặc định thiếu:
- **Quyết định có chủ kiến** (chọn 1 hướng và đi tới cùng, không "an toàn ở giữa").
- **Nội dung thật** (số liệu, ảnh chụp sản phẩm, câu chữ cụ thể của ngành).
- **Chi tiết tay nghề** (căn chỉnh, trạng thái, khoảng cách, chữ số, micro-interaction).

---

## 2. DANH SÁCH CẤM — dấu vân tay của "vibe code"

Nếu UI có từ 2 mục dưới đây trở lên, làm lại.

### Màu & nền
- ❌ Gradient tím → xanh / tím → hồng (`from-purple-500 to-blue-500`, `from-indigo-* to-pink-*`).
- ❌ Chữ tiêu đề tô gradient (`bg-clip-text text-transparent`).
- ❌ Các "blob" mờ phát sáng, quầng sáng neon sau hero, `blur-3xl` trang trí.
- ❌ Nền đen tuyền `#000` + chữ trắng tuyền `#fff` + viền neon.
- ❌ Glassmorphism (`backdrop-blur` + nền trong suốt) dùng tràn lan. Chỉ được dùng cho thanh điều hướng dính hoặc overlay, tối đa 1 chỗ.
- ❌ Dùng màu Tailwind mặc định nguyên xi (`blue-500`, `indigo-600`, `slate-*`, `gray-*`) làm màu thương hiệu.

### Bố cục
- ❌ Hero căn giữa: badge nhỏ → tiêu đề to → 1 dòng mô tả → 2 nút → ảnh mockup. (Công thức số 1 của AI.)
- ❌ Lưới 3 cột thẻ tính năng, mỗi thẻ: icon trong ô vuông bo tròn có màu + tiêu đề + 2 dòng mô tả.
- ❌ Bento grid toàn ô kích thước/kiểu giống nhau.
- ❌ Nhãn chữ in hoa nhỏ giãn cách phía trên MỌI tiêu đề section (`FEATURES`, `PRICING`, `TESTIMONIALS`).
- ❌ Mọi section đều căn giữa, cùng padding, cùng nhịp — trang trông như băng chuyền.
- ❌ Bảng giá 3 cột với cột giữa có badge "Phổ biến nhất" phóng to — nếu cần bảng giá thì thiết kế theo dữ liệu thật của sản phẩm.
- ❌ Khối "Testimonials" với avatar tròn, 5 sao, tên giả kiểu "Nguyễn Văn A, CEO".
- ❌ Dải số liệu bịa: "10K+ người dùng", "99.9% uptime", "10x nhanh hơn".

### Thành phần
- ❌ `rounded-2xl` / `rounded-3xl` + `shadow-lg` / `shadow-xl` cho mọi thẻ.
- ❌ Thẻ lồng thẻ lồng thẻ. Ưu tiên đường kẻ phân cách, khoảng trắng, nền nhạt.
- ❌ Callout với viền trái dày màu (`border-l-4 border-blue-500`).
- ❌ shadcn/ui để nguyên mặc định (màu, radius, font) — ai cũng nhận ra.
- ❌ Icon ✨ (Sparkles) để biểu thị "AI". Icon robot, não bộ, tia sét.
- ❌ Emoji trong tiêu đề, nút, menu (🚀 🔥 ✨ 💡 ⚡).
- ❌ Nút có gradient + đổ bóng màu + hover phóng to `scale-105`.

### Chuyển động
- ❌ Mọi phần tử đều fade-up khi cuộn tới.
- ❌ Hiệu ứng gõ chữ (typewriter), chữ chạy, số đếm tăng dần không có lý do.
- ❌ Hover nảy, xoay, phát sáng trên thẻ.

### Câu chữ
- ❌ "Khai phá sức mạnh của…", "Nâng tầm…", "Cách mạng hóa…", "Giải pháp toàn diện", "Trải nghiệm liền mạch", "Tối ưu hóa mọi quy trình", "Unlock / Supercharge / Seamless / Effortless / Next-gen".
- ❌ Dùng dấu gạch dài (—) dày đặc, câu 3 vế "Nhanh hơn. Thông minh hơn. Mạnh mẽ hơn."
- ❌ Lorem ipsum, dữ liệu giả "John Doe", "Acme Inc", "example@email.com" lọt lên bản demo cho khách.

---

## 3. Nguyên tắc định hướng

1. **Sản phẩm là nhân vật chính.** Thay hình minh họa bằng ảnh chụp/khung UI thật của chính sản phẩm, đã được dàn dựng với dữ liệu đẹp và thực tế.
2. **Một ý tưởng thị giác mạnh cho mỗi sản phẩm** (xem mục 13). Không trộn 5 xu hướng.
3. **Mật độ có chủ đích.** Trang marketing thoáng; ứng dụng (dashboard) chặt, nhiều thông tin, giống công cụ làm việc thật (Linear, Stripe Dashboard, Vercel, Attio).
4. **Ít màu, nhiều sắc độ.** 1 màu nhấn + 1 dải trung tính có ánh màu (tinted neutral). Màu nhấn chiếm < 10% diện tích.
5. **Chữ làm nên giao diện.** 80% chất lượng cảm nhận đến từ typography và khoảng cách, không phải hiệu ứng.
6. **Phá đối xứng có kiểm soát.** Bố cục lệch trái, cột không đều (7/5, 8/4), tiêu đề lớn tràn lề — nhưng luôn bám lưới.
7. **Chi tiết thắng hiệu ứng.** Trạng thái rỗng, lỗi, đang tải, focus, phím tắt — đây là nơi AI bỏ quên và là nơi khách hàng cảm nhận "chuyên nghiệp".

---

## 4. Design tokens (bắt buộc dùng token, cấm hard-code)

Stack khuyến nghị: **Tailwind CSS v4** (`@theme`), **Radix / shadcn** đã tùy biến, **Motion** (framer-motion) cho chuyển động.
Mọi màu, cỡ chữ, bán kính, bóng đổ phải đi qua biến. Không viết `text-[#3b82f6]` hay `bg-blue-500` trong component.

### 4.1 Màu — dùng OKLCH

```css
@import "tailwindcss";

@theme {
  /* Trung tính có ánh màu (không dùng gray thuần) — chỉnh hue theo từng dự án */
  --color-bg:        oklch(0.985 0.003 85);   /* nền trang, hơi ấm, không trắng tinh */
  --color-surface:   oklch(1 0 0);            /* bề mặt nổi: panel, popover */
  --color-subtle:    oklch(0.965 0.004 85);   /* nền phụ, hàng bảng hover */
  --color-border:    oklch(0.91 0.005 85);    /* đường kẻ 1px */
  --color-border-strong: oklch(0.84 0.006 85);
  --color-muted:     oklch(0.55 0.01 85);     /* chữ phụ */
  --color-fg:        oklch(0.21 0.01 85);     /* chữ chính, không đen tuyền */

  /* Màu nhấn — MỖI DỰ ÁN MỘT MÀU, xem mục 13 */
  --color-accent:    oklch(0.62 0.17 45);
  --color-accent-fg: oklch(0.99 0 0);
  --color-accent-soft: oklch(0.95 0.04 45);

  /* Ngữ nghĩa — giảm bão hòa, không dùng đỏ/xanh lá chói */
  --color-success: oklch(0.62 0.12 155);
  --color-warning: oklch(0.75 0.13 80);
  --color-danger:  oklch(0.58 0.17 27);
  --color-info:    oklch(0.6 0.1 240);
}

/* Dark mode: KHÔNG đảo màu đơn giản. Nền xám ấm sâu, không #000 */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --color-bg:      oklch(0.17 0.005 85);
    --color-surface: oklch(0.205 0.006 85);
    --color-subtle:  oklch(0.235 0.006 85);
    --color-border:  oklch(0.29 0.006 85);
    --color-border-strong: oklch(0.36 0.008 85);
    --color-muted:   oklch(0.68 0.01 85);
    --color-fg:      oklch(0.94 0.005 85);
    --color-accent-soft: oklch(0.3 0.06 45);
  }
}
```

Quy tắc màu:
- Tỷ lệ diện tích ≈ **70% nền / 20% bề mặt & chữ / ≤10% màu nhấn**.
- Màu nhấn chỉ dùng cho: hành động chính, trạng thái chọn, 1 điểm nhấn dữ liệu. Không dùng làm nền section lớn.
- Độ tương phản chữ ≥ 4.5:1 (chữ thường), ≥ 3:1 (chữ ≥ 24px). Kiểm tra cả dark mode.

### 4.2 Typography

**Font phải hỗ trợ tiếng Việt đầy đủ.** Luôn test bằng câu: *"Hướng dẫn quản lý ưu tiên — Ỹ Ữ Ẫ Ợ Ệ đồng 1.234.567₫"*. Dấu không được dính, lệch hoặc rơi về font fallback.

Tránh các font "mặc định AI" làm font chính: Inter, Poppins, Montserrat, Roboto, Open Sans, Plus Jakarta Sans, Space Grotesk, Geist (nay đã quá phổ biến trong bản vibe code).

Gợi ý (đều có bộ ký tự tiếng Việt trên Google Fonts — vẫn phải tự kiểm tra lại):

| Vai trò | Lựa chọn | Tính cách |
|---|---|---|
| Sans hiển thị/tiêu đề | **Bricolage Grotesque**, **Be Vietnam Pro** (chỉ khi tùy chỉnh weight/tracking kỹ), **Lexend** | Có cá tính, vẫn dễ đọc |
| Sans thân bài/UI | **Be Vietnam Pro**, **IBM Plex Sans**, **Nunito Sans** | Trung tính, rõ ở cỡ nhỏ |
| Serif nhấn (marketing) | **Fraunces**, **Newsreader**, **Source Serif 4** | Tạo cảm giác biên tập, cao cấp |
| Mono (số liệu, mã, ID) | **JetBrains Mono**, **IBM Plex Mono** | Kỹ thuật, chính xác |

Nếu có ngân sách: font trả phí/độc quyền (ví dụ bản Việt hóa của các foundry) là cách nhanh nhất để thoát "mùi AI".

Thang cỡ chữ (tỷ lệ ~1.2, khóa cứng — không tự ý thêm cỡ):

```css
@theme {
  --text-xs:   0.75rem;   /* 12 — nhãn, meta */
  --text-sm:   0.8125rem; /* 13 — UI dày đặc, bảng */
  --text-base: 0.9375rem; /* 15 — thân bài app */
  --text-md:   1.0625rem; /* 17 — thân bài marketing */
  --text-lg:   1.25rem;   /* 20 */
  --text-xl:   1.5rem;    /* 24 */
  --text-2xl:  2rem;      /* 32 */
  --text-3xl:  2.75rem;   /* 44 */
  --text-display: clamp(2.75rem, 6vw, 5.5rem); /* hero */
}
```

Quy tắc chữ:
- Tiêu đề lớn: `letter-spacing: -0.02em` đến `-0.035em`, `line-height: 1.05–1.15`, weight 500–600 (không lạm dụng 700–800).
- Thân bài: `line-height: 1.55–1.65`, độ rộng dòng **55–75 ký tự** (`max-w-[65ch]`).
- `text-wrap: balance` cho tiêu đề, `text-wrap: pretty` cho đoạn văn.
- Số liệu, tiền, bảng: `font-variant-numeric: tabular-nums;` — bắt buộc.
- Tối đa **2 họ font** mỗi sản phẩm (+1 mono).
- Chữ in hoa chỉ cho nhãn rất nhỏ, có `tracking-wide`, và **không** đặt trên mọi section.

### 4.3 Khoảng cách, lưới, bán kính, bóng

```css
@theme {
  --spacing: 0.25rem; /* mọi khoảng cách là bội số 4px */

  --radius-sm: 4px;   /* badge, checkbox */
  --radius-md: 6px;   /* nút, input */
  --radius-lg: 10px;  /* panel, dialog */
  /* KHÔNG dùng radius > 12px cho thành phần UI, trừ avatar/pill có chủ đích */

  --shadow-xs: 0 1px 0 oklch(0 0 0 / 0.04);
  --shadow-sm: 0 1px 2px oklch(0 0 0 / 0.05), 0 0 0 1px oklch(0 0 0 / 0.04);
  --shadow-pop: 0 8px 24px -6px oklch(0 0 0 / 0.12), 0 0 0 1px oklch(0 0 0 / 0.05);
  /* Bóng chỉ cho thứ thực sự nổi lên: popover, dropdown, dialog, toast */
}
```

- Lưới marketing: 12 cột, `max-width: 1200–1280px`, gutter 24px (desktop) / 16px (mobile).
- Nhịp dọc giữa section marketing: không đều nhau — luân phiên 96 / 160 / 128px để tạo nhịp.
- Phân cấp bằng **khoảng trắng và đường kẻ 1px** trước, nền nhạt sau, bóng đổ cuối cùng.

---

## 5. Bố cục — các mẫu nên dùng thay cho công thức AI

### Hero (thay hero căn giữa)
Chọn 1 trong:
- **Lệch trái + sản phẩm tràn phải:** tiêu đề căn trái chiếm 6–7 cột, ảnh UI thật tràn ra khỏi mép phải màn hình.
- **Tiêu đề biên tập:** chữ display rất lớn, serif hoặc grotesque cá tính, 1 câu khẳng định cụ thể, bên dưới là demo tương tác thật (không phải ảnh).
- **Sản phẩm trước, chữ sau:** khung app chiếm gần toàn màn hình đầu tiên, tiêu đề ngắn đặt góc trên trái.

Tiêu đề hero phải **nói cụ thể sản phẩm làm gì cho ai**. Ví dụ tốt: *"Chốt công nợ cuối tháng trong 20 phút thay vì 2 ngày."* Ví dụ xấu: *"Nền tảng quản trị doanh nghiệp thông minh thế hệ mới."*

### Tính năng (thay lưới 3 thẻ icon)
- **Hàng xen kẽ:** mỗi tính năng là 1 hàng, chữ một bên — ảnh UI cận cảnh một bên, đổi phía mỗi hàng, kích thước ảnh khác nhau.
- **Danh sách có đánh số + ảnh dính (sticky):** bên trái danh sách tính năng, bên phải ảnh UI đổi theo mục đang cuộn tới.
- **Tab demo:** một khung UI, các tab đổi trạng thái thật.
- Bento chỉ khi các ô **khác nhau về kích thước VÀ loại nội dung** (1 ô biểu đồ thật, 1 ô trích dẫn, 1 ô số liệu, 1 ô ảnh màn hình).

### Bằng chứng xã hội
- Logo khách hàng thật (đơn sắc, cùng độ cao quang học), hoặc
- 1 trích dẫn lớn kèm ảnh thật, tên thật, chức vụ thật, tên công ty thật. Không có thì **bỏ section**, không bịa.

### Ứng dụng / dashboard (BizOS, Agos…)
- Khung: sidebar 232–260px (thu gọn được) + topbar 48–56px + vùng nội dung.
- Ưu tiên **bảng và danh sách** hơn thẻ. Bảng: hàng cao 36–44px, viền ngang 1px, không kẻ dọc, header dính, cột số căn phải + tabular-nums.
- Command palette (`⌘K` / `Ctrl K`) cho điều hướng và hành động.
- Bộ lọc dạng "chip" có thể xóa, lưu được view.
- Trang chi tiết: bố cục 2 cột (nội dung chính + panel thuộc tính bên phải), giống Linear/Attio.

---

## 6. Thành phần (component)

**Nút**
- Chiều cao: 28 (sm) / 32 (md, mặc định trong app) / 40 (lg, marketing).
- Primary: nền `--color-accent`, không gradient, không bóng màu. Hover: tối hơn ~4% lightness. Active: dịch xuống 0.5px hoặc tối thêm.
- Secondary: nền surface + viền 1px. Ghost: chỉ chữ, nền subtle khi hover.
- Mỗi màn hình **chỉ 1 nút primary**.

**Input**
- Cao 32–36px, viền 1px `--color-border`, focus: viền accent + ring 3px `--color-accent-soft`. Không glow.
- Label luôn hiển thị phía trên (không chỉ dùng placeholder). Lỗi hiển thị ngay dưới, câu chữ hướng dẫn cách sửa.

**Focus ring**: `outline: 2px solid var(--color-accent); outline-offset: 2px;` chỉ với `:focus-visible`. Không bao giờ `outline: none` mà không thay thế.

**Badge / trạng thái**: chấm tròn 6px + chữ, hoặc nền `*-soft` + chữ đậm màu. Không dùng badge nền đặc chói.

**Dialog / popover / dropdown**: radius-lg, shadow-pop, animation scale 0.98→1 + opacity trong 140ms.

**Toast**: góc dưới, ngắn gọn, có hành động "Hoàn tác" khi xóa.

**Tùy biến shadcn**: bắt buộc thay toàn bộ biến màu, radius, font của shadcn bằng token ở mục 4 trước khi dùng component đầu tiên.

---

## 7. Chuyển động

- Thời lượng: 120–180ms (hover, toggle), 200–280ms (mở panel, dialog), tối đa 400ms (chuyển trang).
- Easing: `cubic-bezier(0.2, 0, 0, 1)` (vào) và `cubic-bezier(0.4, 0, 1, 1)` (ra). Không dùng `ease-in-out` mặc định cho mọi thứ, không dùng spring nảy cho UI làm việc.
- Chỉ animate `transform` và `opacity`.
- Chuyển động phải **giải thích** điều gì đó: phần tử đến từ đâu, cái gì vừa thay đổi. Không trang trí.
- Trang marketing: tối đa 1–2 khoảnh khắc chuyển động "đáng nhớ" (ví dụ demo sản phẩm tự chạy), phần còn lại tĩnh.
- Luôn tôn trọng `@media (prefers-reduced-motion: reduce)`.

---

## 8. Icon, hình ảnh, minh họa

- Một bộ icon duy nhất cho mỗi sản phẩm, nét 1.5px, cỡ 16px (app) / 20px (marketing). Gợi ý: Phosphor, Tabler, hoặc Lucide **nhưng** không đặt icon trong ô vuông màu.
- Icon đi cạnh chữ, cùng màu chữ (hoặc muted), không tô màu nhấn trừ khi đang active.
- Hình ảnh: ưu tiên **ảnh chụp UI thật** với dữ liệu thật (tên công ty Việt, số tiền VNĐ, ngày dd/mm/yyyy). Đặt trong khung có viền 1px, bo 10px, có thể nghiêng nhẹ hoặc cắt tràn.
- Ảnh người: ảnh thật của đội ngũ/khách hàng. Cấm ảnh stock "doanh nhân cười bắt tay", cấm minh họa 3D/isometric sinh bằng AI, cấm nhân vật hoạt hình Corporate Memphis.
- Hoạ tiết nền (nếu cần): lưới chấm/đường mảnh độ mờ thấp, noise grain 2–4%, không blob.

---

## 9. Câu chữ (UX writing) tiếng Việt

- Viết như người thật nói với khách hàng thật. Câu ngắn, động từ mạnh, có con số cụ thể.
- Nút ghi rõ hành động: "Tạo hóa đơn", "Gửi cho khách", không phải "Bắt đầu ngay", "Khám phá".
- Thông báo lỗi = chuyện gì xảy ra + cách sửa: *"Không lưu được vì mất kết nối. Dữ liệu vẫn còn trên máy, bấm Thử lại."*
- Trạng thái rỗng = vì sao rỗng + 1 hành động tiếp theo + (tùy chọn) ví dụ mẫu.
- Định dạng Việt Nam: `1.234.567 ₫`, `18/11/2026`, giờ 24h `14:30`, số điện thoại `0901 234 567`.
- Xưng hô nhất quán trong toàn sản phẩm (chọn "bạn" hoặc "anh/chị", không trộn).
- Không emoji trong UI chức năng. Không dấu chấm than liên tục.

---

## 10. Dữ liệu & biểu đồ (dashboard)

- KPI tile: số lớn (tabular-nums, weight 500), nhãn nhỏ muted phía trên, thay đổi so với kỳ trước (▲ 4,2%) màu ngữ nghĩa dịu, sparkline mảnh tùy chọn.
- Biểu đồ: 1 màu nhấn cho chuỗi chính, các chuỗi khác dùng sắc độ trung tính. Lưới mờ, không viền khung, không 3D, không pie chart quá 4 phần.
- Trục và nhãn dùng `--text-xs`, màu muted. Tooltip dạng popover chuẩn.
- Luôn có trạng thái: đang tải (skeleton đúng hình dạng nội dung), rỗng, lỗi, không có quyền.

---

## 11. Những chi tiết "tay nghề" bắt buộc

- [ ] Favicon + icon PWA riêng, ảnh Open Graph riêng cho từng trang chính.
- [ ] `::selection` dùng màu accent-soft.
- [ ] Scrollbar mảnh, cùng tông trung tính.
- [ ] Trang 404 / 500 được thiết kế, có đường quay lại.
- [ ] Skeleton loading khớp đúng bố cục thật (không spinner giữa màn hình cho nội dung).
- [ ] Optimistic UI cho thao tác nhanh (tick, đổi tên, kéo thả).
- [ ] Phím tắt hiển thị trong tooltip/menu (`Ctrl K`, `C` để tạo mới…).
- [ ] Trạng thái hover, active, focus-visible, disabled, loading cho MỌI phần tử tương tác.
- [ ] Căn chỉnh quang học: icon trong nút căn giữa theo mắt, không chỉ theo toán học.
- [ ] Không có layout shift khi tải (đặt kích thước ảnh, font `size-adjust`/`font-display: swap`).
- [ ] Responsive thật: kiểm tra 375px, 768px, 1280px, 1536px. Không cuộn ngang. Bảng trên mobile chuyển thành danh sách.
- [ ] Dark mode được thiết kế riêng (độ tương phản, bóng đổ chuyển thành viền sáng nhẹ), không chỉ đảo màu.

---

## 12. Khả năng truy cập (a11y) — tối thiểu

- HTML ngữ nghĩa (`button`, `nav`, `main`, `label`), không `div onClick`.
- Vùng bấm ≥ 40×40px trên mobile.
- Toàn bộ thao tác dùng được bằng bàn phím; thứ tự Tab hợp lý; dialog bẫy focus và đóng bằng Esc.
- `alt` có nghĩa cho ảnh, `aria-label` cho nút chỉ có icon.
- Không truyền tải thông tin chỉ bằng màu.

---

## 13. Bản sắc riêng cho từng dự án

> ⚠️ Đây là **đề xuất khởi điểm** — chủ dự án cần xác nhận/điều chỉnh. Nguyên tắc: 3 sản phẩm phải **khác nhau rõ rệt**, nhưng cùng chất lượng tay nghề. Nếu 3 sản phẩm trông giống nhau, khách hàng sẽ nghĩ là template.

| | **Agos** | **Zero** | **BizOS** |
|---|---|---|---|
| Ý tưởng thị giác | Kỹ thuật, chính xác, "phòng điều khiển" | Tối giản cực độ, khoảng trắng là chủ đạo | Công cụ làm việc tin cậy, dày thông tin, biên tập |
| Màu nhấn (OKLCH gợi ý) | Cam đất `oklch(0.64 0.16 45)` | Đen mực + 1 điểm xanh lá chanh `oklch(0.88 0.19 125)` | Xanh rêu đậm `oklch(0.48 0.09 165)` |
| Hue trung tính | Ấm (85) | Gần như trung tính (0–260, chroma ≤ 0.003) | Hơi lạnh-xanh (200) |
| Font | Bricolage Grotesque + JetBrains Mono | 1 sans duy nhất (IBM Plex Sans) + mono | Newsreader (tiêu đề marketing) + Be Vietnam Pro (UI) |
| Radius | 4–6px, góc sắc | 0–4px | 6–10px |
| Đặc trưng | Nhãn mono, đường lưới mảnh, số liệu realtime | Chữ rất lớn, rất ít màu, lưới nghiêm ngặt | Bảng dữ liệu đẹp, trang chi tiết 2 cột, ⌘K |
| Tránh | Neon/cyberpunk | Lạnh lẽo, thiếu trạng thái | Giống ERP cũ: menu dày, màu xanh dương mặc định |

Mỗi dự án nên có file `tokens.css` riêng ghi đè mục 4.

---

## 14. Quy trình làm việc cho AI agent

Trước khi code UI:
1. Đọc file này + `tokens.css` của dự án.
2. Xác định: màn hình này phục vụ ai, hành động chính là gì, dữ liệu thật là gì.
3. Viết ra (trong đầu hoặc comment) cấu trúc phân cấp: cái gì quan trọng nhất → ít nhất.
4. Chọn mẫu bố cục ở mục 5. Không dùng công thức mục 2.

Trong khi code:
- Chỉ dùng token. Không màu/cỡ chữ/khoảng cách ngẫu nhiên.
- Dùng dữ liệu mẫu thực tế, tiếng Việt, đúng ngành.
- Viết đủ các trạng thái: default, hover, focus, loading, empty, error, disabled.

Sau khi code — **TỰ KIỂM TRA (bắt buộc trước khi báo xong)**:
- [ ] Không vi phạm mục nào trong DANH SÁCH CẤM (mục 2). Liệt kê ra nếu nghi ngờ.
- [ ] Chụp màn hình ở 375px và 1440px, cả light & dark.
- [ ] "Bài test che logo": che logo đi, màn hình này có phân biệt được với 1 landing page AI bất kỳ không? Nếu không → sửa.
- [ ] "Bài test nheo mắt": nheo mắt nhìn, có thấy ngay 1 điểm nhấn chính và thứ bậc rõ ràng không?
- [ ] Mọi chữ tiếng Việt hiển thị đúng font, đúng dấu.
- [ ] Số liệu dùng tabular-nums, định dạng VN.
- [ ] Không còn lorem ipsum / dữ liệu giả lộ liễu.
- [ ] Đạt tương phản WCAG AA.
- [ ] Lighthouse: Performance ≥ 90, Accessibility ≥ 95.

---

## 15. Nguồn tham khảo đúng "gu" (để học tư duy, không sao chép)

Linear, Stripe, Vercel, Attio, Raycast, Arc, Mercury, Ramp, Height, Cron/Notion Calendar, Pitch, Family, Rauno Freiberg (rauno.me), Emil Kowalski, Paco Coursey.
Học: cách họ dùng khoảng trắng, chữ, đường kẻ 1px, chuyển động có mục đích và ảnh chụp sản phẩm thật. **Không** sao chép bố cục, màu hay câu chữ của họ.

---

*Cập nhật lần cuối: 18/11/2026. Mọi thay đổi quy tắc cần ghi vào đây để cả 3 dự án dùng chung một chuẩn.*
