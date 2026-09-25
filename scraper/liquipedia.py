"""Scraper de Liquipedia (Counter-Strike) -> data/players/<slug>.json

Uso:
    python scraper/liquipedia.py            # todos los jugadores de players.json
    python scraper/liquipedia.py nch        # solo uno
    python scraper/liquipedia.py --missing  # solo los que todavía no tienen datos

Respeta los términos de la API de Liquipedia:
- User-Agent propio y gzip
- action=parse: 1 pedido cada 30 s; resto: 1 cada 2 s
Los datos de Liquipedia son CC BY-SA 3.0: la página muestra la atribución y el link a la fuente.
"""
import datetime as dt
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYERS = os.path.join(ROOT, "players.json")
OUT_DIR = os.path.join(ROOT, "data", "players")

WIKI = "https://liquipedia.net/counterstrike"
API = WIKI + "/api.php"
HEADERS = {
    "User-Agent": "CS2-CARD/1.0 (B4IT STUDIO NFC player card; fan project; +https://liquipedia.net/api-terms-of-use)",
    "Accept-Encoding": "gzip",
}
PARSE_GAP = 31.0
QUERY_GAP = 2.5

_last = {"parse": 0.0, "query": 0.0}


def _wait(kind):
    gap = PARSE_GAP if kind == "parse" else QUERY_GAP
    # cualquier pedido respeta al menos el intervalo corto
    since = time.time() - max(_last.values())
    since_kind = time.time() - _last[kind]
    delay = max(gap - since_kind, QUERY_GAP - since, 0)
    if delay > 0:
        time.sleep(delay)
    _last[kind] = time.time()


