document.addEventListener("DOMContentLoaded", () => {
  const profileUsernameEl = document.getElementById("profileUsername");
  const ordersListEl = document.getElementById("ordersList");
  const noOrdersMessageEl = document.getElementById("noOrdersMessage");
  const API_BASE = "/api/v1"; // Your API base URL

  function decodeJwtToken(token) {
    try {
      const base64Url = token.split(".")[1];
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
      console.error("Failed to decode JWT:", e);
      return null;
    }
  }

  function formatDate(dateString) {
    const options = { year: "numeric", month: "long", day: "numeric" };
    return new Date(dateString).toLocaleDateString("ru-RU", options);
  }

  function renderOrder(order) {
    const orderCard = document.createElement("div");
    orderCard.classList.add("order-card");

    let statusClass = "status-unknown";
    if (order.status_name) {
      statusClass =
        "status-" + order.status_name.toLowerCase().replace(/\s+/g, "-");
    }

    // Ensure items_preview is an array and join it, or use a placeholder
    let itemsPreviewHtml = "Состав заказа не указан.";
    if (Array.isArray(order.items_preview) && order.items_preview.length > 0) {
      itemsPreviewHtml = `<small>Состав: ${order.items_preview.join(", ")}</small>`;
    } else if (typeof order.items_preview === "string") {
      // If it's already a string
      itemsPreviewHtml = `<small>Состав: ${order.items_preview}</small>`;
    }

    orderCard.innerHTML = `
            <div class="order-card-header">
                <span class="order-id">Заказ #${order.order_id}</span>
                <span class="order-status ${statusClass}">${order.status_name || "Статус неизвестен"}</span>
            </div>
            <div class="order-card-body">
                <p class="order-date">Дата: ${formatDate(order.created_at)}</p>
                <p class="order-total">Сумма: ${order.total_amount ? order.total_amount.toFixed(2) : "N/A"} руб.</p>
                <div class="order-items-preview">
                    ${itemsPreviewHtml}
                </div>
            </div>
            <div class="order-card-footer">
                <a href="/order-details/${order.order_id}" class="details-link">Подробнее</a>
                <!-- /order-details/ID - это пример, такой страницы пока нет -->
            </div>
        `;
    return orderCard;
  }

  async function fetchUserOrders(token) {
    if (!ordersListEl || !noOrdersMessageEl) return;
    ordersListEl.innerHTML =
      '<p class="loading-orders">Загрузка ваших заказов...</p>';
    noOrdersMessageEl.style.display = "none";

    try {
      const response = await fetch(`${API_BASE}/orders/my`, {
        // Предполагаемый эндпоинт
        headers: {
          Authorization: `Bearer ${token}`,
          accept: "application/json",
        },
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          ordersListEl.innerHTML =
            '<p class="error-message">Ошибка авторизации при загрузке заказов.</p>';
          // Опционально редирект на логин, если токен невалиден
          // window.location.href = '/login.html?reason=invalid_token';
        } else {
          throw new Error(`HTTP error ${response.status}`);
        }
        return;
      }

      const orders = await response.json();
      ordersListEl.innerHTML = ""; // Clear loading message

      if (orders && orders.length > 0) {
        orders.forEach((order) => {
          ordersListEl.appendChild(renderOrder(order));
        });
      } else {
        noOrdersMessageEl.style.display = "block";
      }
    } catch (error) {
      console.error("Failed to fetch orders:", error);
      ordersListEl.innerHTML =
        '<p class="error-message">Не удалось загрузить историю заказов. Попробуйте позже.</p>';
    }
  }

  function initProfilePage() {
    // Используем getCookie из authUtils.js
    const token =
      typeof getCookie === "function"
        ? getCookie("kurabye_access_token")
        : null;

    if (!token) {
      // Если authUtils.js не подключен или getCookie не определена, или токена нет
      // Редирект на страницу входа, если пользователь не авторизован
      // Это дублирует проверку из header-auth-status.js, но полезно как защита самой страницы
      window.location.href = `/login.html?redirectUrl=${encodeURIComponent(window.location.pathname)}`;
      return;
    }

    const decodedToken = decodeJwtToken(token);
    const username = decodedToken
      ? decodedToken.user_name
      : localStorage.getItem("kurabye_user_name") || "Пользователь";

    if (profileUsernameEl) {
      profileUsernameEl.textContent = username;
    }

    fetchUserOrders(token);
  }

  initProfilePage();
});
