// Se ejecuta después de armar la página. Datos del jugador: window.CS2CARD.data
function personalizar(P) {
  // ejemplo: agregar una línea bajo el nombre
  // const p = document.createElement("p");
  // p.textContent = "Texto propio";
  // document.querySelector("#realname").after(p);
}
if (window.CS2CARD) personalizar(window.CS2CARD.data);
else document.addEventListener("cs2card:ready", (e) => personalizar(e.detail));
