# CS2-CARD: diseño de la interfaz

Esta carpeta es **solo la interfaz**. Se puede rediseñar entera (por ejemplo con Claude Design) sin tocar el scraper ni el build.

| Archivo | Qué es |
|---|---|
| `index.html` | estructura. Dejá `<!--META-->` y `<!--DATA-->`: ahí el build inyecta los meta tags y los datos del jugador |
| `styles.css` | estilos y animaciones |
| `app.js` | lee los datos y arma la página |
| `sample-data/nch.json` | datos reales de ejemplo (NCH) para diseñar |

Para ver el diseño solo, sin el build, levantá un servidor en esta carpeta y abrí `index.html`. Sin datos inyectados, carga `sample-data/nch.json` o lo que pases con `?data=archivo.json`.

```bash
python -m http.server 8000
```

El build (`../build.py`) copia `styles.css` y `app.js` a `site/assets/`. El `index.html` lo usa como plantilla: una copia por jugador con los datos embebidos.

## Datos disponibles (`window.__PLAYER__`)

```text
slug, page, nick, name, nationality, born (YYYY-MM-DD), status, role, team,
games[], alternate_ids[], years_active {Player, Coach}, since (año),
winnings_liquipedia (USD), bio, links[{type, url}], press[{text, url}],
history[{game, start, end, team, role}],
results[] y coaching[]: {date, place, place_rank, tier, type, game, tournament,
                         tournament_url, team, team_full, opponent, opponent_full,
                         score, prize, prize_value}
stats.{all|player|coach}: {events, main_events, wins, podiums, finals, qualifiers_won,
                           prize_total, first_year, last_year,
                           by_year{YYYY:{events,wins,podiums,prize}}, top_teams, tiers, best_prize}
custom: overrides cargados a mano en players.json (nick, name, role, tagline, bio, links, since)
source_url, license, updated
```

Mantené visible la atribución a Liquipedia (licencia CC BY-SA 3.0).
