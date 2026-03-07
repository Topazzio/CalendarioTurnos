let selectedMaterial = "";
let selectedDate = "";
let selectedTime = "";
let weekOffset = 0;

const cards = document.querySelectorAll(".material-card");
const btn = document.getElementById("continuar");
const formSection = document.getElementById("formulario-turno");
const calendarioSection = document.getElementById("calendario-section");
const confirmacionSection = document.getElementById("confirmacion-section");
const resumenTurno = document.getElementById("resumen-turno");
const weekdayNames = [
  "Domingo",
  "Lunes",
  "Martes",
  "Miércoles",
  "Jueves",
  "Viernes",
  "Sábado",
];

/* =========================
   SELECCION MATERIAL
========================= */

cards.forEach((card) => {
  card.addEventListener("click", () => {
    cards.forEach((c) => c.classList.remove("active"));
    card.classList.add("active");
    selectedMaterial = card.dataset.material;

    btn.disabled = false;
    btn.classList.add("enabled");
  });
});

/* =========================
   MOSTRAR FORM
========================= */

btn.addEventListener("click", () => {
  if (!selectedMaterial) return;
  formSection.style.display = "block";
  formSection.scrollIntoView({ behavior: "smooth" });
});

/* =========================
   IR A CALENDARIO
========================= */

document.getElementById("turnoForm").addEventListener("submit", function (e) {
  e.preventDefault();

  calendarioSection.style.display = "block";
  calendarioSection.scrollIntoView({ behavior: "smooth" });

  loadCalendar();
});

/* =========================
   CALENDARIO
========================= */

async function loadCalendar() {
  try {
    const res = await fetch(`/week-availability?week_offset=${weekOffset}`);
    const data = await res.json();

    const container = document.getElementById("calendar");
    container.innerHTML = "";

    data.days.forEach(day => {

      const jsDate = new Date(day.date + "T00:00:00");

      // ❌ Ignorar domingos
      if (jsDate.getDay() === 0) return;

      const dayDiv = document.createElement("div");
      dayDiv.className = "day";

      /* 🔵 MARCAR DIA DE HOY */
      const hoy = new Date();
      if (
        jsDate.getFullYear() === hoy.getFullYear() &&
        jsDate.getMonth() === hoy.getMonth() &&
        jsDate.getDate() === hoy.getDate()
      ) {
        dayDiv.classList.add("hoy");
      }

      /* 📅 NOMBRE DEL DIA */
      const nombreDia = jsDate.toLocaleDateString("es-ES", {
        weekday: "long"
      });

      const fechaFormateada = jsDate.toLocaleDateString("es-ES", {
        day: "numeric",
        month: "long"
      });

      const title = document.createElement("h4");
      title.innerText =
        nombreDia.charAt(0).toUpperCase() + nombreDia.slice(1);

      const dateText = document.createElement("div");
      dateText.className = "date";
      dateText.innerText = fechaFormateada;

      dayDiv.appendChild(title);
      dayDiv.appendChild(dateText);

      /* ⏰ SLOTS */
      day.slots.forEach(slot => {
        const slotDiv = document.createElement("div");
        slotDiv.className =
          "slot " + (slot.available ? "available" : "busy");

        slotDiv.innerText = slot.time;

        if (slot.available) {
          slotDiv.onclick = () => {
            selectedDate = day.date;
            selectedTime = slot.time;
            mostrarConfirmacion();
          };
        }

        dayDiv.appendChild(slotDiv);
      });

      container.appendChild(dayDiv);
    });

  } catch (error) {
    console.error("Error cargando calendario:", error);
  }
}

function changeWeek(offset) {
  weekOffset += offset;
  loadCalendar();
}

/* =========================
   CONFIRMACION
========================= */

function mostrarConfirmacion() {
  const nombre = document.getElementById("nombre").value;
  const telefono = document.getElementById("telefono").value;
  const auto = document.getElementById("auto").value;
  const anio = document.getElementById("anio").value;
  const pago = document.getElementById("pago").value;
  const comentarios = document.getElementById("comentarios").value;

  resumenTurno.innerHTML = `
    <p><strong>Material:</strong> ${selectedMaterial}</p>
    <p><strong>Nombre:</strong> ${nombre}</p>
    <p><strong>Teléfono:</strong> ${telefono}</p>
    <p><strong>Auto:</strong> ${auto}</p>
    <p><strong>Año:</strong> ${anio}</p>
    <p><strong>Forma de pago:</strong> ${pago}</p>
    <p><strong>Fecha:</strong> ${selectedDate}</p>
    <p><strong>Hora:</strong> ${selectedTime}</p>
    <p><strong>Comentarios:</strong> ${comentarios}</p>
  `;

  confirmacionSection.style.display = "block";
  confirmacionSection.scrollIntoView({ behavior: "smooth" });
}

/* =========================
   EDITAR
========================= */

document.getElementById("editar-btn").addEventListener("click", () => {
  confirmacionSection.style.display = "none";
  calendarioSection.scrollIntoView({ behavior: "smooth" });
});

/* =========================
   CONFIRMAR TURNO
========================= */

document.getElementById("confirmar-btn").addEventListener("click", async () => {
  const nombre = document.getElementById("nombre").value;
  const telefono = document.getElementById("telefono").value;
  const auto = document.getElementById("auto").value;
  const anio = document.getElementById("anio").value;
  const pago = document.getElementById("pago").value;
  const comentarios = document.getElementById("comentarios").value;

  const startTime = `${selectedDate}T${selectedTime}:00`;

  const res = await fetch("/book", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: nombre,
      phone: telefono,
      material: selectedMaterial,
      auto: auto,
      anio: anio,
      pago: pago,
      comentarios: comentarios,
      start_time: startTime,
    }),
  });

  const result = await res.json();

  if (res.ok) {
    alert("✅ Turno confirmado correctamente");
    location.reload();
  } else {
    alert(result.detail || "Error al reservar");
  }
});

loadCalendar();
setInterval(() => {
  loadCalendar();
}, 10000);
