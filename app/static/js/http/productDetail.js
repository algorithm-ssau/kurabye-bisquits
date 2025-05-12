document.addEventListener("DOMContentLoaded", () => {
  const API_BASE_URL = "/api/v1";

  // Cache DOM Elements
  const elements = {
    nameTitle: document.getElementById("productName"),
    image: document.getElementById("productImage"),
    photoContainer: document.getElementById("productPhotoContainer"), // Assuming this is the parent of the image

    // Info switcher elements
    infoDescriptionPaneP: document
      .getElementById("infoDescription")
      ?.querySelector("p"),
    compositionListPaneUl: document.getElementById("compositionList"),
    nutritionFatsP: document
      .getElementById("infoNutrition")
      ?.querySelector("#nutritionFats"),
    nutritionProteinsP: document
      .getElementById("infoNutrition")
      ?.querySelector("#nutritionProteins"),
    nutritionCarbsP: document
      .getElementById("infoNutrition")
      ?.querySelector("#nutritionCarbs"),
    nutritionEnergyP: document
      .getElementById("infoNutrition")
      ?.querySelector("#nutritionEnergy"),

    // Price and quantity for the single displayed package
    apiGrammageDisplay: document.getElementById("apiGrammage"),
    apiPriceDisplay: document.getElementById("apiPrice"),
    quantityInput: document.getElementById("quantityInput"),
    quantityMinusBtn: document.querySelector(
      "#dynamicPriceList .quantity-btn.minus",
    ), // Ensure these selectors are correct for your HTML
    quantityPlusBtn: document.querySelector(
      "#dynamicPriceList .quantity-btn.plus",
    ),
    staticPriceList: document.getElementById("staticPriceList"), // To hide the original static list if it exists

    addToCartBtn: document.getElementById("addToCartBtn"),

    infoSwitcherButtons: document.querySelectorAll(
      ".info-switcher-buttons .info-tab-btn",
    ),
    infoPanes: document.querySelectorAll(".info-switcher-content .info-pane"),

    recommendationsGrid: document.querySelector(".recommendations-grid"), // From your HTML
  };

  let currentProductData = null; // To store the fetched product data

  // --- Utility Functions (should ideally be in authUtils.js and imported/included) ---
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
    return decoded ? decoded.user_id : null; // Assumes 'user_id' is in the JWT payload
  }
  // --- End Utility Functions ---

  function getProductIdFromPath() {
    const pathSegments = window.location.pathname.split("/"); // e.g., ["", "product", "123"]
    if (
      pathSegments.length > 2 &&
      pathSegments[1].toLowerCase() === "product"
    ) {
      const productId = parseInt(pathSegments[2]);
      if (!isNaN(productId)) return productId;
    }
    console.error("Product ID not found or invalid in URL path: /product/{id}");
    return null;
  }

  async function fetchProductDetails(productId) {
    if (!productId) {
      if (elements.nameTitle)
        elements.nameTitle.textContent = "Товар не найден (неверный URL)";
      return;
    }
    if (elements.nameTitle)
      elements.nameTitle.textContent = "Загрузка информации о товаре...";
    if (elements.image) elements.image.style.opacity = 0.7; // Visual feedback for loading

    try {
      const response = await fetch(
        `${API_BASE_URL}/product/?product_id=${productId}`,
      );
      if (!response.ok) {
        const errorText = await response.text(); // Try to get more error info
        throw new Error(
          `HTTP ${response.status}: ${response.statusText || errorText}`,
        );
      }
      currentProductData = await response.json();
      populatePage(currentProductData);
      setupEventListeners(); // Setup listeners after data is available
      // loadRecommendations(currentProductData.category_id, currentProductData.product_id); // Placeholder
    } catch (error) {
      console.error("Failed to fetch product details:", error);
      if (elements.nameTitle)
        elements.nameTitle.textContent = error.message.includes("404")
          ? "Товар не найден"
          : "Ошибка загрузки данных";
      if (elements.photoContainer)
        elements.photoContainer.innerHTML =
          '<p style="text-align:center;">Не удалось загрузить изображение.</p>';
    } finally {
      if (elements.image) elements.image.style.opacity = 1;
    }
  }

  function populatePage(product) {
    document.title = product.name || "Детали товара"; // Update browser tab title
    if (elements.nameTitle) elements.nameTitle.textContent = product.name;

    if (elements.image) {
      const imageUrl = product.product_image.startsWith("/")
        ? product.product_image
        : `/${product.product_image}`;
      elements.image.src = imageUrl;
      elements.image.alt = product.name;
    }

    // Info switcher content
    if (elements.infoDescriptionPaneP)
      elements.infoDescriptionPaneP.textContent =
        product.description || "Описание отсутствует.";

    if (elements.compositionListPaneUl) {
      elements.compositionListPaneUl.innerHTML = ""; // Clear previous
      if (product.composition && product.composition.length > 0) {
        product.composition.forEach((item) => {
          const li = document.createElement("li");
          li.textContent = `${item.name}${item.is_allergen ? " (аллерген!)" : ""}`;
          elements.compositionListPaneUl.appendChild(li);
        });
      } else {
        elements.compositionListPaneUl.innerHTML = "<li>Состав не указан.</li>";
      }
    }

    if (elements.nutritionFatsP)
      elements.nutritionFatsP.innerHTML = `${product.fats !== null ? product.fats : "..."} <strong>жиры</strong>`;
    if (elements.nutritionProteinsP)
      elements.nutritionProteinsP.innerHTML = `${product.proteins !== null ? product.proteins : "..."} <strong>белки</strong>`;
    if (elements.nutritionCarbsP)
      elements.nutritionCarbsP.innerHTML = `${product.carbohydrates !== null ? product.carbohydrates : "..."} <strong>углеводы</strong>`;
    if (elements.nutritionEnergyP)
      elements.nutritionEnergyP.innerHTML = `${product.energy !== null ? product.energy : "..."} <strong>кКал (на 100г)</strong>`;

    // Populate the dynamic price list section (for the single package from API)
    if (elements.apiGrammageDisplay)
      elements.apiGrammageDisplay.textContent = `${product.grammage || "N/A"}`;
    if (elements.apiPriceDisplay)
      elements.apiPriceDisplay.textContent = `${(product.price || 0).toFixed(2)}`;

    if (elements.staticPriceList)
      elements.staticPriceList.style.display = "none"; // Hide the original static list

    // Ensure quantity input reference is up-to-date if it was dynamically created or might change
    // However, based on your HTML, it's static within the dynamicPriceList.
    elements.quantityInput = document.getElementById("quantityInput");
    elements.quantityMinusBtn = document.querySelector(
      "#dynamicPriceList .quantity-btn.minus",
    );
    elements.quantityPlusBtn = document.querySelector(
      "#dynamicPriceList .quantity-btn.plus",
    );
  }

  function setupEventListeners() {
    // Quantity controls
    if (elements.quantityMinusBtn && elements.quantityInput) {
      elements.quantityMinusBtn.addEventListener("click", () => {
        let currentValue = parseInt(elements.quantityInput.value);
        if (currentValue > 1) elements.quantityInput.value = currentValue - 1;
      });
    }
    if (elements.quantityPlusBtn && elements.quantityInput) {
      elements.quantityPlusBtn.addEventListener("click", () => {
        let currentValue = parseInt(elements.quantityInput.value);
        if (currentValue < 99) elements.quantityInput.value = currentValue + 1; // Max 99
      });
    }

    // Info switcher tabs
    if (elements.infoSwitcherButtons && elements.infoPanes) {
      elements.infoSwitcherButtons.forEach((button) => {
        button.addEventListener("click", () => {
          const tabId = button.dataset.infotab; // e.g., "description", "composition", "nutrition"

          elements.infoSwitcherButtons.forEach((btn) =>
            btn.classList.remove("active"),
          );
          button.classList.add("active");

          elements.infoPanes.forEach((pane) => {
            pane.classList.remove("active");
            // Construct the target pane ID e.g., "infoDescription", "infoComposition"
            const targetPaneId = `info${tabId.charAt(0).toUpperCase() + tabId.slice(1)}`;
            if (pane.id === targetPaneId) {
              pane.classList.add("active");
            }
          });
        });
      });
    }

    // Add to Cart Button
    if (elements.addToCartBtn && currentProductData) {
      // Clone and replace to ensure only one event listener if this function is called multiple times
      const newBtn = elements.addToCartBtn.cloneNode(true);
      elements.addToCartBtn.parentNode.replaceChild(
        newBtn,
        elements.addToCartBtn,
      );
      elements.addToCartBtn = newBtn; // Update the reference in our elements cache

      elements.addToCartBtn.addEventListener("click", async () => {
        const quantity = elements.quantityInput
          ? parseInt(elements.quantityInput.value)
          : 1;
        if (quantity < 1) {
          alert("Пожалуйста, выберите корректное количество.");
          return;
        }

        const token = getCookie("kurabye_access_token");
        if (!token) {
          alert(
            "Пожалуйста, войдите в систему, чтобы добавить товары в корзину.",
          );
          const currentPath =
            window.location.pathname +
            window.location.search +
            window.location.hash;
          window.location.href = `/login.html?redirectUrl=${encodeURIComponent(currentPath)}`;
          return;
        }

        const cartId = getUserIdFromJwt();
        if (!cartId) {
          alert("Ошибка идентификации пользователя. Попробуйте войти снова.");
          return;
        }

        const payload = {
          product_id: parseInt(currentProductData.product_id),
          cart_id: parseInt(cartId),
          product_quantity: parseInt(quantity),
        };

        elements.addToCartBtn.disabled = true;
        elements.addToCartBtn.textContent = "Добавляем...";

        try {
          const response = await fetch(
            `${API_BASE_URL}/cart/${currentProductData.product_id}`,
            {
              method: "PATCH",
              headers: {
                "Content-Type": "application/json",
                accept: "application/json",
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify(payload),
            },
          );

          if (response.ok) {
            // const result = await response.json(); // Assuming API returns some confirmation
            alert(
              `"${currentProductData.name}" (${quantity} шт.) успешно добавлен в корзину!`,
            );
          } else if (response.status === 401) {
            alert(
              `"${currentProductData.name}" в ${quantity} шт. нету на складах :(`,
            );
          } else {
            const errorData = await response
              .json()
              .catch(() => ({ detail: "Не удалось добавить товар." }));
            let errorMessage = "Не удалось добавить товар в корзину.";
            if (errorData.detail && typeof errorData.detail === "string") {
              errorMessage = errorData.detail;
            } else if (
              errorData.detail &&
              Array.isArray(errorData.detail) &&
              errorData.detail[0] &&
              errorData.detail[0].msg
            ) {
              errorMessage = errorData.detail[0].msg;
            }
            alert(`Ошибка: ${errorMessage}`);
            if (response.status === 401 || response.status === 403) {
              // Token invalid or expired
              window.location.href = `/login.html?reason=token_expired&redirectUrl=${encodeURIComponent(window.location.pathname + window.location.search)}`;
            }
          }
        } catch (error) {
          console.error("Error adding product to cart:", error);
          alert("Произошла сетевая ошибка при добавлении товара.");
        } finally {
          elements.addToCartBtn.disabled = false;
          elements.addToCartBtn.textContent = "Добавить в корзину";
        }
      });
    }
  }

  // Placeholder for recommendations - you can implement this similarly to catalogLoader
  if (elements.recommendationsGrid) {
    elements.recommendationsGrid.innerHTML =
      "<p>Рекомендованные товары появятся здесь.</p>";
  }

  // --- Initial Load ---
  const productId = getProductIdFromPath();
  fetchProductDetails(productId);
});
