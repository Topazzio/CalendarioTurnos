const images = document.querySelectorAll(".trabajo-item img");

const lightbox = document.getElementById("lightbox");
const lightboxImg = document.getElementById("lightbox-img");
const lightboxText = document.getElementById("lightbox-text");

const closeBtn = document.querySelector(".close");
const prevBtn = document.querySelector(".prev");
const nextBtn = document.querySelector(".next");

let currentIndex = 0;

/* abrir imagen */
images.forEach((img, index) => {
  img.addEventListener("click", () => {
    currentIndex = index;
    showImage();
    lightbox.classList.add("active");
  });
});

function showImage() {
  const img = images[currentIndex];
  lightboxImg.src = img.src;
  lightboxText.textContent = img.dataset.info;
}

/* siguiente */
function nextImage() {
  currentIndex = (currentIndex + 1) % images.length;
  showImage();
}

/* anterior */
function prevImage() {
  currentIndex =
    (currentIndex - 1 + images.length) % images.length;
  showImage();
}

nextBtn.addEventListener("click", nextImage);
prevBtn.addEventListener("click", prevImage);

/* teclado */
document.addEventListener("keydown", (e) => {
  if (!lightbox.classList.contains("active")) return;

  if (e.key === "ArrowRight") nextImage();
  if (e.key === "ArrowLeft") prevImage();
  if (e.key === "Escape") lightbox.classList.remove("active");
});

/* cerrar */
closeBtn.addEventListener("click", () => {
  lightbox.classList.remove("active");
});

/* click fuera */
lightbox.addEventListener("click", (e) => {
  if (e.target === lightbox) {
    lightbox.classList.remove("active");
  }
});