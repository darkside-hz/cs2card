"""Arma el sitio estático en site/ a partir de design/ + data/players/*.json

    python build.py

Salida:
    site/index.html              portada con la lista de jugadores
    site/<slug>/index.html       perfil (datos embebidos: carga instantánea al escanear)
    site/assets/                 styles.css, app.js (copiados de design/)
    site/data/<slug>.json
    qr/<slug>.png                QR del link de cada jugador (si hay base_url en site.json)

Personalización por jugador (el link del NFC nunca cambia, solo lo que se sirve en él):
    players.json                 opciones: theme, hide, tabs, intro, tagline, nick, bio, links...
    design/jugadores/<slug>/     custom.css / custom.js se suman al diseño base;
                                 index.html (opcional) reemplaza la plantilla entera;
                                 cualquier otro archivo (fotos, videos) se publica junto a la página.
"""
import html
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.join(ROOT, "design")
DATA = os.path.join(ROOT, "data", "players")
SITE = os.path.join(ROOT, "site")
CONF = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
BASE = (os.environ.get("BASE_URL") or CONF.get("base_url", "")).rstrip("/")


def player_page(tpl, p, own):
    """own: carpeta design/jugadores/<slug>/ (puede no existir)"""
    nick = (p.get("custom") or {}).get("nick") or p.get("nick") or p["slug"]
    s = p.get("stats", {}).get("all", {})
    desc = f"{s.get('events', 0)} torneos · {s.get('wins', 0)} títulos · {s.get('podiums', 0)} podios. Perfil CS2-CARD con datos de Liquipedia."
    url = f"{BASE}/{p['slug']}/" if BASE else ""
    meta = "\n".join([
        f'<meta name="description" content="{html.escape(desc)}">',
        f'<meta property="og:title" content="{html.escape(nick)} · CS2-CARD">',
        f'<meta property="og:description" content="{html.escape(desc)}">',
        f'<meta property="og:type" content="profile">',
        f'<meta property="og:url" content="{url}">' if url else "",
    ])
    data = json.dumps(p, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    out = tpl.replace("<!--META-->", meta)
    out = out.replace("<title>CS2-CARD</title>", f"<title>{html.escape(nick)} · CS2-CARD</title>")
    out = out.replace('href="styles.css"', 'href="../assets/styles.css"')
    out = out.replace('src="app.js"', 'src="../assets/app.js"')
    out = out.replace("<!--DATA-->", f"<script>window.__PLAYER__={data};</script>")
    if os.path.exists(os.path.join(own, "custom.css")):
        out = out.replace("</head>", '<link rel="stylesheet" href="custom.css">\n</head>')
    if os.path.exists(os.path.join(own, "custom.js")):
        out = out.replace("</body>", '<script src="custom.js"></script>\n</body>')
    return out


def index_page(players):
    cards = "\n".join(
        f'<a class="row" style="animation-delay:{i * 60}ms" href="{p["slug"]}/">'
        f'<div class="place p1">{html.escape((p.get("nick") or p["slug"])[:2].upper())}</div>'
        f'<div><div class="t">{html.escape(p.get("nick") or p["slug"])}</div>'
        f'<div class="m"><span>{html.escape(p.get("name") or "")}</span></div></div>'
        f'<div class="pr">{p.get("stats", {}).get("all", {}).get("wins", 0)} 🏆</div></a>'
        for i, p in enumerate(players))
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#0b0b0c">
<title>CS2-CARD</title>
<link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/styles.css"></head><body>
<header class="hero shown"><div class="hero-stripes"><i></i><i></i></div><div class="hero-inner">
<div class="brand">CS2-CARD <span>//</span> B4IT STUDIO</div>
<p class="ask reveal">¿VOS TENÉS NICK?</p><h1 class="nick reveal">CS2-CARD</h1>
<p class="headline reveal">Tarjetas NFC para jugadores de Counter-Strike. Apoyá el celular en la tarjeta y mirá el perfil.</p>
</div></header>
<main><div class="list">{cards}</div></main>
<footer class="foot"><div>Datos de <a href="https://liquipedia.net/counterstrike/">Liquipedia</a> · CC BY-SA 3.0</div><div class="foot-brand">CS2-CARD · B4IT STUDIO</div></footer>
</body></html>"""


def qr(slug):
    if not BASE:
        return None
    import qrcode
    d = os.path.join(ROOT, "qr")
    os.makedirs(d, exist_ok=True)
    img = qrcode.make(f"{BASE}/{slug}/", border=2, box_size=16)
    path = os.path.join(d, f"{slug}.png")
    img.save(path)
    return path


def main():
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    os.makedirs(os.path.join(SITE, "assets"))
    os.makedirs(os.path.join(SITE, "data"))
    for f in ("styles.css", "app.js"):
        shutil.copy(os.path.join(DESIGN, f), os.path.join(SITE, "assets", f))
    tpl = open(os.path.join(DESIGN, "index.html"), encoding="utf-8").read()

    conf = json.load(open(os.path.join(ROOT, "players.json"), encoding="utf-8"))
    seen = set()
    for entry in conf:
        slug = entry.get("slug", "")
        if not re.match(r"^[a-z0-9][a-z0-9-]{0,39}$", slug) or not entry.get("page"):
            raise SystemExit(f"players.json: entrada inválida {entry} (slug en minúsculas/números/guiones y page obligatorios)")
        if slug in seen or slug in ("assets", "data"):
            raise SystemExit(f"players.json: slug repetido o reservado '{slug}'")
        seen.add(slug)
    players = []
    for entry in conf:
        slug = entry["slug"]
        path = os.path.join(DATA, slug + ".json")
        if not os.path.exists(path):
            print(f"sin datos: {slug} (correr scraper)")
            continue
        p = json.load(open(path, encoding="utf-8"))
        # las opciones de players.json se aplican en cada build (no hace falta volver a scrapear)
        p["custom"] = {k: v for k, v in entry.items() if k not in ("slug", "page")}
        players.append(p)
        own = os.path.join(DESIGN, "jugadores", slug)
        dst = os.path.join(SITE, slug)
        if os.path.isdir(own):
            shutil.copytree(own, dst)
        else:
            os.makedirs(dst)
        own_tpl = os.path.join(own, "index.html")
        page_tpl = open(own_tpl, encoding="utf-8").read() if os.path.exists(own_tpl) else tpl
        with open(os.path.join(dst, "index.html"), "w", encoding="utf-8") as f:
            f.write(player_page(page_tpl, p, own))
        shutil.copy(path, os.path.join(SITE, "data", slug + ".json"))
        q = qr(slug)
        print(f"{slug}: {BASE + '/' + slug + '/' if BASE else '(sin base_url)'}{'  QR ok' if q else ''}")

    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page(players))
    shutil.copy(os.path.join(SITE, "index.html"), os.path.join(SITE, "404.html"))
    open(os.path.join(SITE, ".nojekyll"), "w").close()
    # copia de muestra para trabajar el diseño aparte
    if players:
        os.makedirs(os.path.join(DESIGN, "sample-data"), exist_ok=True)
        shutil.copy(os.path.join(DATA, players[0]["slug"] + ".json"), os.path.join(DESIGN, "sample-data", "nch.json" if players[0]["slug"] == "nch" else players[0]["slug"] + ".json"))
    print(f"site/ listo: {len(players)} jugador(es)")


if __name__ == "__main__":
    main()
