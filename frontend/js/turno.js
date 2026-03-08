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
const calendarLoading = document.getElementById("calendar-loading");
const turnosDisponiblesDiv = document.getElementById("turnos-disponibles");
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
  calendarLoading.classList.remove("hidden");

  try {
    const res = await fetch(`/week-availability?week_offset=${weekOffset}`);
    const data = await res.json();

    let totalDisponibles = 0;

    data.days.forEach((day) => {
      day.slots.forEach((slot) => {
        if (slot.available) totalDisponibles++;
      });
    });

    if (totalDisponibles >= 6) {
      turnosDisponiblesDiv.className = "turnos-disponibles normal";
      turnosDisponiblesDiv.innerText = `⚡ Quedan ${totalDisponibles} turnos disponibles esta semana`;
    } else if (totalDisponibles >= 3) {
      turnosDisponiblesDiv.className = "turnos-disponibles pocos";
      turnosDisponiblesDiv.innerText = `🔥 Solo quedan ${totalDisponibles} turnos disponibles esta semana`;
    } else if (totalDisponibles > 0) {
      turnosDisponiblesDiv.className = "turnos-disponibles muy-pocos";
      turnosDisponiblesDiv.innerText = `🚨 Últimos ${totalDisponibles} turnos disponibles`;
    } else {
      turnosDisponiblesDiv.className = "turnos-disponibles muy-pocos";
      turnosDisponiblesDiv.innerText =
        "❌ No quedan turnos disponibles esta semana";
    }
    const container = document.getElementById("calendar");
    container.innerHTML = "";

    data.days.forEach((day) => {
      const jsDate = new Date(day.date + "T00:00:00");

      if (jsDate.getDay() === 0) return;

      const dayDiv = document.createElement("div");
      dayDiv.className = "day";

      const nombreDia = jsDate.toLocaleDateString("es-ES", { weekday: "long" });
      const fechaFormateada = jsDate.toLocaleDateString("es-ES", {
        day: "numeric",
        month: "long",
      });

      const title = document.createElement("h4");
      title.innerText = nombreDia.charAt(0).toUpperCase() + nombreDia.slice(1);

      const dateText = document.createElement("div");
      dateText.className = "date";
      dateText.innerText = fechaFormateada;

      dayDiv.appendChild(title);
      dayDiv.appendChild(dateText);

      day.slots.forEach((slot) => {
        const slotDiv = document.createElement("div");

        let disponible = slot.available;

        slotDiv.className = "slot " + (disponible ? "available" : "busy");

        slotDiv.innerText = slot.time;

        if (disponible) {
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
  } finally {
    calendarLoading.classList.add("hidden");
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
  }
);

const text = await res.text();
console.log(text);
// console.log(result);
if (res.ok) {
  
  alert("✅ Turno confirmado correctamente");

  if(result.whatsapp_link){
    window.open(result.whatsapp_link, "_blank");
    alert("Se abrirá WhatsApp para que puedas enviar un mensaje con los detalles de tu turno.");
  }

  location.reload();

} else {
  alert(result.detail || "Error al reservar");
}
});
setInterval(() => {
  loadCalendar();
}, 30000);
