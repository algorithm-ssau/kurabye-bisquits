document.addEventListener("DOMContentLoaded", () => {
  const elements = {
    profileDisplayName: document.getElementById("profileDisplayName"),
    profileLogin: document.getElementById("profileLogin"),
    profileName: document.getElementById("profileName"),
    profileLastName: document.getElementById("profileLastName"),
    profilePhone: document.getElementById("profilePhone"),
    ordersList: document.getElementById("ordersList"),
    noOrdersMessage: document.getElementById("noOrdersMessage"),
  };
  // Изменяем базовый URL для заказов, если эндпоинт другой
  const API_GET_USER_ORDERS_URL = "/api/v1/cart/get_user_orders"; // Новый эндпоинт

  // --- Utility Functions (из authUtils.js или определены здесь) ---
  function getCookie(name) {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.startsWith(name + "=")) {
        return cookie.substring(name.length + 1);
      }
    }
    return null;
  }

  function decodeJwtTokenPayload(token) {
    if (!token) return null;
    try {
      const base64Url = token.split(".")[1];
      if (!base64Url) return null;
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map(function (c) {
            return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
          })
          .join(""),
      );
      return JSON.parse(jsonPayload);
    } catch (e) {
      console.error("Failed to decode JWT payload:", e);
      return null;
    }
  }
  // --- End Utility Functions ---

  function populateProfileData(decodedToken) {
    if (!decodedToken) {
      if (elements.profileDisplayName)
        elements.profileDisplayName.textContent = "Ошибка данных";
      [
        "profileLogin",
        "profileName",
        "profileLastName",
        "profilePhone",
      ].forEach((id) => {
        if (elements[id]) elements[id].textContent = "N/A";
      });
      return;
    }

    const displayName =
      decodedToken.name && decodedToken.last_name
        ? `${decodedToken.name} ${decodedToken.last_name}`
        : decodedToken.login || decodedToken.user_name || "Пользователь";

    if (elements.profileDisplayName)
      elements.profileDisplayName.textContent = displayName;
    if (elements.profileLogin)
      elements.profileLogin.textContent =
        decodedToken.login || decodedToken.user_name || "N/A";
    if (elements.profileName)
      elements.profileName.textContent = decodedToken.name || "N/A";
    if (elements.profileLastName)
      elements.profileLastName.textContent = decodedToken.last_name || "N/A";
    if (elements.profilePhone)
      elements.profilePhone.textContent = decodedToken.phone || "N/A";

    localStorage.setItem("kurabye_user_name", displayName);
  }

  function formatDate(dateString) {
    const options = {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    };
    try {
      return new Date(dateString).toLocaleDateString("ru-RU", options);
    } catch (e) {
      return dateString; // Return original if parsing fails
    }
  }

  function getStatusText(statusId) {
    switch (statusId) {
      case 1:
        return "Ожидает подтверждения"; // Pending
      case 2:
        return "В обработке"; // Processing
      case 3:
        return "Отправлен"; // Shipped
      case 4:
        return "Доставлен"; // Delivered
      case 5:
        return "Отменен"; // Cancelled
      default:
        return "Статус неизвестен";
    }
  }

  function getStatusClass(statusId) {
    switch (statusId) {
      case 1:
        return "status-pending";
      case 2:
        return "status-processing";
      case 3:
        return "status-shipped";
      case 4:
        return "status-delivered";
      case 5:
        return "status-cancelled";
      default:
        return "status-unknown";
    }
  }

  function renderOrder(order) {
    const orderCard = document.createElement("div");
    orderCard.classList.add("order-card");

    const statusText = getStatusText(order.status_id);
    const statusClass = getStatusClass(order.status_id);

    // В API ответа нет total_amount и items_preview, адаптируем карточку
    orderCard.innerHTML = `
            <div class="order-card-header">
                <a href="/order/${order.order_id}" class="order-id">Заказ #${order.order_id}</a>
                <span class="order-status ${statusClass}">${statusText}</span>
            </div>
            <div class="order-card-body">
                <p class="order-date">Дата оформления: ${formatDate(order.created_at)}</p>
                <p class="order-address">Адрес доставки: ${order.shipping_address || "Не указан"}</p>
                ${order.comment ? `<p class="order-comment-display">Комментарий: ${order.comment}</p>` : ""}
            </div>
            <div class="order-card-footer">
                <!-- Ссылка "Подробнее" может вести на отдельную страницу деталей заказа, если она будет -->
                <a href="/order-details/${order.order_id}" class="details-link" style="display:none;">Подробнее</a>
            </div>
        `;
    // Скрываем кнопку "Подробнее", т.к. пока нет такой страницы и данных для нее в этом API
    const detailsLink = orderCard.querySelector(".details-link");
    if (detailsLink) detailsLink.style.display = "none"; // Можно убрать совсем, если не планируется

    return orderCard;
  }

  async function fetchUserOrders(token, userId) {
    if (!elements.ordersList || !elements.noOrdersMessage) return;
    elements.ordersList.innerHTML =
      '<p class="loading-orders">Загрузка ваших заказов...</p>';
    elements.noOrdersMessage.style.display = "none";

    try {
      // Используем новый эндпоинт и передаем user_id как query параметр
      const response = await fetch(
        `${API_GET_USER_ORDERS_URL}?user_id=${userId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`, // Токен все еще нужен для авторизации запроса
            accept: "application/json",
          },
        },
      );
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          elements.ordersList.innerHTML =
            '<p class="error-message">Ошибка авторизации при загрузке заказов.</p>';
        } else {
          elements.ordersList.innerHTML = `<p class="error-message">Не удалось загрузить заказы (код: ${response.status}).</p>`;
        }
        console.error(
          "Failed to fetch orders:",
          response.status,
          await response.text().catch(() => ""),
        );
        return;
      }
      const orders = await response.json();
      elements.ordersList.innerHTML = ""; // Clear loading message
      if (orders && orders.length > 0) {
        orders.forEach((order) => {
          elements.ordersList.appendChild(renderOrder(order));
        });
      } else {
        elements.noOrdersMessage.style.display = "block";
      }
    } catch (error) {
      console.error("Failed to fetch orders:", error);
      elements.ordersList.innerHTML =
        '<p class="error-message">У вас пока нет заказов.</p>';
    }
  }

  function initProfilePage() {
    const token = getCookie("kurabye_access_token");

    if (!token) {
      console.warn(
        "No access token found for profile page. Redirecting to login.",
      );
      const redirectTarget = encodeURIComponent(
        window.location.pathname +
          window.location.search +
          window.location.hash,
      );
      window.location.href = `/login.html?redirectUrl=${redirectTarget}`;
      return;
    }

    const decodedToken = decodeJwtTokenPayload(token);

    if (decodedToken && decodedToken.user_id) {
      // Проверяем наличие user_id
      populateProfileData(decodedToken);
      fetchUserOrders(token, decodedToken.user_id); // Передаем user_id в fetchUserOrders
    } else {
      if (elements.profileDisplayName)
        elements.profileDisplayName.textContent =
          "Ошибка: неверный формат токена или отсутствует ID пользователя.";
      console.error(
        "Token found but could not be decoded or user_id is missing.",
      );
      // Можно добавить редирект на выход или сообщение о необходимости перелогиниться
    }
  }

  initProfilePage();
});
