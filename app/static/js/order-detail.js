document.addEventListener("DOMContentLoaded", () => {
  const elements = {
    pageTitle: document.getElementById("pageTitle"),
    orderDetailIdSpan: document.getElementById("orderDetailId"),
    orderDetailsContent: document.getElementById("orderDetailsContent"),
    loadingMessage: document.getElementById("orderDetailLoadingMessage"),
    errorMessage: document.getElementById("orderDetailErrorMessage"),

    summaryOrderId: document.getElementById("summaryOrderId"),
    summaryOrderDate: document.getElementById("summaryOrderDate"),
    summaryOrderStatus: document.getElementById("summaryOrderStatus"),
    summaryShippingAddress: document.getElementById("summaryShippingAddress"),
    summaryCommentContainer: document.getElementById("summaryCommentContainer"),
    summaryOrderComment: document.getElementById("summaryOrderComment"),

    orderItemsTableBody: document.getElementById("orderItemsTableBody"),
    orderItemsTableFooter: document.getElementById("orderItemsTableFooter"),
    orderTotalAmount: document.getElementById("orderTotalAmount"),
  };

  const API_BASE_ORDER_DETAIL_URL = "/api/v1/cart/get_order"; // Эндпоинт для получения деталей заказа

  // --- Utility Functions (из authUtils.js или определены здесь) ---
  function getCookie(name) {
    /* ... как раньше ... */
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.startsWith(name + "=")) {
        return cookie.substring(name.length + 1);
      }
    }
    return null;
  }
  // decodeJwtTokenPayload и getUserIdFromJwt не нужны здесь напрямую, если API защищен только токеном,
  // но checkAuthAndRedirect может быть полезен из authUtils.js для защиты страницы.
  function checkAuthAndRedirect(loginPageUrl = "/login") {
    const accessToken = getCookie("kurabye_access_token");
    if (!accessToken) {
      const currentPath =
        window.location.pathname +
        window.location.search +
        window.location.hash;
      window.location.href = `${loginPageUrl}?redirectUrl=${encodeURIComponent(currentPath)}`;
      return false;
    }
    return true;
  }
  // --- End Utility Functions ---

  function getOrderIdFromPath() {
    const pathSegments = window.location.pathname.split("/"); // e.g., ["", "order", "45"]
    if (pathSegments.length > 2 && pathSegments[1].toLowerCase() === "order") {
      const orderId = parseInt(pathSegments[2]);
      if (!isNaN(orderId)) return orderId;
    }
    console.error("Order ID not found or invalid in URL path: /order/{id}");
    return null;
  }

  function formatDate(dateString) {
    /* ... как в profile-page.js ... */
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
      return dateString;
    }
  }

  // getStatusText и getStatusClass как в profile-page.js
  function getStatusText(statusIdOrName) {
    if (typeof statusIdOrName === "number") {
      switch (statusIdOrName) {
        case 1:
          return "Ожидает подтверждения";
        case 2:
          return "В обработке";
        case 3:
          return "Отправлен";
        case 4:
          return "Доставлен";
        case 5:
          return "Отменен";
        default:
          return "Статус неизвестен";
      }
    }
    // Если API возвращает status_name как строку
    return statusIdOrName || "Статус неизвестен";
  }
  function getStatusClass(statusIdOrName) {
    let statusKey = "unknown";
    if (typeof statusIdOrName === "number") {
      switch (statusIdOrName) {
        case 1:
          statusKey = "pending";
          break;
        case 2:
          statusKey = "processing";
          break;
        case 3:
          statusKey = "shipped";
          break;
        case 4:
          statusKey = "delivered";
          break;
        case 5:
          statusKey = "cancelled";
          break;
      }
    } else if (typeof statusIdOrName === "string") {
      statusKey = statusIdOrName.toLowerCase().replace(/\s+/g, "-");
    }
    return `status-${statusKey}`;
  }

  function renderOrderItem(item) {
    if (!elements.orderItemsTableBody) return;
    const row = elements.orderItemsTableBody.insertRow();

    const nameCell = row.insertCell();
    nameCell.textContent = item.product_name;
    nameCell.classList.add("item-name");

    const priceCell = row.insertCell();
    priceCell.textContent = `${item.product_price.toFixed(2)} ₽`;
    priceCell.classList.add("item-price");

    const quantityCell = row.insertCell();
    quantityCell.textContent = item.quantity_in_order;
    quantityCell.classList.add("item-quantity");

    const subtotalCell = row.insertCell();
    subtotalCell.textContent = `${(item.product_price * item.quantity_in_order).toFixed(2)} ₽`;
    subtotalCell.classList.add("item-subtotal");
  }

  function populateOrderDetails(orderData) {
    if (!orderData) return;

    if (elements.orderDetailIdSpan)
      elements.orderDetailIdSpan.textContent = `#${orderData.order_id}`;
    document.title = `Заказ #${orderData.order_id} - Печенье Курабье`;

    if (elements.summaryOrderId)
      elements.summaryOrderId.textContent = `#${orderData.order_id}`;
    if (elements.summaryOrderDate)
      elements.summaryOrderDate.textContent = formatDate(orderData.created_at);

    const statusText = getStatusText(
      orderData.status_id || orderData.status_name,
    ); // API дает и то, и то
    const statusClass = getStatusClass(
      orderData.status_id || orderData.status_name,
    );
    if (elements.summaryOrderStatus) {
      elements.summaryOrderStatus.textContent = statusText;
      elements.summaryOrderStatus.className = `summary-value order-status ${statusClass}`;
    }

    if (elements.summaryShippingAddress)
      elements.summaryShippingAddress.textContent =
        orderData.shipping_address || "N/A";

    if (orderData.order_comment) {
      if (elements.summaryOrderComment)
        elements.summaryOrderComment.textContent = orderData.order_comment;
      if (elements.summaryCommentContainer)
        elements.summaryCommentContainer.style.display = "flex"; // Или 'block'
    } else {
      if (elements.summaryCommentContainer)
        elements.summaryCommentContainer.style.display = "none";
    }

    // Populate items table
    if (elements.orderItemsTableBody)
      elements.orderItemsTableBody.innerHTML = ""; // Clear
    let calculatedTotalAmount = 0;
    if (orderData.product_list && orderData.product_list.length > 0) {
      orderData.product_list.forEach((item) => {
        renderOrderItem(item);
        calculatedTotalAmount += item.product_price * item.quantity_in_order;
      });
      if (elements.orderItemsTableFooter)
        elements.orderItemsTableFooter.style.display = "";
    } else {
      if (elements.orderItemsTableBody)
        elements.orderItemsTableBody.innerHTML =
          '<tr><td colspan="4" style="text-align:center;">В этом заказе нет товаров.</td></tr>';
      if (elements.orderItemsTableFooter)
        elements.orderItemsTableFooter.style.display = "none";
    }

    if (elements.orderTotalAmount)
      elements.orderTotalAmount.textContent = `${calculatedTotalAmount.toFixed(2)} руб`;

    if (elements.orderDetailsContent)
      elements.orderDetailsContent.style.display = "block";
    if (elements.loadingMessage) elements.loadingMessage.style.display = "none";
    if (elements.errorMessage) elements.errorMessage.style.display = "none";
  }

  async function fetchOrderDetails(orderId) {
    const token = getCookie("kurabye_access_token");
    if (!token) {
      checkAuthAndRedirect("/login"); // Убедись, что checkAuthAndRedirect определена
      return;
    }

    if (elements.loadingMessage)
      elements.loadingMessage.style.display = "block";
    if (elements.errorMessage) elements.errorMessage.style.display = "none";
    if (elements.orderDetailsContent)
      elements.orderDetailsContent.style.display = "none";

    try {
      const response = await fetch(
        `${API_BASE_ORDER_DETAIL_URL}?order_id=${orderId}`,
        {
          headers: {
            accept: "application/json",
            Authorization: `Bearer ${token}`, // Токен нужен для доступа к заказу
          },
        },
      );
      if (!response.ok) {
        throw new Error(
          `HTTP error ${response.status}: ${await response.text().catch(() => "Failed to fetch")}`,
        );
      }
      const orderData = await response.json();
      populateOrderDetails(orderData);
    } catch (error) {
      console.error("Error fetching order details:", error);
      if (elements.loadingMessage)
        elements.loadingMessage.style.display = "none";
      if (elements.errorMessage) {
        elements.errorMessage.textContent = `Не удалось загрузить детали заказа: ${error.message.includes("404") ? "Заказ не найден" : "Ошибка сервера"}`;
        elements.errorMessage.style.display = "block";
      }
    }
  }

  // --- Initial Load ---
  if (
    typeof checkAuthAndRedirect === "function" &&
    !checkAuthAndRedirect("/login")
  ) {
    // Если checkAuthAndRedirect выполнил редирект, дальнейшее выполнение не нужно
    return;
  }

  const orderId = getOrderIdFromPath();
  if (orderId) {
    if (elements.orderDetailIdSpan)
      elements.orderDetailIdSpan.textContent = `#${orderId}`; // Предварительно ставим ID
    fetchOrderDetails(orderId);
  } else {
    if (elements.pageTitle)
      elements.pageTitle.textContent = "Ошибка: ID Заказа не найден";
    if (elements.loadingMessage) elements.loadingMessage.style.display = "none";
    if (elements.errorMessage) {
      elements.errorMessage.textContent =
        "Некорректный URL или ID заказа не указан.";
      elements.errorMessage.style.display = "block";
    }
  }
});
