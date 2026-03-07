const items = document.querySelectorAll(".faq-item");

items.forEach(item => {
  const question = item.querySelector(".faq-question");
  const answer = item.querySelector(".faq-answer");

  question.addEventListener("click", () => {

    // cerrar otros
    items.forEach(i => {
      if (i !== item) {
        i.classList.remove("active");
        i.querySelector(".faq-answer").style.maxHeight = null;
      }
    });

    // toggle actual
    item.classList.toggle("active");

    if (item.classList.contains("active")) {
      answer.style.maxHeight = answer.scrollHeight + "px";
    } else {
      answer.style.maxHeight = null;
    }
  });
});