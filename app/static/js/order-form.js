// static/js/order-form.js
document.addEventListener("DOMContentLoaded", () => {
  const orderForm = document.getElementById("createOrderForm");
  const fullNameInput = document.getElementById("fullName");
  const phoneInput = document.getElementById("phone");
  const shippingAddressInput = document.getElementById("shippingAddress");
  const orderCommentInput = document.getElementById("orderComment");
  const submitOrderBtn = document.getElementById("submitOrderBtn");
  const orderFormErrorEl = document.getElementById("orderFormError");
  const orderFormSuccessEl = document.getElementById("orderFormSuccess");

  const API_CREATE_ORDER_URL = "/api/v1/cart/create_order";

  // Функции из authUtils.js (getCookie, decodeJwtTokenPayload, getUserIdFromJwt, checkAuthAndRedirect)
  // Должны быть доступны (authUtils.js подключен перед этим скриптом)

  function populateUserDataFromJwt() {
    const token = getCookie("kurabye_access_token");
    if (!token) return; // checkAuthAndRedirect должен был уже сработать

    const decodedToken = decodeJwtTokenPayload(token);
    if (decodedToken) {
      // Предполагаем, что JWT содержит 'name', 'last_name', 'phone'
      const storedFullName =
        decodedToken.name && decodedToken.last_name
          ? `${decodedToken.name} ${decodedToken.last_name}`
          : decodedToken.name || ""; // Или только имя, если фамилии нет

      if (fullNameInput && storedFullName) {
        fullNameInput.value = storedFullName;
      }
      if (phoneInput && decodedToken.phone) {
        phoneInput.value = decodedToken.phone;
      }
    }
  }

  function showOrderFormMessage(element, messages, isError = true) {
    if (!element) return;
    element.innerHTML = "";
    if (messages && messages.length > 0) {
      const ul = document.createElement("ul");
      messages.forEach((msgText) => {
        const li = document.createElement("li");
        li.textContent = msgText;
        ul.appendChild(li);
      });
      element.appendChild(ul);
      element.style.display = "block";
    } else {
      element.style.display = "none";
    }
    element.className = `form-message ${isError ? "error-message" : "success-message"}`;
  }

  if (orderForm) {
    // 1. Авторизация и предзаполнение данных
    if (typeof checkAuthAndRedirect === "function") {
      if (!checkAuthAndRedirect("/login")) {
        // Укажи корректный путь к странице входа
        return; // Прерываем выполнение, если редирект
      }
    } else {
      console.warn(
        "checkAuthAndRedirect function not found. Page might be accessible without auth.",
      );
      // Базовая проверка токена, если checkAuthAndRedirect не определена
      if (!getCookie("kurabye_access_token")) {
        const currentPath =
          window.location.pathname +
          window.location.search +
          window.location.hash;
        window.location.href = `/login?redirectUrl=${encodeURIComponent(currentPath)}`;
        return;
      }
    }

    populateUserDataFromJwt(); // Заполняем ФИО и телефон

    // 2. Обработка отправки формы
    orderForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (submitOrderBtn) {
        submitOrderBtn.disabled = true;
        submitOrderBtn.textContent = "Оформляем...";
      }
      if (orderFormErrorEl) orderFormErrorEl.style.display = "none";
      if (orderFormSuccessEl) orderFormSuccessEl.style.display = "none";

      const userId = getUserIdFromJwt();
      if (!userId) {
        showOrderFormMessage(orderFormErrorEl, [
          "Ошибка: не удалось определить пользователя. Пожалуйста, войдите снова.",
        ]);
        if (submitOrderBtn) {
          submitOrderBtn.disabled = false;
          submitOrderBtn.textContent = "ПОДТВЕРДИТЬ ЗАКАЗ";
        }
        return;
      }

      const orderData = {
        status_id: 2, // "В обработке", как в твоем примере
        user_id: parseInt(userId),
        created_at: new Date().toISOString(), // Текущее время в UTC ISO формате
        shipping_address: shippingAddressInput.value,
        comment: orderCommentInput.value || null, // null если пусто
      };

      const token = getCookie("kurabye_access_token");

      try {
        const response = await fetch(API_CREATE_ORDER_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(orderData),
        });

        const responseData = await response.json();

        if (response.ok) {
          // Предполагаем, что API возвращает данные созданного заказа или сообщение об успехе
          console.log("Order created successfully:", responseData);
          // showOrderFormMessage(
          //   orderFormSuccessEl,
          //   ["Заказ успешно оформлен! Мы скоро свяжемся с вами."],
          //   false,
          // );
          alert("Заказ успешно оформлен! Мы скоро свяжемся с вами.");
          window.location.replace("/");
        } else {
          let errorMessages = ["Не удалось оформить заказ."];
          if (responseData.detail && typeof responseData.detail === "string") {
            errorMessages = [responseData.detail];
          } else if (
            responseData.detail &&
            Array.isArray(responseData.detail)
          ) {
            errorMessages = responseData.detail.map(
              (err) => `${err.loc ? err.loc.join(".") + ": " : ""}${err.msg}`,
            );
          }
          showOrderFormMessage(orderFormErrorEl, errorMessages);
        }
      } catch (error) {
        console.error("Create order network error:", error);
        showOrderFormMessage(orderFormErrorEl, [
          "Произошла сетевая ошибка. Пожалуйста, попробуйте снова.",
        ]);
      } finally {
        if (submitOrderBtn) {
          submitOrderBtn.disabled = false;
          submitOrderBtn.textContent = "ПОДТВЕРДИТЬ ЗАКАЗ";
        }
      }
    });
  }
});
