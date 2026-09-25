/* CS2-CARD — render del perfil. Datos: window.__PLAYER__ (inyectado por build.py) o ?data=archivo.json */
(async function () {
  "use strict";

  // ---------- datos ----------
  let P = window.__PLAYER__;
  if (!P) {
    const src = new URLSearchParams(location.search).get("data") || "sample-data/nch.json";
    P = await fetch(src).then(r => r.json());
  }
  const C = P.custom || {};          // opciones por jugador desde players.json
  const nick = C.nick || P.nick || P.page;

  // ---------- personalización por jugador ----------
  // theme: colores; hide: secciones a ocultar; tabs: nombres de pestañas; photo: imagen propia
  const THEME_VARS = { accent: ["--orange", "--orange-2"], bg: ["--bg"], bg2: ["--bg2"], card: ["--card"], line: ["--line"], text: ["--text"], muted: ["--muted"] };
  Object.entries(C.theme || {}).forEach(([k, v]) => (THEME_VARS[k] || ["--" + k]).forEach(n => document.documentElement.style.setProperty(n, v)));
  const HIDE = new Set(C.hide || []);
  const SECTIONS = { ask: ".ask", chips: "#chips", headline: "#headline", socials: "#socials", stats: "#stats", split: "#split",
    chart: "#chart", highlights: "#highlights", timeline: "#timeline", bio: "#bio-card", footer: ".foot", intro: "#intro" };

  // ---------- utilidades ----------
  const $ = s => document.querySelector(s);
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const usd = (v, compact) => new Intl.NumberFormat("es-AR", { style: "currency", currency: "USD", maximumFractionDigits: 0, notation: compact && v >= 100000 ? "compact" : "standard" }).format(v || 0);
  const MES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  const fdate = d => { const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(d || ""); return m ? `${+m[3]} ${MES[+m[2] - 1]} ${m[1]}` : (d || ""); };
  const place = p => (p || "").replace(/(\d+)(st|nd|rd|th)/g, "$1°").replace(/\s*-\s*/g, "–");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const FLAGS = { Argentina: "ar", Brazil: "br", Chile: "cl", Uruguay: "uy", Paraguay: "py", Peru: "pe", Bolivia: "bo", Colombia: "co", Venezuela: "ve", Ecuador: "ec", Mexico: "mx", "United States": "us", Canada: "ca", Spain: "es", Portugal: "pt", France: "fr", Germany: "de", Italy: "it", "United Kingdom": "gb", Poland: "pl", Denmark: "dk", Sweden: "se", Norway: "no", Finland: "fi", Russia: "ru", Ukraine: "ua", Kazakhstan: "kz", Latvia: "lv", Estonia: "ee", Lithuania: "lt", Czechia: "cz", "Czech Republic": "cz", Slovakia: "sk", Hungary: "hu", Romania: "ro", Bulgaria: "bg", Serbia: "rs", "Bosnia and Herzegovina": "ba", Croatia: "hr", Slovenia: "si", Turkey: "tr", Israel: "il", Netherlands: "nl", Belgium: "be", Switzerland: "ch", Austria: "at", Australia: "au", "New Zealand": "nz", China: "cn", Mongolia: "mn", Japan: "jp", "South Korea": "kr", Indonesia: "id", Philippines: "ph", Malaysia: "my", Singapore: "sg", "South Africa": "za", Belarus: "by", Georgia: "ge", Armenia: "am", Uzbekistan: "uz" };
  const COUNTRY_ES = { Argentina: "Argentina", Brazil: "Brasil", Chile: "Chile", Uruguay: "Uruguay", Paraguay: "Paraguay", Peru: "Perú", Colombia: "Colombia", Mexico: "México", "United States": "Estados Unidos", Spain: "España" };
  // bandera como imagen (Windows no dibuja emojis de banderas)
  const flag = c => { const k = FLAGS[c]; return k ? `<img class="flag" src="https://flagcdn.com/w40/${k}.png" alt="" width="20" height="15">` : "🌐"; };

  const STATUS_ES = { Active: "Activo", Retired: "Retirado", Inactive: "Inactivo" };
  const ROLE_ES = { Coach: "Coach", Rifler: "Rifler", AWPer: "AWPer", "In-game leader": "IGL", Support: "Support", Entry: "Entry", Lurker: "Lurker", Analyst: "Analista", Manager: "Manager" };

  const SOC = {
    instagram: ["Instagram", "#e1306c", "IG"], twitter: ["X", "#1d1d1f", "X"], twitch: ["Twitch", "#9146ff", "TW"],
    youtube: ["YouTube", "#ff0033", "YT"], tiktok: ["TikTok", "#111", "TT"], kick: ["Kick", "#53fc18", "K"],
    facebook: ["Facebook", "#1877f2", "f"], steam: ["Steam", "#1b2838", "ST"], faceit: ["FACEIT", "#ff5500", "FC"],
    esea: ["ESEA", "#0b8a3e", "E"], gamersclub: ["Gamers Club", "#1c6dd0", "GC"], hltv: ["HLTV", "#2b6ea6", "H"],
    discord: ["Discord", "#5865f2", "DC"], home: ["Web", "#444", "W"], web: ["Link", "#444", "↗"], vk: ["VK", "#0077ff", "VK"],
    bilibili: ["bilibili", "#00a1d6", "B"], weibo: ["Weibo", "#e6162d", "WB"], liquipedia: ["Liquipedia", "#2b4a7e", "LP"],
  };

  // ---------- derivados ----------
  const S = P.stats || {};
  const all = S.all || {}, sp = S.player || {}, sc = S.coach || {};
  const age = P.born ? Math.floor((Date.now() - new Date(P.born + "T00:00:00")) / 3.15576e10) : null;
  const since = C.since || P.since || all.first_year;
  const years = since ? (new Date().getFullYear() - since) : null;

  document.title = `${nick} · CS2-CARD`;

  // ---------- INTRO ----------
  const intro = $("#intro"), app = $("#app");
  function scramble(target, text, ms) {
    if (reduced) { target.textContent = text; return; }
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#$%&*<>/";
    let t0 = null;
    requestAnimationFrame(function frame(t) {
      if (t0 === null) t0 = t;
      const k = Math.min(1, Math.max(0, (t - t0) / ms));
      const n = Math.floor(k * text.length);
      target.textContent = text.slice(0, n) + [...text.slice(n)].map(c => c === " " ? " " : chars[(Math.random() * chars.length) | 0]).join("");
      if (k < 1) requestAnimationFrame(frame); else target.textContent = text;
    });
  }
  let introDone = false;
  function endIntro() {
    if (introDone) return; introDone = true;
    intro.classList.add("out");
    document.body.classList.remove("locked");
    setTimeout(() => intro.remove(), 650);
    app.hidden = false;
    requestAnimationFrame(() => { $(".hero").classList.add("shown"); countUpVisible(); });
  }
  document.body.classList.add("locked");
  intro.addEventListener("click", endIntro);
  if (HIDE.has("intro")) { endIntro(); }
  const st = $("#intro-status");
  const IT = C.intro || {};
  setTimeout(() => (st.textContent = IT.reading || "LEYENDO CS2-CARD"), 550);
  setTimeout(() => { st.textContent = IT.found || "PERFIL ENCONTRADO"; scramble($("#intro-nick"), (IT.title || nick).toUpperCase(), 700); }, 1000);
  setTimeout(endIntro, reduced ? 300 : (IT.duration || 2500));

  // ---------- HERO ----------
  $("#nick").textContent = nick;
  if (C.ask) $(".ask").textContent = C.ask;
  if (C.photo) {
    const ph = el("div", "hero-photo"); ph.style.backgroundImage = `url("${C.photo}")`;
    $(".hero").insertBefore(ph, $(".hero-inner"));
  }
  const nm = C.name || P.name;
  $("#realname").textContent = nm ? nm : "";
  const chips = $("#chips");
  const ctry = P.nationality;
  if (ctry) chips.append(el("span", "chip", `${flag(ctry)} ${esc(COUNTRY_ES[ctry] || ctry)}`));
  const role = C.role || P.role;
  if (role) chips.append(el("span", "chip o", esc(ROLE_ES[role] || role)));
  if (P.team) chips.append(el("span", "chip", esc(P.team)));
  if (P.status) chips.append(el("span", "chip", esc(STATUS_ES[P.status] || P.status)));
  if (since) chips.append(el("span", "chip", `Desde ${since}`));
  if (age) chips.append(el("span", "chip", `${age} años`));

  // resumen en español armado con los datos
  const parts = [];
  const ya = P.years_active || {};
  if (ya.Player) parts.push(`jugador (${ya.Player.replace(" - ", "–")})`);
  if (ya.Coach) parts.push(`coach (${ya.Coach.replace(" - ", "–")})`);
  let head = C.tagline || "";
  if (!head) {
    head = years ? `${years} años en la escena` : "";
    if (parts.length) head += (head ? " como " : "Como ") + parts.join(" y ");
    head += head ? ". " : "";
    head += `${all.events || 0} torneos registrados, ${all.wins || 0} títulos y ${all.podiums || 0} podios.`;
  }
  $("#headline").textContent = head;

  const socials = $("#socials");
  (C.links || P.links || []).forEach(l => {
    const [label, color, abbr] = SOC[l.type] || [l.type, "#444", "↗"];
    const a = el("a", "soc", `<span class="b" style="background:${color}">${esc(abbr)}</span>${esc(label)}`);
    a.href = l.url; a.target = "_blank"; a.rel = "noopener";
    socials.append(a);
  });

  // ---------- TABS ----------
  const TL = C.tabs || {};
  const tabs = [
    { id: "overview", label: TL.overview || "Overview" },
    { id: "results", label: TL.results || "Results", n: (P.results || []).length },
    { id: "coaching", label: TL.coaching || "Coaching", n: (P.coaching || []).length },
  ].filter(t => (t.id === "overview" || t.n) && !HIDE.has("tab-" + t.id));
  const nav = $("#tabs");
  tabs.forEach((t, i) => {
    const b = el("button", "tab", `${t.label}${t.n ? `<span class="n">${t.n}</span>` : ""}`);
    b.setAttribute("role", "tab"); b.dataset.tab = t.id; b.setAttribute("aria-selected", i === 0);
    b.addEventListener("click", () => select(t.id, true));
    nav.append(b);
  });
  const rendered = {};
  function select(id, scroll) {
    nav.querySelectorAll(".tab").forEach(b => b.setAttribute("aria-selected", b.dataset.tab === id));
    ["overview", "results", "coaching"].forEach(p => { $("#panel-" + p).hidden = p !== id; });
    if (!rendered[id] && id !== "overview") { renderList(id, "all"); rendered[id] = true; }
    if (scroll && nav.getBoundingClientRect().top <= 0) window.scrollTo({ top: nav.offsetTop, behavior: reduced ? "auto" : "smooth" });
    history.replaceState(null, "", id === "overview" ? location.pathname + location.search : "#" + id);
    if (id === "overview") countUpVisible();
  }

  // ---------- OVERVIEW ----------
  const stats = $("#stats");
  const statDefs = [
    { v: all.wins || 0, k: "Títulos", s: `${all.finals || 0} finales` },
    { v: all.podiums || 0, k: "Podios", s: "top 3 en torneos" },
    { v: all.events || 0, k: "Torneos", s: `${all.main_events || 0} + ${(all.events || 0) - (all.main_events || 0)} clasificatorios` },
    { v: years || 0, k: "Años de carrera", s: since ? `desde ${since}` : "" },
    { v: all.prize_total || 0, k: "Premios ganados", s: "premios de equipo en torneos", money: true, wide: true },
    { v: P.winnings_liquipedia || 0, k: "Ganancias aprox.", s: "individual · Liquipedia", money: true, wide: true, hideIfZero: true },
  ];
  statDefs.filter(d => !(d.hideIfZero && !d.v)).forEach(d => {
    const s = el("div", "stat" + (d.wide ? " wide" : ""), `<div class="v" data-to="${d.v}" data-money="${d.money ? 1 : 0}">${d.money ? usd(d.v, true) : d.v}</div><div class="k">${d.k}</div><div class="s">${esc(d.s)}</div>`);
    stats.append(s);
  });
  function countUpVisible() {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      const box = e.target, v = box.querySelector(".v");
      if (!v) return;
      box.classList.add("in");
      const to = +v.dataset.to, money = v.dataset.money === "1", dur = reduced ? 1 : 1300;
      let t0 = null;
      requestAnimationFrame(function f(t) {
        if (t0 === null) t0 = t;
        const k = Math.min(1, Math.max(0, (t - t0) / dur)), e2 = 1 - Math.pow(1 - k, 3), x = to * e2;
        v.textContent = money ? usd(x, true) : Math.round(x);
        if (k < 1) requestAnimationFrame(f);
      });
    }), { threshold: .3 });
    stats.querySelectorAll(".stat:not(.in)").forEach(s => io.observe(s));
  }

  const split = $("#split");
  if (sp.events) split.append(el("div", "", `<b><i>▸</i> Como jugador</b>${sp.events} torneos · ${sp.wins} títulos · ${usd(sp.prize_total)}`));
  if (sc.events) split.append(el("div", "", `<b><i>▸</i> Como coach</b>${sc.events} torneos · ${sc.wins} títulos · ${usd(sc.prize_total)}`));
  if (!split.children.length) split.remove();

  // gráfico por año
  const chart = $("#chart");
  const by = all.by_year || {};
  const ys = Object.keys(by);
  if (ys.length) {
    const y0 = +ys[0], y1 = +ys[ys.length - 1];
    const max = Math.max(...Object.values(by).map(v => v.events), 1);
    for (let y = y0; y <= y1; y++) {
      const v = by[y] || { events: 0, wins: 0 };
      const b = el("div", "bar", `<span class="c">${v.events || ""}</span><div class="col" style="height:${(v.events / max) * 100}%;animation-delay:${(y - y0) * 45}ms"><div class="win" style="height:${v.events ? (v.wins / v.events) * 100 : 0}%"></div></div><span class="y">'${String(y).slice(2)}</span>`);
      b.title = `${y}: ${v.events} torneos, ${v.wins} títulos`;
      chart.append(b);
    }
    new IntersectionObserver((es, o) => es.forEach(e => {
      if (!e.isIntersecting) return; o.disconnect();
      chart.classList.add("in");
    }), { threshold: .35 }).observe(chart);
  } else chart.closest(".card").remove();

  // mejores resultados: por puesto, luego tier, luego premio
  const tierRank = t => ({ "S-Tier": 0, "A-Tier": 1, "B-Tier": 2, "C-Tier": 3, "D-Tier": 4, "Monthly": 5, "Weekly": 6 }[t] ?? 8);
  const allRows = [...(P.results || []).map(r => ({ ...r, _as: "Jugador" })), ...(P.coaching || []).map(r => ({ ...r, _as: "Coach" }))];
  const best = allRows.filter(r => r.place_rank && r.tier !== "Qualifier")
    .sort((a, b) => (a.place_rank - b.place_rank) || (tierRank(a.tier) - tierRank(b.tier)) || (b.prize_value - a.prize_value) || b.date.localeCompare(a.date))
    .slice(0, 6);
  const hl = $("#highlights");
  best.forEach((r, i) => hl.append(rowEl(r, i, true)));
  if (!best.length) hl.closest(".card").remove();

  // trayectoria
  const tl = $("#timeline");
  const hist = (P.history || []).slice().reverse();
  $("#teams-count").textContent = hist.length ? `${new Set(hist.map(h => h.team)).size} equipos` : "";
  let lastGame = null;
  hist.forEach(h => {
    if (h.game !== lastGame) { tl.append(el("li", "in", `<div class="gm">${esc(h.game || "")}</div>`)); lastGame = h.game; }
    const clean = s => (s || "").replace(/\?\?/g, "··").replace(/-\?\?/g, "");
    const end = h.end ? clean(h.end) : "presente";
    tl.append(el("li", h.role ? "coach" : "", `<span class="tm">${esc(h.team)}</span>${h.role ? `<span class="rl">${esc(h.role)}</span>` : ""}<div class="dt">${esc(clean(h.start))} → ${esc(end)}</div>`));
  });
  if (!hist.length) tl.closest(".card").remove();
  const tio = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); tio.unobserve(e.target); } }), { threshold: .2 });
  tl.querySelectorAll("li:not(.in)").forEach((li, i) => { li.style.animationDelay = (i % 6) * 60 + "ms"; tio.observe(li); });

  // bio y prensa
  const bio = C.bio || P.bio;
  if (bio) $("#bio").textContent = bio; else $("#bio").remove();
  const press = $("#press");
  (P.press || []).forEach(p => {
    const a = el(p.url ? "a" : "div", "press", "📰 " + esc(p.text));
    if (p.url) { a.href = p.url; a.target = "_blank"; a.rel = "noopener"; }
    press.append(a);
  });
  if (!bio && !(P.press || []).length) $("#bio-card").remove();

  // ---------- RESULTS / COACHING ----------
  const FILTERS = [
    { id: "all", label: "Todos", f: () => true },
    { id: "wins", label: "🏆 Títulos", f: r => r.place_rank === 1 && r.tier !== "Qualifier" },
    { id: "top3", label: "Top 3", f: r => r.place_rank && r.place_rank <= 3 && r.tier !== "Qualifier" },
    { id: "prize", label: "Con premio", f: r => r.prize_value > 0 },
    { id: "lan", label: "LAN", f: r => /Offline/.test(r.type) },
    { id: "main", label: "Sin clasificatorios", f: r => r.tier !== "Qualifier" },
  ];
  document.querySelectorAll(".filters").forEach(box => {
    const key = box.dataset.for;
    FILTERS.forEach(F => {
      const b = el("button", "fbtn", F.label);
      b.setAttribute("aria-pressed", F.id === "all");
      b.addEventListener("click", () => {
        box.querySelectorAll(".fbtn").forEach(x => x.setAttribute("aria-pressed", x === b));
        renderList(key, F.id);
      });
      box.append(b);
    });
  });

  function rowEl(r, i, showAs) {
    const a = el(r.tournament_url ? "a" : "div", "row");
    if (r.tournament_url) { a.href = r.tournament_url; a.target = "_blank"; a.rel = "noopener"; }
    a.style.animationDelay = reduced ? "0ms" : Math.min(i, 14) * 35 + "ms";
    const pc = r.place_rank && r.place_rank <= 3 && r.tier !== "Qualifier" ? " p" + r.place_rank : "";
    const pl = place(r.place);
    const [p1, p2] = pl.split("–");
    const vs = r.score ? `<div class="vs">${esc(r.team || "")} <b>${esc(r.score)}</b> ${esc(r.opponent || "")}</div>` : (r.team ? `<div class="vs">${esc(r.team)}</div>` : "");
    a.innerHTML = `
      <div class="place${pc}">${esc(p1 || "–")}${p2 ? `<small>a ${esc(p2)}</small>` : ""}</div>
      <div><div class="t">${esc(r.tournament)}</div>
        <div class="m"><span>${fdate(r.date)}</span><span class="tier">${esc(r.tier)}</span><span>${r.type === "Offline" ? "LAN" : esc(r.type)}</span>${showAs ? `<span>${r._as}</span>` : ""}</div>${vs}</div>
      <div class="pr${r.prize_value ? "" : " z"}">${r.prize_value ? usd(r.prize_value) : "—"}</div>`;
    return a;
  }

  function renderList(key, fid) {
    const box = $("#list-" + key);
    const F = FILTERS.find(x => x.id === fid) || FILTERS[0];
    const rows = (P[key] || []).filter(F.f).slice().sort((a, b) => b.date.localeCompare(a.date));
    box.innerHTML = "";
    const tot = rows.reduce((s, r) => s + (r.prize_value || 0), 0);
    box.append(el("div", "summary", `<b>${rows.length}</b> torneos · <b>${rows.filter(r => r.place_rank === 1 && r.tier !== "Qualifier").length}</b> títulos · <b>${usd(tot)}</b> en premios`));
    if (!rows.length) { box.append(el("div", "empty", "Sin resultados para este filtro.")); return; }
    let yr = null, i = 0;
    const byYear = {};
    rows.forEach(r => { const y = r.date.slice(0, 4); byYear[y] = (byYear[y] || 0) + 1; });
    rows.forEach(r => {
      const y = r.date.slice(0, 4);
      if (y !== yr) { yr = y; box.append(el("div", "yearh", `${y} <span>${byYear[y]}</span>`)); i = 0; }
      box.append(rowEl(r, i++));
    });
  }

  // ---------- footer ----------
  const src = $("#src"); src.href = P.source_url || "https://liquipedia.net/counterstrike/";
  $("#updated").textContent = fdate(P.updated);

  // secciones ocultas por configuración
  HIDE.forEach(k => { const e = SECTIONS[k] && $(SECTIONS[k]); if (!e) return; (e.closest(".card") || e).remove(); });

  const h = location.hash.slice(1);
  if (tabs.some(t => t.id === h)) select(h);
  else if (tabs[0] && tabs[0].id !== "overview") select(tabs[0].id);

  // gancho para custom.js de cada jugador
  window.CS2CARD = { data: P, select };
  document.dispatchEvent(new CustomEvent("cs2card:ready", { detail: P }));
})();
