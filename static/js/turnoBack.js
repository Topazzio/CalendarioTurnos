const cards = document.querySelectorAll(".material-card");
const btn = document.getElementById("continuar");
const formSection = document.getElementById("formulario-turno");
const form = document.getElementById("turnoForm");

let selectedMaterial = "";

cards.forEach(card => {
  card.addEventListener("click", () => {
    cards.forEach(c => c.classList.remove("active"));
    card.classList.add("active");
    selectedMaterial = card.dataset.material;
    btn.disabled = false;
    btn.classList.add("enabled");
  });
});

/* Mostrar formulario */
btn.addEventListener("click", () => {
  if (!selectedMaterial) return;
  formSection.style.display = "block";
  formSection.scrollIntoView({ behavior: "smooth" });
});

/* Enviar a WhatsApp */
form.addEventListener("submit", function(e) {
  e.preventDefault();

  const nombre = document.getElementById("nombre").value;
  const telefono = document.getElementById("telefono").value;
  const auto = document.getElementById("auto").value;
  const anio = document.getElementById("anio").value;
  const comentarios = document.getElementById("comentarios").value;
  const pago = document.getElementById("pago").value;

  const mensaje = `
Hola! Quiero pedir turno para tapizar mi volante.

📌 Material: ${selectedMaterial}
👤 Nombre: ${nombre}
📱 Teléfono: ${telefono}
🚗 Auto: ${auto}
📅 Año: ${anio}
💳 Forma de pago: ${pago}
📝 Comentarios: ${comentarios}
  `;

  const numero = "549XXXXXXXXXX"; // ← tu numero

  window.open(
    `https://wa.me/${numero}?text=${encodeURIComponent(mensaje)}`,
    "_blank"
  );
});