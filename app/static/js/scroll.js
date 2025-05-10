document.addEventListener("DOMContentLoaded", () => {
  const sections = document.querySelectorAll("section");

  if (sections.length === 0) {
    return;
  }

  const observer = new IntersectionObserver(
    (entries, currentObserver) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          entry.target.classList.remove("hidden");
          currentObserver.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.15,
    },
  );

  sections.forEach((section) => {
    observer.observe(section);
  });
});
