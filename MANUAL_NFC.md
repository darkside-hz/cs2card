# Manual: grabar el NFC de una CS2-CARD

Sirve para iPhone y Android. No cuesta nada: la app es gratis y el sticker es el que ya tenés.

## Qué necesitás
- El sticker NFC. Los de la foto son de unos 25 mm y entran en el hueco de 27 mm de la base. Mejor si es **NTAG213** (144 bytes, alcanza de sobra para un link) o NTAG215/216. Evitá los "Mifare Classic": los iPhone no los leen.
- Un celular con NFC y la app **NFC Tools**, gratis, en App Store y Google Play (de "wakdev").
- El link del jugador. Con NCH: `https://darkside-hz.github.io/cs2card/nch/`

## Paso a paso

1. **Prendé el NFC.** En Android: Ajustes → NFC. En iPhone no hay que activarlo.
2. **Abrí NFC Tools** → pestaña **Escribir** (Write) → **Agregar un registro** → **URL / URI**.
3. **Pegá el link** completo, con `https://` al principio, y tocá OK.
4. Tocá **Escribir / 1 registro** y **apoyá el celular sobre el sticker** hasta que diga "Escritura correcta". Tarda un par de segundos. Si falla, mové el celular despacio: la antena está cerca de la cámara en la mayoría.
5. **Probalo antes de pegarlo:** con la app cerrada, acercá el celular al sticker. Tiene que abrir el navegador con la página del jugador.
   - iPhone XS o más nuevo: abre solo, con un aviso arriba para tocar.
   - iPhone 7, 8 y X: no leen tags con la pantalla bloqueada; abrí el Centro de control y usá el botón "Escáner NFC".
   - Android: abre solo con la pantalla encendida.
6. **Recién cuando funcione**, pegá el sticker en el hueco de la base, poné una gota de pegamento en el borde y encastrá la tapa con el diseño hacia arriba. Después de pegar, probalo otra vez.

## Cosas para tener en cuenta

- **El link no se cambia nunca.** Todo lo que ves en la página (diseño, textos, colores, datos) se modifica desde el proyecto y se publica solo. El sticker no se regraba.
- **No lo bloquees.** NFC Tools tiene la opción "Bloquear etiqueta" y es irreversible. Solo usala si estás 100% seguro del link, y yo no la recomiendo.
- El sticker no funciona pegado sobre metal (necesita una capa aislante) ni al lado de otro NFC (tarjetas de subte, banco). Ponelo lejos de esas.
- Si un celular no lee la tarjeta, el QR (`qr/nch.png`) abre exactamente la misma página.
- Si grabás una tarjeta nueva, escribí en el sticker el link de **ese** jugador. Anotá con un marcador en una etiqueta cuál es cuál para no mezclarlas.

## Solución de problemas

| Problema | Qué hacer |
|---|---|
| "Error al escribir" | Acercá y no muevas el celular; sacale la funda; probá con el otro lado del celular. |
| Lee, pero no abre nada | Verificá que el registro sea tipo **URL** y no "Texto". |
| Abre una página 404 | El link no está publicado todavía o tiene un error de tipeo. Abrilo primero en el navegador. |
| El iPhone no reacciona | Sacá la funda, desbloqueá el celular y acercalo a la parte de arriba de la tarjeta. |
| Funciona en un celular y en otro no | Probá con NFC Tools → Leer: si el tag se lee ahí, el sticker está bien y es un tema del celular. |
