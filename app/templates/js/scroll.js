const sections = document.querySelectorAll("section");

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            entry.target.classList.remove("hidden");
        } else {
            entry.target.classList.remove("visible");
            entry.target.classList.add("hidden");
        }
    });
}, {
    threshold: 0.15 // когда хотя бы 15% видно
});

sections.forEach(section => {
    section.classList.add("hidden"); // изначально скрыто
    observer.observe(section);
});