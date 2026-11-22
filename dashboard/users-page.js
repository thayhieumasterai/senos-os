// Trang Người dùng (2026-11-22, multi-user): chủ thêm người, chọn vai trò và cấp quyền. Chỉ CHỦ mở được (máy chủ
// chặn /users với mọi người khác, users_guard.OWNER_ONLY). Quyền thật nằm ở máy chủ; trang này chỉ là chỗ chọn.
//
// Một người "Một phần quyền" có sẵn bộ não riêng; ở đây chủ cấp thêm: bộ não chung (chỉ xem / xem và sửa), Agent
// trong các bộ não đó (tất cả hoặc chọn từng cái), tài khoản kênh trong Hộp thư bot, và có cho AI hành động ra ngoài.
(function () {
  "use strict";
  const t = (k, v) => (window.t ? window.t(k, v) : k);
  const esc = (s) => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  const ic = (n) => (window.ic ? window.ic(n) : "");

  async function api(path, body) {
    const opt = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
    const r = await fetch(path, opt);
    let d = {};
    try { d = await r.json(); } catch (e) {}
    if (!r.ok && d.ok === undefined) d.ok = false;
    return d;
  }

  let DATA = { users: [], seats: {}, brains: [], channels: [] };
  const AGENTS = {};          // brain path -> [{slug}]

  async function render(el) {
    el.innerHTML = `<div class="pg-loading pg-page">${esc(t("common.loading"))}</div>`;
    const d = await api("/users");
    if (!d.ok) { el.innerHTML = `<div class="cview-section"><div class="gcard">${esc(d.error || t("users.err_load"))}</div></div>`; return; }
    DATA = d;
    const s = d.seats || {};
    const cap = s.max == null ? t("users.unlimited") : String(s.max);
    const full = s.max != null && s.used >= s.max;
    el.innerHTML = `
      <div class="cview-section us-page">
        <div class="us-head">
          <div>
            <h3>${esc(t("page.users.label"))}</h3>
            <div class="gcard-meta">${esc(t("users.seats", { used: s.used || 0, max: cap }))}${full ? " · " + esc(t("users.seats_full")) : ""}</div>
          </div>
          <div class="us-head-act">
            ${full ? `<a class="s-btn-ghost us-buy" href="/portal" target="_top">${ic("plus")} ${esc(t("users.buy_more"))}</a>` : ""}
            <button class="s-btn" id="usAdd" ${full ? "disabled" : ""}>${ic("user-plus")} ${esc(t("users.add"))}</button>
          </div>
        </div>
        <div class="gcard us-list">
          <div class="us-row us-owner">${ic("shield")}<div class="us-who"><b>${esc(t("users.owner"))}</b><span class="gcard-meta">${esc(t("users.owner_note"))}</span></div></div>
          ${(d.users || []).map(rowHtml).join("") || `<div class="gcard-meta us-empty">${esc(t("users.empty"))}</div>`}
        </div>
        <div id="usForm"></div>
      </div>`;
    el.querySelector("#usAdd")?.addEventListener("click", () => openForm(el, null));
    el.querySelectorAll("[data-us-edit]").forEach(b => b.addEventListener("click", () =>
      openForm(el, (DATA.users || []).find(u => u.id === b.dataset.usEdit))));
    el.querySelectorAll("[data-us-toggle]").forEach(b => b.addEventListener("click", async () => {
      const u = (DATA.users || []).find(x => x.id === b.dataset.usToggle);
      const r = await api(`/users/${encodeURIComponent(u.id)}`, { disabled: !u.disabled });
      if (!r.ok) alert(r.error || t("users.err_save"));
      render(el);
    }));
    el.querySelectorAll("[data-us-del]").forEach(b => b.addEventListener("click", async () => {
      const u = (DATA.users || []).find(x => x.id === b.dataset.usDel);
      if (!confirm(t("users.del_q", { name: u.name || u.username }))) return;
      const r = await api(`/users/${encodeURIComponent(u.id)}/delete`, {});
      if (!r.ok) alert(r.error || t("users.err_save"));
      render(el);
    }));
  }

  function rowHtml(u) {
    const role = u.role === "full" ? t("users.role_full") : t("users.role_limited");
    const p = u.perms || {};
    const bits = u.role === "full" ? [] : [
      t("users.sum_brains", { n: Object.keys(p.brains || {}).length }),
      t("users.sum_channels", { n: (p.channels || []).length }),
    ];
    return `<div class="us-row${u.disabled ? " us-off" : ""}">
      ${ic(u.role === "full" ? "shield-check" : "user")}
      <div class="us-who"><b>${esc(u.name || u.username)}</b>
        <span class="gcard-meta">@${esc(u.username)} · ${esc(role)}${bits.length ? " · " + esc(bits.join(" · ")) : ""}${u.disabled ? " · " + esc(t("users.disabled")) : ""}</span></div>
      <div class="us-act">
        <button class="s-btn-ghost" data-us-edit="${esc(u.id)}">${esc(t("common.edit"))}</button>
        <button class="s-btn-ghost" data-us-toggle="${esc(u.id)}">${esc(u.disabled ? t("users.enable") : t("users.disable"))}</button>
        <button class="s-btn-ghost us-del" data-us-del="${esc(u.id)}" aria-label="${esc(t("common.delete"))}">${ic("trash-2")}</button>
      </div>
    </div>`;
  }

  async function agentsOf(brain) {
    if (!AGENTS[brain]) {
      const d = await api("/users/agents?brain=" + encodeURIComponent(brain));
      AGENTS[brain] = d.agents || [];
    }
    return AGENTS[brain];
  }

  function openForm(el, u) {
    const box = el.querySelector("#usForm");
    const p = (u && u.perms) || { brains: {}, agents: {}, channels: [], outside: false };
    const role = (u && u.role) || "limited";
    const own = (u && u.personal_brain) || "";
    const brains = (DATA.brains || []).filter(b => b.path !== own);
    box.innerHTML = `
      <div class="gcard us-form">
        <h4>${esc(u ? t("users.edit_title", { name: u.name || u.username }) : t("users.add_title"))}</h4>
        <div class="us-grid">
          <label class="js-lbl">${esc(t("users.f_username"))}<input class="js-input" id="usUser" ${u ? "disabled" : ""} value="${esc(u ? u.username : "")}" autocomplete="off" placeholder="${esc(t("users.f_username_ph"))}"></label>
          <label class="js-lbl">${esc(t("users.f_name"))}<input class="js-input" id="usName" value="${esc(u ? u.name : "")}"></label>
          <label class="js-lbl">${esc(u ? t("users.f_pw_new") : t("users.f_pw"))}<input class="js-input" id="usPw" type="password" autocomplete="new-password" placeholder="${esc(u ? t("users.f_pw_keep") : t("users.f_pw_ph"))}"></label>
          <label class="js-lbl">${esc(t("users.f_role"))}
            <select class="js-input" id="usRole">
              <option value="limited" ${role === "limited" ? "selected" : ""}>${esc(t("users.role_limited"))}</option>
              <option value="full" ${role === "full" ? "selected" : ""}>${esc(t("users.role_full"))}</option>
            </select></label>
        </div>
        <div class="gcard-meta" id="usRoleNote"></div>
        <div id="usPerms">
          <div class="us-sec">${ic("brain")} <b>${esc(t("users.p_brains"))}</b>
            <div class="gcard-meta">${esc(t("users.p_brains_note"))}</div></div>
          ${brains.map(b => {
            const lv = (p.brains || {})[b.path] || "";
            return `<div class="us-brain" data-brain="${esc(b.path)}">
              <label class="us-chk"><input type="checkbox" class="usB" ${lv ? "checked" : ""}> ${esc(b.label)}</label>
              <select class="js-input usLv" ${lv ? "" : "disabled"}>
                <option value="read" ${lv !== "write" ? "selected" : ""}>${esc(t("users.lv_read"))}</option>
                <option value="write" ${lv === "write" ? "selected" : ""}>${esc(t("users.lv_write"))}</option>
              </select>
              <div class="us-agents" ${lv ? "" : "hidden"}></div>
            </div>`;
          }).join("") || `<div class="gcard-meta">${esc(t("users.p_no_brains"))}</div>`}
          <div class="us-sec">${ic("messages-square")} <b>${esc(t("users.p_channels"))}</b>
            <div class="gcard-meta">${esc(t("users.p_channels_note"))}</div></div>
          ${(DATA.channels || []).map(c => `<label class="us-chk"><input type="checkbox" class="usC" value="${esc(c.id)}" ${(p.channels || []).includes(c.id) ? "checked" : ""}> ${esc(c.name)} <span class="gcard-meta">${esc(c.channel || "")}</span></label>`).join("")
            || `<div class="gcard-meta">${esc(t("users.p_no_channels"))}</div>`}
          <div class="us-sec">${ic("send")} <b>${esc(t("users.p_outside"))}</b></div>
          <label class="us-chk"><input type="checkbox" id="usOut" ${p.outside ? "checked" : ""}> ${esc(t("users.p_outside_note"))}</label>
        </div>
        <div class="us-foot">
          <span class="gcard-meta" id="usMsg"></span>
          <button class="s-btn-ghost" id="usCancel">${esc(t("common.cancel"))}</button>
          <button class="s-btn" id="usSave">${esc(t("common.save"))}</button>
        </div>
      </div>`;
    const roleSel = box.querySelector("#usRole");
    const syncRole = () => {
      const lim = roleSel.value === "limited";
      box.querySelector("#usPerms").hidden = !lim;
      box.querySelector("#usRoleNote").textContent = lim ? t("users.role_limited_note") : t("users.role_full_note");
    };
    roleSel.addEventListener("change", syncRole); syncRole();
    box.querySelectorAll(".us-brain").forEach(row => {
      const cb = row.querySelector(".usB"), lv = row.querySelector(".usLv"), ag = row.querySelector(".us-agents");
      const fill = async () => {
        const list = await agentsOf(row.dataset.brain);
        const have = (p.agents || {})[row.dataset.brain] || [];
        const all = have.includes("*");
        ag.innerHTML = list.length ? `<div class="gcard-meta">${esc(t("users.p_agents"))}</div>
          <label class="us-chk"><input type="checkbox" class="usAall" ${all ? "checked" : ""}> ${esc(t("users.p_agents_all"))}</label>
          <div class="us-agent-list" ${all ? "hidden" : ""}>${list.map(a => `<label class="us-chk"><input type="checkbox" class="usA" value="${esc(a.slug)}" ${have.includes(a.slug) ? "checked" : ""}> ${esc(a.name)}</label>`).join("")}</div>`
          : `<div class="gcard-meta">${esc(t("users.p_no_agents"))}</div>`;
        ag.querySelector(".usAall")?.addEventListener("change", e => { ag.querySelector(".us-agent-list").hidden = e.target.checked; });
      };
      cb.addEventListener("change", () => { lv.disabled = !cb.checked; ag.hidden = !cb.checked; if (cb.checked && !ag.innerHTML) fill(); });
      if (cb.checked) fill();
    });
    box.querySelector("#usCancel").addEventListener("click", () => { box.innerHTML = ""; });
    box.querySelector("#usSave").addEventListener("click", async () => {
      const perms = { brains: {}, agents: {}, channels: [], outside: box.querySelector("#usOut").checked };
      box.querySelectorAll(".us-brain").forEach(row => {
        if (!row.querySelector(".usB").checked) return;
        const b = row.dataset.brain;
        perms.brains[b] = row.querySelector(".usLv").value;
        if (row.querySelector(".usAall")?.checked) perms.agents[b] = ["*"];
        else perms.agents[b] = [...row.querySelectorAll(".usA:checked")].map(x => x.value);
      });
      perms.channels = [...box.querySelectorAll(".usC:checked")].map(x => x.value);
      const body = { name: box.querySelector("#usName").value.trim(), role: roleSel.value, perms };
      const pw = box.querySelector("#usPw").value;
      if (pw) body.password = pw;
      let r;
      if (u) r = await api(`/users/${encodeURIComponent(u.id)}`, body);
      else {
        body.username = box.querySelector("#usUser").value.trim().toLowerCase();
        if (!pw) { box.querySelector("#usMsg").textContent = t("users.f_pw_need"); return; }
        r = await api("/users", body);
      }
      if (!r.ok) { box.querySelector("#usMsg").textContent = r.error || t("users.err_save"); return; }
      render(el);
    });
    box.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Một người dùng thêm vào mở trang Tài khoản: chỉ đổi mật khẩu của chính mình (họ không đọc được /settings).
  function renderSelf(el, me) {
    el.innerHTML = `
      <div class="cview-section">
        <h3>${esc(t("users.self_title"))}</h3>
        <div class="gcard" style="max-width:520px">
          <div class="gcard-meta">${ic("user")} <b>${esc(me.name || me.username)}</b> · @${esc(me.username)} · ${esc(me.role === "full" ? t("users.role_full") : t("users.role_limited"))}</div>
          <label class="js-lbl">${esc(t("cs.ac_cur_pw"))}</label><input class="js-input" id="usSelfCur" type="password" autocomplete="current-password">
          <label class="js-lbl">${esc(t("users.f_pw_new"))}</label><input class="js-input" id="usSelfPw" type="password" autocomplete="new-password">
          <button class="gcard-btn" id="usSelfSave">${esc(t("common.save"))}</button>
          <div class="gcard-meta" id="usSelfMsg"></div>
          <button class="s-btn-ghost" id="usSelfOut" style="margin-top:12px">${ic("log-out")} ${esc(t("users.sign_out"))}</button>
        </div>
      </div>`;
    el.querySelector("#usSelfSave").addEventListener("click", async () => {
      const fd = new FormData();
      fd.append("current_password", el.querySelector("#usSelfCur").value);
      fd.append("password", el.querySelector("#usSelfPw").value);
      const r = await fetch("/auth/password", { method: "POST", body: fd });
      let d = {}; try { d = await r.json(); } catch (e) {}
      el.querySelector("#usSelfMsg").textContent = d.ok ? t("users.self_saved") : (d.error || t("users.err_save"));
    });
    el.querySelector("#usSelfOut").addEventListener("click", async () => {
      try { await fetch("/auth/logout", { method: "POST" }); } catch (e) {}
      location.reload();
    });
  }

  window.SenOSUsers = { render, renderSelf };
})();
