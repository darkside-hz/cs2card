# CS2-CARD: perfil web del jugador para el NFC

Tocás la tarjeta con el celular, se abre el navegador y aparece un dashboard animado del jugador con datos de Liquipedia.

```text
players.json          lista de jugadores (slug = parte del link, page = página en Liquipedia)
scraper/liquipedia.py baja y procesa Liquipedia -> data/players/<slug>.json
design/               interfaz (separada, para rediseñar aparte) -> ver design/README.md
build.py              arma site/ (una página por jugador) y qr/<slug>.png
.github/workflows/    GitHub Actions: actualiza los lunes y publica en GitHub Pages (gratis)
```

## Agregar un jugador

1. Sumalo en `players.json`. El `page` es el final del link de Liquipedia: `liquipedia.net/counterstrike/NCH` → `"NCH"`.
   ```json
   { "slug": "nch", "page": "NCH" }
   ```
   Campos opcionales para pisar lo de Liquipedia: `nick`, `name`, `role`, `tagline`, `bio`, `since`, `links`.
2. Subí el cambio (commit + push). El workflow scrapea al jugador nuevo y publica.
3. El link queda en `https://USUARIO.github.io/REPO/<slug>/`. Ese es el link que se graba en el NFC.

El `slug` no se cambia nunca después de grabar la tarjeta, porque el NFC apunta a ese link.

## Personalizar a un jugador (sin tocar el NFC)

El NFC guarda solo el link `…/<slug>/`. Todo lo que se muestra en ese link se regenera en cada publicación, así que podés cambiar cualquier cosa las veces que quieras. Una vez grabada, la tarjeta no se toca más.

**Opciones en `players.json`** (se aplican al publicar, no hace falta volver a scrapear):

```json
{
  "slug": "nch", "page": "NCH",
  "theme":   { "accent": "#2f9bff", "bg": "#050608" },
  "hide":    ["intro", "chart", "highlights", "timeline", "bio", "socials", "stats", "split", "tab-coaching"],
  "tabs":    { "overview": "Resumen", "results": "Jugador", "coaching": "Coach" },
  "intro":   { "found": "COACH ENCONTRADO", "title": "NACHO", "duration": 3000 },
  "photo":   "foto.jpg",
  "ask":     "¿VOS TENÉS NICK?",
  "tagline": "Texto propio que reemplaza el resumen automático",
  "nick": "NCH", "name": "…", "role": "…", "bio": "…", "since": 2011,
  "links":   [{ "type": "instagram", "url": "https://instagram.com/…" }]
}
```

**Diseño propio por jugador:** creá `design/jugadores/<slug>/` (copiá `_ejemplo/`):
- `custom.css`: estilos que pisan el diseño base, solo para ese jugador.
- `custom.js`: lógica extra (ver el ejemplo).
- `index.html`: si existe, reemplaza la plantilla entera para ese jugador. Tenés libertad total de diseño, siempre que deje `<!--DATA-->` para los datos.
- Cualquier otro archivo (foto, video, logo) se publica junto a la página, por ejemplo `"photo": "foto.jpg"`.

Cambiar `design/index.html`, `styles.css` o `app.js` cambia a todos los jugadores a la vez.

## Grabar el NFC (NTAG213/215)

1. Instalá **NFC Tools** (gratis, iPhone y Android).
2. Andá a Escribir → Agregar registro → **URL** → pegá el link del jugador → Escribir, y apoyá el sticker.
3. Probalo con un iPhone y un Android: los dos abren el link en el navegador predeterminado sin instalar nada.
4. Opcional: en Otros → Bloquear etiqueta. **Es irreversible**: el sticker ya no se puede regrabar.

`qr/<slug>.png` es el mismo link en QR, por si el celular no tiene NFC.

## Correr local

```bash
pip install -r requirements.txt
python scraper/liquipedia.py
python build.py
python -m http.server 8765 --directory site
```

El scraper respeta los límites de la API de Liquipedia (1 página cada 30 s), así que cada jugador tarda cerca de 1,5 minutos.
