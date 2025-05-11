// static/js/product-detail.js
document.addEventListener("DOMContentLoaded", () => {
  const API_BASE_URL = "/api/v1";

  const elements = {
    nameTitle: document.getElementById("productName"),
    image: document.getElementById("productImage"),

    infoDescriptionPane: document
      .getElementById("infoDescription")
      .querySelector("p"),
    compositionListPane: document.getElementById("compositionList"),
    nutritionFatsPane: document
      .getElementById("infoNutrition")
      .querySelector("#nutritionFats"),
    nutritionProteinsPane: document
      .getElementById("infoNutrition")
      .querySelector("#nutritionProteins"),
    nutritionCarbsPane: document
      .getElementById("infoNutrition")
      .querySelector("#nutritionCarbs"),
    nutritionEnergyPane: document
      .getElementById("infoNutrition")
      .querySelector("#nutritionEnergy"),

    dynamicPriceListUl: document.getElementById("dynamicPriceList"), // The UL for dynamic price info
    // Specific elements within the dynamic list item will be selected after creation or assumed structure for now
    apiGrammageDisplay: document.getElementById("apiGrammage"), // Span for grammage in dynamic list
    apiPriceDisplay: document.getElementById("apiPrice"), // Span for price in dynamic list
    quantityInput: document.getElementById("quantityInput"), // Input for quantity in dynamic list
    quantityMinusBtn: document.querySelector(
      "#dynamicPriceList .quantity-btn.minus",
    ),
    quantityPlusBtn: document.querySelector(
      "#dynamicPriceList .quantity-btn.plus",
    ),

    addToCartBtn: document.getElementById("addToCartBtn"),

    infoSwitcherButtons: document.querySelectorAll(
      ".info-switcher-buttons .info-tab-btn",
    ),
    infoPanes: document.querySelectorAll(".info-switcher-content .info-pane"),

    recommendationsGrid: document.querySelector(".recommendations-grid"),
  };

  let currentProductData = null;

  function getProductIdFromPath() {
    const pathSegments = window.location.pathname.split("/");
    if (
      pathSegments.length > 2 &&
      pathSegments[1].toLowerCase() === "product"
    ) {
      const productId = parseInt(pathSegments[2]);
      if (!isNaN(productId)) return productId;
    }
    console.error("Product ID not found or invalid in URL path.");
    return null;
  }

  async function fetchProductDetails(productId) {
    if (!productId) {
      if (elements.nameTitle)
        elements.nameTitle.textContent = "Товар не найден (URL)";
      return;
    }
    if (elements.nameTitle) elements.nameTitle.textContent = "Загрузка...";
    if (elements.image) elements.image.style.opacity = 0.7;

    try {
      const response = await fetch(
        `${API_BASE_URL}/product/?product_id=${productId}`,
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      currentProductData = await response.json();
      populatePage(currentProductData);
      setupEventListeners();
      // loadRecommendations(currentProductData.category_id, currentProductData.product_id);
    } catch (error) {
      console.error("Failed to fetch product details:", error);
      if (elements.nameTitle)
        elements.nameTitle.textContent = error.message.includes("404")
          ? "Товар не найден"
          : "Ошибка загрузки";
      if (elements.image && elements.image.parentElement)
        elements.image.parentElement.innerHTML =
          '<p style="text-align:center;">Изображение не найдено.</p>';
    } finally {
      if (elements.image) elements.image.style.opacity = 1;
    }
  }

  function populatePage(product) {
    document.title = product.name || "Детали товара";
    if (elements.nameTitle) elements.nameTitle.textContent = product.name;

    if (elements.image) {
      const imageUrl = product.product_image.startsWith("/")
        ? product.product_image
        : `/${product.product_image}`;
      elements.image.src = imageUrl;
      elements.image.alt = product.name;
    }

    if (elements.infoDescriptionPane)
      elements.infoDescriptionPane.textContent =
        product.description || "Описание отсутствует.";

    if (elements.compositionListPane) {
      elements.compositionListPane.innerHTML = "";
      if (product.composition && product.composition.length > 0) {
        product.composition.forEach((item) => {
          const li = document.createElement("li");
          li.textContent = `${item.name}${item.is_allergen ? " (аллерген!)" : ""}`;
          elements.compositionListPane.appendChild(li);
        });
      } else {
        elements.compositionListPane.innerHTML = "<li>Состав не указан.</li>";
      }
    }

    if (elements.nutritionFatsPane)
      elements.nutritionFatsPane.innerHTML = `${product.fats !== null ? product.fats : "..."} г <strong>жиры</strong>`;
    if (elements.nutritionProteinsPane)
      elements.nutritionProteinsPane.innerHTML = `${product.proteins !== null ? product.proteins : "..."} г <strong>белки</strong>`;
    if (elements.nutritionCarbsPane)
      elements.nutritionCarbsPane.innerHTML = `${product.carbohydrates !== null ? product.carbohydrates : "..."} г <strong>углеводы</strong>`;
    if (elements.nutritionEnergyPane)
      elements.nutritionEnergyPane.innerHTML = `${product.energy !== null ? product.energy : "..."} кКал <strong>(на 100г)</strong>`;

    // Populate the dynamic price list (which now has only one item based on API)
    if (elements.apiGrammageDisplay)
      elements.apiGrammageDisplay.textContent = `${product.grammage || "N/A"}`;
    if (elements.apiPriceDisplay)
      elements.apiPriceDisplay.textContent = `${(product.price || 0).toFixed(2)}`;

    // Ensure quantity input is accessible for event listeners later
    elements.quantityInput = document.getElementById("quantityInput");
    elements.quantityMinusBtn = document.querySelector(
      "#dynamicPriceList .quantity-btn.minus",
    );
    elements.quantityPlusBtn = document.querySelector(
      "#dynamicPriceList .quantity-btn.plus",
    );
  }

  function setupEventListeners() {
    if (elements.quantityMinusBtn && elements.quantityInput) {
      elements.quantityMinusBtn.addEventListener("click", () => {
        let currentValue = parseInt(elements.quantityInput.value);
        if (currentValue > 1) elements.quantityInput.value = currentValue - 1;
      });
    }
    if (elements.quantityPlusBtn && elements.quantityInput) {
      elements.quantityPlusBtn.addEventListener("click", () => {
        let currentValue = parseInt(elements.quantityInput.value);
        if (currentValue < 99) elements.quantityInput.value = currentValue + 1;
      });
    }

    elements.infoSwitcherButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const tabId = button.dataset.infotab;
        elements.infoSwitcherButtons.forEach((btn) =>
          btn.classList.remove("active"),
        );
        button.classList.add("active");
        elements.infoPanes.forEach((pane) => {
          pane.classList.remove("active");
          if (
            pane.id === `info${tabId.charAt(0).toUpperCase() + tabId.slice(1)}`
          ) {
            pane.classList.add("active");
          }
        });
      });
    });

    if (elements.addToCartBtn && currentProductData) {
      const newBtn = elements.addToCartBtn.cloneNode(true); // Re-clone to ensure fresh listeners
      elements.addToCartBtn.parentNode.replaceChild(
        newBtn,
        elements.addToCartBtn,
      );
      elements.addToCartBtn = newBtn; // Update reference

      elements.addToCartBtn.addEventListener("click", () => {
        const quantity = elements.quantityInput
          ? parseInt(elements.quantityInput.value)
          : 1;
        if (quantity < 1) {
          alert("Пожалуйста, выберите корректное количество.");
          return;
        }
        alert(
          `"${currentProductData.name}" (${currentProductData.grammage}гр, ${quantity} шт.) добавлен в корзину (заглушка).`,
        );
        // TODO: Implement API call
      });
    }
  }

  // Recommendations placeholder
  if (elements.recommendationsGrid) {
    elements.recommendationsGrid.innerHTML = "<p>Пока нет рекомендаций.</p>";
  }

  const productId = getProductIdFromPath();
  fetchProductDetails(productId);
});
