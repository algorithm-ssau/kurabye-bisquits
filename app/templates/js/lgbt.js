gsap.to("body", { "--myColor": "#4e0e0e", yoyo: true, repeat: 40, duration: 2 });

const bisquit = document.querySelector(".bisquit");

bisquit.addEventListener("click", () => {
    gsap.to(bisquit, {
        duration: 1,
        rotation: "+=360", // добавляет 360° к текущему углу
        transformOrigin: "50% 50%", // крутится из центра
        ease: "power1.inOut"
    });
});

function typeText(selector, text, speed = 0.05) {
    const element = document.querySelector(selector);
    element.textContent = ""; // очистить содержимое
    const chars = text.split("");
  
    chars.forEach((char, index) => {
      gsap.to({}, {
        delay: index * speed,
        onComplete: () => {
          element.textContent += char;
        }
      });
    });
  }