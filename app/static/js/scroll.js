document.addEventListener("DOMContentLoaded", () => {
  const sections = document.querySelectorAll("section");

  if (sections.length === 0) {
    console.log("Scroll.js: Секции для наблюдения не найдены.");
    return;
  }
  console.log(`Scroll.js: Найдено секций для наблюдения: ${sections.length}`);

  const observer = new IntersectionObserver(
    (entries, currentObserver) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          console.log(
            `Scroll.js: Секция ${entry.target.id || entry.target.className} становится видимой. Добавляем .visible, убираем .hidden. Отписываемся.`,
          );
          entry.target.classList.add("visible");
          entry.target.classList.remove("hidden");
          currentObserver.unobserve(entry.target); // Ключевой момент!
        }
      });
    },
    {
      threshold: 0.15,
    },
  );

  sections.forEach((section) => {
    console.log(
      `Scroll.js: Начинаем наблюдение за секцией ${section.id || section.className}`,
    );
    observer.observe(section);
  });
});
