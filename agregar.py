"""Agrega uno o varios jugadores a players.json a partir del link de Liquipedia.

    python agregar.py https://liquipedia.net/counterstrike/Mvk
    python agregar.py https://liquipedia.net/counterstrike/Mvk --slug mvk
    python agregar.py URL1 URL2 URL3            # varios de una
    python agregar.py URL --scrape             # además baja los datos y arma el sitio local
    python agregar.py URL --dry-run            # muestra qué haría, sin tocar nada

El slug es la parte final del link que se graba en el NFC (…/cs2card/<slug>/).
Una vez grabada una tarjeta, ese slug no se cambia más.
"""
import json
import os
import re
import subprocess
import sys
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
PLAYERS = os.path.join(ROOT, "players.json")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")


def page_from_url(url):
    u = urlparse(url.strip())
    if "liquipedia.net" not in u.netloc or not u.path.startswith("/counterstrike/"):
        raise ValueError(f"No es un link de Liquipedia Counter-Strike: {url}")
    page = unquote(u.path[len("/counterstrike/"):]).strip("/")
    if not page or "/" in page:
        raise ValueError(f"Usá el link de la página principal del jugador (sin /Results, /Coaching…): {url}")
    return page.replace("_", " ")


def slug_from_page(page):
    s = re.sub(r"[^a-z0-9]+", "-", page.lower()).strip("-")
    return s[:40]


def main(argv):
    args = argv[1:]
    dry = "--dry-run" in args
    scrape = "--scrape" in args
    slug_forced = None
    if "--slug" in args:
        i = args.index("--slug")
        slug_forced = args[i + 1].lower()
        del args[i:i + 2]
    urls = [a for a in args if not a.startswith("--")]
    if not urls:
        print(__doc__)
        return 1
    if slug_forced and len(urls) > 1:
        print("--slug solo se puede usar con un link a la vez")
        return 1

    players = json.load(open(PLAYERS, encoding="utf-8"))
    slugs = {p["slug"] for p in players}
    pages = {p["page"].lower() for p in players}
    added = []
    for url in urls:
        try:
            page = page_from_url(url)
        except ValueError as e:
            print(e)
            return 1
        slug = slug_forced or slug_from_page(page)
        if not SLUG_RE.match(slug):
            print(f"slug inválido '{slug}': solo minúsculas, números y guiones")
            return 1
        if page.lower() in pages:
            print(f"ya existe: {page}")
            continue
        if slug in slugs:
            print(f"el slug '{slug}' ya está usado; elegí otro con --slug")
            return 1
        players.append({"slug": slug, "page": page})
        slugs.add(slug); pages.add(page.lower())
        added.append(slug)
        print(f"+ {page}  ->  /{slug}/")

    if dry or not added:
        print("(sin cambios)" if not added else "(dry-run: no se guardó nada)")
        return 0
    with open(PLAYERS, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"players.json: {len(players)} jugadores")

    if scrape:
        subprocess.check_call([sys.executable, os.path.join(ROOT, "scraper", "liquipedia.py"), *added])
        subprocess.check_call([sys.executable, os.path.join(ROOT, "build.py")])
    else:
        print("Listo. Al hacer push, GitHub Actions baja sus datos y publica la página.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
