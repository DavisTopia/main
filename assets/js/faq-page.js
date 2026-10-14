const initializeFaqPage = () => {
  const page = document.querySelector(".nts-faq-page");
  if (!page) {
    return;
  }

  const questions = Array.from(page.querySelectorAll(".nts-faq details"));
  questions.forEach((question) => {
    question.addEventListener("toggle", () => {
      if (question.open) {
        questions.forEach((otherQuestion) => {
          if (otherQuestion !== question) {
            otherQuestion.open = false;
          }
        });
      }
    });
  });

  const revealItems = Array.from(page.querySelectorAll("[data-faq-reveal]"));
  if (
    revealItems.length === 0 ||
    !("IntersectionObserver" in window) ||
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  ) {
    return;
  }

  page.classList.add("nts-faq-motion");
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { rootMargin: "0px 0px -6% 0px", threshold: 0.08 },
  );

  revealItems.forEach((item) => revealObserver.observe(item));
  window.setTimeout(() => {
    revealItems.forEach((item) => {
      item.classList.add("is-visible");
      revealObserver.unobserve(item);
    });
  }, 2500);
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeFaqPage, { once: true });
} else {
  initializeFaqPage();
}