def api_get(params, kind="query"):
    _wait(kind)
    params = dict(params, format="json", formatversion=2)
    for attempt in range(4):
        r = requests.get(API, params=params, headers=HEADERS, timeout=60)
        if r.status_code == 429:
            time.sleep(60 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Liquipedia rate limit (429) persistente")


def existing_pages(page):
    """Resuelve redirecciones y devuelve {'main': título, 'results': bool, 'coaching': bool}"""
    titles = [page, page + "/Results", page + "/Coaching"]
    d = api_get({"action": "query", "titles": "|".join(titles), "redirects": 1})
    q = d.get("query", {})
    redirects = {r["from"]: r["to"] for r in q.get("redirects", [])}
    ok = {p["title"] for p in q.get("pages", []) if not p.get("missing") and not p.get("invalid")}
    main = redirects.get(page, page)
    if main not in ok:
        raise ValueError(f"No existe la página '{page}' en Liquipedia")
    return {
        "main": main,
        "results": redirects.get(page + "/Results", page + "/Results") in ok,
        "coaching": redirects.get(page + "/Coaching", page + "/Coaching") in ok,
    }


def parse_html(title):
    d = api_get({"action": "parse", "page": title, "prop": "text", "redirects": 1}, kind="parse")
    return BeautifulSoup(d["parse"]["text"], "html.parser")


# ---------- helpers ----------
def txt(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip() if el else ""


def money(s):
    m = re.search(r"\$\s?([\d,]+(?:\.\d+)?)", s or "")
    return float(m.group(1).replace(",", "")) if m else 0.0


def abs_url(href):
    if not href:
        return None
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("/"):
        return "https://liquipedia.net" + href
    return href


def iso_date(s):
    m = re.search(r"(\w+ \d{1,2}, \d{4})", s or "")
    if not m:
        return None
    try:
        return dt.datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat()
    except ValueError:
        return None


# ---------- página principal ----------
def parse_main(soup, title):
    data = {}
    box = soup.select_one(".fo-nttax-infobox")
    info = {}
    if box:
        head = box.select_one(".infobox-header")
        if head:
            for s in head.select(".infobox-buttons"):
                s.decompose()
            data["nick"] = txt(head).replace("[e][h]", "").strip()
        for c in box.select(".infobox-cell-2.infobox-description"):
            k = txt(c).rstrip(":")
            v = c.find_next_sibling()
            if v is None:
                continue
            for br in v.find_all("br"):
                br.replace_with("\n")
            info[k] = [x.strip() for x in v.get_text().split("\n") if x.strip()] if k in ("Games", "Alternate IDs") else txt(v)

        # redes / links
        links = []
        icons = box.select_one(".infobox-icons")
        if icons:
            for a in icons.select("a.external"):
                i = a.select_one("i.lp-icon")
                kind = next((c[3:] for c in (i.get("class") if i else []) if c.startswith("lp-") and c != "lp-icon"), "web")
                links.append({"type": kind, "url": a.get("href")})
        data["links"] = links

        # historial de equipos
        history = []
        hist_head = next((h for h in box.select(".infobox-header") if txt(h) == "History"), None)
        if hist_head:
            cont = hist_head.find_parent("div").find_next_sibling("div")
            game = None
            for el in cont.select_one(".infobox-center").children if cont and cont.select_one(".infobox-center") else []:
                if getattr(el, "name", None) == "b":
                    game = txt(el)
                elif getattr(el, "name", None) == "table":
                    for tr in el.select("tr"):
                        tds = tr.find_all("td")
                        if len(tds) < 2:
                            continue
                        dates = txt(tds[0]).split("—")
                        team_cell = tds[1]
                        role = None
                        extra = txt(team_cell)
                        a = team_cell.find("a")
                        team = txt(a) if a else extra
                        m = re.search(r"\(([^)]+)\)", extra)
                        if m:
                            role = m.group(1)
                        history.append({
                            "game": game,
                            "start": dates[0].strip() if dates else None,
                            "end": dates[1].strip() if len(dates) > 1 else None,
                            "team": team,
                            "role": role,
                        })
        data["history"] = history

    data["name"] = info.get("Name")
    data["romanized_name"] = info.get("Romanized Name")
    data["nationality"] = info.get("Nationality")
    data["born"] = iso_date(info.get("Born", ""))
    data["status"] = info.get("Status")
    data["role"] = info.get("Role")
    data["team"] = info.get("Team")
    data["games"] = info.get("Games") or []
    data["alternate_ids"] = info.get("Alternate IDs") or []
    data["winnings_liquipedia"] = money(info.get("Approx. Total Winnings", ""))
    data["years_active"] = {k.replace("Years Active", "").strip(" ()") or "Player": v.replace("–", "-")
                            for k, v in info.items() if k.startswith("Years Active")}
    data["infobox"] = {k: v for k, v in info.items()}

    # bio: primer párrafo con texto
    out = soup.select_one(".mw-parser-output") or soup
    for p in out.find_all("p", recursive=False):
        t = txt(p)
        if len(t) > 40:
            data["bio"] = re.sub(r'"\s+(\S+)\s+"', r'"\1"', t)
            break

    # entrevistas / prensa
    press = []
    h = out.find(id="Interviews")
    if h:
        ul = h.find_parent("div").find_next_sibling(["ul", "div"])
        for li in (ul.select("li") if ul else []):
            a = li.select_one("a.external")
            press.append({"text": txt(li), "url": a.get("href") if a else None})
    data["press"] = press

    # tablas de logros del overview (fallback si no hay subpáginas)
    over = {"player": [], "coach": []}
    tabs = out.select_one("#Achievements")
    tabs = tabs.find_parent("div").find_next_sibling("div") if tabs else None
    if tabs and tabs.select_one("[data-tabs-dynamic]"):
        labels = [txt(li) for li in tabs.select("ul.tabs li") if "show-all" not in (li.get("class") or [])]
        for i, lab in enumerate(labels, start=1):
            c = tabs.select_one(f".content{i}")
            key = "coach" if "Coach" in lab else "player"
            over[key] += parse_results_table(c)
    elif tabs:
        over["player"] = parse_results_table(tabs)
    data["_overview_tables"] = over
    data["page"] = title
    return data


# ---------- tablas de resultados ----------
def parse_results_table(root):
    rows = []
    if root is None:
        return rows
    for table in root.select("table.table2__table"):
        head = table.select_one("tr.table2__row--head-title")
        cols = []
        for th in head.find_all("th") if head else []:
            name = txt(th).lower()
            span = int(th.get("colspan", 1))
            if name == "tournament" and span == 2:
                cols += ["tournament_icon", "tournament"]
            elif name == "result" and span == 2:
                cols += ["score", "opponent"]
            else:
                cols += [name] + [name + f"_{i}" for i in range(1, span)]
        for tr in table.select("tr.table2__row--body"):
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue
            c = dict(zip(cols, tds))
            r = {}
            r["date"] = txt(c.get("date"))
            pl = c.get("place")
            r["place"] = txt(pl.select_one(".placement-text") if pl else None) or txt(pl)
            m = re.match(r"(\d+)", (pl.get("data-sort-value") or "") if pl else "") or re.match(r"(\d+)", r["place"])
            r["place_rank"] = int(m.group(1)) if m else None
            r["tier"] = txt(c.get("tier"))
            r["type"] = txt(c.get("type"))
            g = c.get("g.")
            gi = g.find("img") if g else None
            r["game"] = gi.get("alt") if gi else None
            t = c.get("tournament")
            a = t.find("a") if t else None
            r["tournament"] = txt(t)
            r["tournament_url"] = abs_url(a.get("href")) if a else None
            for key in ("team", "opponent"):
                cell = c.get(key)
                if cell is None:
                    r[key] = None
                    r[key + "_full"] = None
                    continue
                name = cell.select_one(".name")
                icon_link = cell.select_one(".team-template-image-icon a")
                r[key] = txt(name) or txt(cell) or None
                r[key + "_full"] = icon_link.get("title") if icon_link else r[key]
            r["score"] = txt(c.get("score")).replace(" ", " ")
            r["prize"] = txt(c.get("prize"))
            r["prize_value"] = money(r["prize"])
            rows.append(r)
    return rows


# ---------- estadísticas ----------
def is_main(r):
    """Torneo principal (no clasificatorio ni showmatch)"""
    return r["tier"] not in ("Qualifier", "Showmatch", "Misc")


def stats(rows):
    years = {}
    for r in rows:
        y = r["date"][:4]
        if y.isdigit():
            years.setdefault(y, {"events": 0, "wins": 0, "podiums": 0, "prize": 0.0})
            years[y]["events"] += 1
            years[y]["prize"] += r["prize_value"]
            if r["place_rank"] == 1 and is_main(r):
                years[y]["wins"] += 1
            if r["place_rank"] and r["place_rank"] <= 3 and is_main(r):
                years[y]["podiums"] += 1
    wins = [r for r in rows if r["place_rank"] == 1 and is_main(r)]
    teams = {}
    for r in rows:
        if r.get("team_full"):
            teams[r["team_full"]] = teams.get(r["team_full"], 0) + 1
    tiers = {}
    for r in rows:
        tiers[r["tier"]] = tiers.get(r["tier"], 0) + 1
    return {
        "events": len(rows),
        "wins": len(wins),
        "podiums": sum(1 for r in rows if r["place_rank"] and r["place_rank"] <= 3 and is_main(r)),
        "finals": sum(1 for r in rows if r["place_rank"] and r["place_rank"] <= 2 and is_main(r)),
        "qualifiers_won": sum(1 for r in rows if r["place_rank"] == 1 and r["tier"] == "Qualifier"),
        "main_events": sum(1 for r in rows if is_main(r)),
        "prize_total": round(sum(r["prize_value"] for r in rows), 2),
        "first_year": min(years) if years else None,
        "last_year": max(years) if years else None,
        "by_year": dict(sorted(years.items())),
        "top_teams": sorted(teams.items(), key=lambda kv: -kv[1])[:5],
        "tiers": tiers,
        "best_prize": max(rows, key=lambda r: r["prize_value"]) if rows and max(r["prize_value"] for r in rows) > 0 else None,
    }


def scrape(player):
    page = player["page"]
    pages = existing_pages(page)
    main = parse_main(parse_html(pages["main"]), pages["main"])
    results = parse_results_table(parse_html(pages["main"] + "/Results")) if pages["results"] else main["_overview_tables"]["player"]
    coaching = parse_results_table(parse_html(pages["main"] + "/Coaching")) if pages["coaching"] else main["_overview_tables"]["coach"]
    main.pop("_overview_tables", None)

    all_rows = results + coaching
    first_years = [int(v[:4]) for v in main["years_active"].values() if v[:4].isdigit()]
    data = {
        "slug": player["slug"],
        **main,
        "source_url": f"{WIKI}/{pages['main'].replace(' ', '_')}",
        "license": "CC BY-SA 3.0",
        "updated": dt.date.today().isoformat(),
        "since": min(first_years) if first_years else (int(stats(all_rows)["first_year"]) if all_rows else None),
        "results": results,
        "coaching": coaching,
        "stats": {
            "player": stats(results),
            "coach": stats(coaching),
            "all": stats(all_rows),
        },
        # campos editables a mano en players.json (tienen prioridad)
        "custom": {k: v for k, v in player.items() if k not in ("slug", "page")},
    }
    return data


def main(argv):
    players = json.load(open(PLAYERS, encoding="utf-8"))
    missing_only = "--missing" in argv
    only = set(a.lower() for a in argv[1:] if not a.startswith("--"))
    os.makedirs(OUT_DIR, exist_ok=True)
    failed = []
    for p in players:
        if only and p["slug"] not in only:
            continue
        if missing_only and os.path.exists(os.path.join(OUT_DIR, p["slug"] + ".json")):
            continue
        print(f"-> {p['slug']} ({p['page']})", flush=True)
        try:
            data = scrape(p)
        except Exception as e:  # se conserva el JSON anterior si falla
            print(f"   ERROR: {e}", flush=True)
            failed.append(p["slug"])
            continue
        path = os.path.join(OUT_DIR, p["slug"] + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        s = data["stats"]["all"]
        print(f"   ok: {s['events']} torneos, {s['wins']} títulos, ${s['prize_total']:,.0f}", flush=True)
    if failed:
        print("Fallaron:", ", ".join(failed))
    return 1 if failed and len(failed) == len(players) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
