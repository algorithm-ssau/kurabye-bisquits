// static/js/basket.js
document.addEventListener("DOMContentLoaded", () => {
  const cartTableBodyEl = document.querySelector(".order-table table tbody");
  const cartTableFooterEl = document.querySelector(".order-table table tfoot");
  const cartTotalAmountEl = document.querySelector(
    ".order-table tfoot .total td:nth-child(2)",
  ); // Assumes 2nd td in tfoot total row
  const mainCartContainerEl = document.querySelector(".order-table"); // The div that might show "empty cart"
  const checkoutFooterEl = document.querySelector(".footer"); // The div with "ОФОРМИТЬ ЗАКАЗ" button

  const API_BASE_CART_URL = "/api/v1/cart";

  // --- Utility Functions (ideally from authUtils.js) ---
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

  function getUserIdFromJwt() {
    const token = getCookie("kurabye_access_token");
    if (!token) return null;
    const decoded = decodeJwtTokenPayload(token);
    return decoded ? decoded.user_id : null; // Assuming 'user_id' is in JWT
  }
  // --- End Utility Functions ---

  function showLoadingState() {
    if (cartTableBodyEl)
      cartTableBodyEl.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:20px;">Загрузка корзины...</td></tr>`;
    if (cartTableFooterEl) cartTableFooterEl.style.display = "none";
    if (checkoutFooterEl) checkoutFooterEl.style.display = "none";
    if (mainCartContainerEl && mainCartContainerEl.querySelector("p")) {
      // Hide any previous "empty" message
      const emptyMsg = mainCartContainerEl.querySelector("p");
      if (emptyMsg) emptyMsg.style.display = "none";
    }
    const table = mainCartContainerEl
      ? mainCartContainerEl.querySelector("table")
      : null;
    if (table) table.style.display = ""; // Show table structure for loading message
  }

  function showEmptyCartState() {
    if (mainCartContainerEl) {
      mainCartContainerEl.innerHTML =
        '<p style="text-align:center; padding:30px; font-size: 1.2rem;">Ваша корзина пуста. <a href="/#catalog" style="color: var(--myColor);">Перейти в каталог?</a></p>';
    }
    // Footer and checkout button should remain hidden or also show a message
    if (cartTableFooterEl) cartTableFooterEl.style.display = "none";
    if (checkoutFooterEl) checkoutFooterEl.style.display = "none";
  }

  function renderCartItem(productId, item) {
    if (!cartTableBodyEl) return;

    const row = cartTableBodyEl.insertRow();
    row.dataset.productId = productId;

    const nameCell = row.insertCell();
    nameCell.textContent = `${item.name} ${item.grammage ? item.grammage + "гр" : ""}`;
    // Example for image:
    // nameCell.innerHTML = `<div style="display:flex; align-items:center;"><img src="${item.product_image.startsWith('/') ? item.product_image : '/' + item.product_image}" alt="${item.name}" style="width:50px; height:auto; margin-right:10px; border-radius:4px;"> <span>${item.name} ${item.grammage ? item.grammage + 'гр' : ''}</span></div>`;

    const quantityCell = row.insertCell();
    quantityCell.innerHTML = `
            <div class="button-group">
                <button class="quantity-change-btn" data-action="decrease" data-product-id="${productId}" title="Уменьшить"><img src="/img/minus.svg" alt="-"></button>
                <span class="counter" id="counter-cart-${productId}">${item.quantity}</span>
                <button class="quantity-change-btn" data-action="increase" data-product-id="${productId}" title="Увеличить"><img src="/img/plus.svg" alt="+"></button>
                <button class="remove-item-btn" data-product-id="${productId}" title="Удалить товар">×</button>
            </div>
        `;

    const priceCell = row.insertCell();
    priceCell.textContent = `${item.price.toFixed(2)} ₽`;

    const totalItemPriceCell = row.insertCell();
    totalItemPriceCell.textContent = `${(item.price * item.quantity).toFixed(2)} ₽`;
    totalItemPriceCell.id = `total-item-price-cart-${productId}`;

    attachActionListenersToRow(row, productId, item.price);
  }

  function updateCartTotal(cartData) {
    if (!cartTotalAmountEl) return;
    let totalAmount = 0;
    if (cartData && cartData.items) {
      for (const productId in cartData.items) {
        if (Object.hasOwnProperty.call(cartData.items, productId)) {
          const item = cartData.items[productId];
          totalAmount += item.price * item.quantity;
        }
      }
    }
    cartTotalAmountEl.textContent = `${totalAmount.toFixed(2)} ₽`;
  }

  async function updateCartItemQuantityOnServer(
    productId,
    newQuantity,
    token,
    cartId,
  ) {
    const payload = {
      product_id: parseInt(productId),
      cart_id: parseInt(cartId),
      product_quantity: parseInt(newQuantity),
    };

    try {
      const response = await fetch(`${API_BASE_CART_URL}/${productId}`, {
        method: "PATCH", // Using PATCH for update
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        loadCart(); // Reload the cart to show updated state
      } else if (response.status === 402) {
        alert("Такого количество товара нету на складе.");
        console.error(
          "Failed to update cart item quantity:",
          await response.text(),
        );
        loadCart();
      } else {
        alert("Не удалось обновить количество товара.");
        console.error(
          "Failed to update cart item quantity:",
          await response.text(),
        );
        loadCart();
      }
    } catch (error) {
      alert("Ошибка сети при обновлении корзины.");
      console.error("Network error updating cart item:", error);
      loadCart();
    }
  }

  async function removeCartItemFromServer(productId, token, cartId) {
    const payload = {
      // As per your cURL example for DELETE
      product_id: parseInt(productId),
      cart_id: parseInt(cartId),
    };

    try {
      const response = await fetch(`${API_BASE_CART_URL}/${productId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json", // If body is sent
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload), // If body is required by your DELETE endpoint
      });

      if (response.ok) {
        const result = await response.json();
        if (result.status === "success") {
          console.log(`Product ${productId} removed from cart.`);
          loadCart();
        } else {
          alert("Не удалось удалить товар (сервер не подтвердил успех).");
          loadCart();
        }
      } else {
        alert("Не удалось удалить товар из корзины.");
        console.error("Failed to remove cart item:", await response.text());
        loadCart();
      }
    } catch (error) {
      alert("Ошибка сети при удалении товара.");
      console.error("Network error removing cart item:", error);
      loadCart();
    }
  }

  function attachActionListenersToRow(row, productId, itemPrice) {
    const buttonGroup = row.querySelector(".button-group");
    if (!buttonGroup) return;

    const minusBtn = buttonGroup.querySelector(
      `button[data-action="decrease"][data-product-id="${productId}"]`,
    );
    const plusBtn = buttonGroup.querySelector(
      `button[data-action="increase"][data-product-id="${productId}"]`,
    );
    const removeBtn = buttonGroup.querySelector(
      `button.remove-item-btn[data-product-id="${productId}"]`,
    );
    const counterSpan = buttonGroup.querySelector(`#counter-cart-${productId}`);

    const token = getCookie("kurabye_access_token");
    const cartId = getUserIdFromJwt();

    if (minusBtn && counterSpan && token && cartId) {
      minusBtn.addEventListener("click", () => {
        let currentQuantity = parseInt(counterSpan.textContent);
        if (currentQuantity > 1) {
          // Если хотим удалять при 0, то currentQuantity >= 1
          updateCartItemQuantityOnServer(productId, -1, token, cartId);
        } else if (currentQuantity === 1) {
          // Если количество 1 и нажимаем "-", то удаляем товар
          if (
            confirm(`Удалить "${row.cells[0].textContent.trim()}" из корзины?`)
          ) {
            removeCartItemFromServer(productId, token, cartId);
          }
        }
      });
    }

    if (plusBtn && counterSpan && token && cartId) {
      plusBtn.addEventListener("click", () => {
        let currentQuantity = parseInt(counterSpan.textContent);
        updateCartItemQuantityOnServer(productId, 1, token, cartId);
      });
    }

    if (removeBtn && token && cartId) {
      removeBtn.addEventListener("click", () => {
        if (
          confirm(
            `Вы уверены, что хотите удалить "${row.cells[0].textContent.trim()}" из корзины?`,
          )
        ) {
          removeCartItemFromServer(productId, token, cartId);
        }
      });
    }
  }

  async function loadCart() {
    if (!mainCartContainerEl || !cartTableBodyEl) {
      console.error("Cart container or table body not found.");
      return;
    }
    showLoadingState();

    const token = getCookie("kurabye_access_token");
    const cartId = getUserIdFromJwt();

    if (!token || !cartId) {
      console.warn(
        "User not authenticated or cart ID not found for basket. Redirecting to login.",
      );
      showEmptyCartState();
      mainCartContainerEl.insertAdjacentHTML(
        "beforeend",
        '<p style="color:red; text-align:center; margin-top:10px;">Для доступа к корзине необходимо войти.</p>',
      );
      setTimeout(() => {
        const currentPath =
          window.location.pathname +
          window.location.search +
          window.location.hash;
        window.location.href = `/login?redirectUrl=${encodeURIComponent(currentPath)}`; // Ensure /login is your login page path
      }, 1500);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_CART_URL}/?cart_id=${cartId}`, {
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (cartTableBodyEl)
          cartTableBodyEl.innerHTML = `<tr><td colspan="4" style="text-align:center;color:red;">Не удалось загрузить корзину. Статус: ${response.status}</td></tr>`;
        if (response.status === 401 || response.status === 403) {
          // Unauthorized or Forbidden
          const currentPath =
            window.location.pathname +
            window.location.search +
            window.location.hash;
          window.location.href = `/login?reason=token_invalid&redirectUrl=${encodeURIComponent(currentPath)}`;
        }
        throw new Error(`HTTP error ${response.status}`);
      }

      const cartData = await response.json();
      cartTableBodyEl.innerHTML = ""; // Clear loading message or previous items

      if (
        cartData &&
        cartData.items &&
        Object.keys(cartData.items).length > 0
      ) {
        mainCartContainerEl.querySelector("table").style.display = ""; // Make sure table is visible
        for (const productId in cartData.items) {
          if (Object.hasOwnProperty.call(cartData.items, productId)) {
            renderCartItem(productId, cartData.items[productId]);
          }
        }
        updateCartTotal(cartData);
        if (cartTableFooterEl) cartTableFooterEl.style.display = ""; // Show tfoot
        if (checkoutFooterEl) checkoutFooterEl.style.display = ""; // Show checkout button area
        const emptyMsgInContainer = mainCartContainerEl.querySelector("p"); // Remove "empty" message if it was shown
        if (
          emptyMsgInContainer &&
          emptyMsgInContainer.textContent.includes("Ваша корзина пуста")
        )
          emptyMsgInContainer.remove();
      } else {
        showEmptyCartState();
      }
    } catch (error) {
      console.error("Error loading cart:", error);
      if (cartTableBodyEl)
        cartTableBodyEl.innerHTML =
          '<tr><td colspan="4" style="text-align:center;color:#683c1a;"><b>Корзина пуста</b></td></tr>';
    }
  }

  // Initial load
  loadCart();
});
