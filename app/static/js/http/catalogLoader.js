document.addEventListener("DOMContentLoaded", () => {
  const productGrid = document.querySelector(".product-grid");
  const loadMoreBtn = document.getElementById("loadMoreBtn");
  // Add elements for filters and sorting if they exist in your HTML
  // Example: const sortByPriceBtn = document.getElementById('sortByPrice');

  const API_BASE_URL = "/api/v1";

  if (!productGrid) {
    console.error("Error: .product-grid element not found.");
    return;
  }

  let allFetchedProducts = []; // Stores ALL products ever fetched from the server
  let currentDisplayedProducts = []; // Products currently shown after filtering/sorting

  let currentOffset = 0;
  const productsLimit = 12; // How many products to fetch per "load more" request
  let isLoading = false; // Prevents multiple simultaneous fetch requests
  let hasMoreProducts = true; // Flag to indicate if server has more products

  // Current state for filters and sorting
  let currentFilters = {
    grammage: null, // Can be a number (e.g., 300, 500) or null if no grammage filter is active
  };
  let currentSort = {
    by: null, // Sort criteria: 'price', 'grammage', 'name', etc.
    order: "asc", // Sort order: 'asc' or 'desc'
  };

  async function fetchAndRenderProducts(isLoadMore = false) {
    if (isLoading) return; // Prevent concurrent fetches
    if (!hasMoreProducts && isLoadMore) {
      console.info("No more products to load.");
      return;
    }

    isLoading = true;
    if (!isLoadMore) {
      productGrid.innerHTML = "<p>Загрузка продуктов</p>"; // Initial loading message
      currentOffset = 0;
      allFetchedProducts = []; // Clear previous products on initial load or filter reset
      hasMoreProducts = true;
    } else if (loadMoreBtn) {
      loadMoreBtn.textContent = "Загрузка...";
      loadMoreBtn.disabled = true;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/product/all?limit=${productsLimit}&offset=${currentOffset}`,
      );

      if (!response.ok) {
        if (response.status === 404) {
          if (!isLoadMore)
            productGrid.innerHTML = "<p>Продукты не найдены :(</p>";
          hasMoreProducts = false;
        } else {
          if (!isLoadMore)
            productGrid.innerHTML = `<p>Ошибка загрузки продуктов :( : ${response.statusText}</p>`;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const newProducts = await response.json();

      if (!isLoadMore && newProducts.length === 0) {
        productGrid.innerHTML = "<p>Еще нету продуктов в этой категории :(</p>";
        hasMoreProducts = false;
      } else if (newProducts.length > 0) {
        if (!isLoadMore) {
          // First fetch
          allFetchedProducts = newProducts;
        } else {
          // Subsequent "load more" fetches
          allFetchedProducts = allFetchedProducts.concat(newProducts);
        }
        currentOffset += newProducts.length;
        if (newProducts.length < productsLimit) {
          hasMoreProducts = false; // Last batch of products from server
        }
      } else {
        // newProducts.length === 0 on a "load more" attempt
        hasMoreProducts = false;
      }

      applyFiltersAndSort(); // Apply current filters/sort to the (newly expanded) allFetchedProducts
    } catch (error) {
      console.error("Failed to load products:", error);
      if (
        !isLoadMore &&
        productGrid.innerHTML.includes("Загрузка каталога...")
      ) {
        productGrid.innerHTML = `<p>У нас какие-то проблемы с серверов. Попробуйте позже :(</p>`;
      }
      // Optionally, provide feedback for "load more" errors too
    } finally {
      isLoading = false;
      if (loadMoreBtn) {
        loadMoreBtn.textContent = "Загрузить еще";
        loadMoreBtn.disabled = false;
        updateLoadMoreButtonVisibility();
      }
    }
  }

  function applyFiltersAndSort() {
    let productsToDisplay = [...allFetchedProducts]; // Work on a copy

    // 1. Apply Filters
    if (currentFilters.grammage !== null) {
      productsToDisplay = productsToDisplay.filter(
        (p) => p.grammage === currentFilters.grammage,
      );
    }

    // 2. Apply Sorting
    if (currentSort.by) {
      productsToDisplay.sort((a, b) => {
        let valA, valB;

        switch (currentSort.by) {
          case "price":
            valA = a.price;
            valB = b.price;
            break;
          case "grammage":
            valA = a.grammage; // Assuming grammage is a number
            valB = b.grammage;
            break;
          case "name":
            valA = a.name.toLowerCase(); // Case-insensitive sort for names
            valB = b.name.toLowerCase();
            break;
          default:
            return 0; // No specific sort, maintain current order
        }

        if (valA < valB) {
          return currentSort.order === "asc" ? -1 : 1;
        }
        if (valA > valB) {
          return currentSort.order === "asc" ? 1 : -1;
        }
        return 0; // Values are equal
      });
    }

    currentDisplayedProducts = productsToDisplay;
    renderProducts(currentDisplayedProducts); // Render the filtered and sorted products
    updateLoadMoreButtonVisibility(); // Show/hide "Load More" based on server and client state
  }

  function renderProducts(productsToRender) {
    productGrid.innerHTML = ""; // Clear previous items before rendering the new set

    if (productsToRender.length === 0) {
      productGrid.innerHTML = "<p>Продукты с данными фильтрами не найдены.</p>";
      return;
    }

    productsToRender.forEach((product) => {
      const imageUrl = product.product_image.startsWith("/")
        ? product.product_image
        : `/${product.product_image}`;

      const productCardLink = document.createElement("a");
      productCardLink.href = `/product/${product.product_id}`;
      productCardLink.classList.add("product-card-link");
      productGrid.appendChild(productCardLink);

      const grammageText = product.grammage ? `${product.grammage}g` : "N/A"; // Or some other placeholder

      const productCardHTML = `
                <div class="product-card">
                    <p class="product-title">${product.name}</p>
                    <img src="${imageUrl}" alt="${product.name}" />
                    <div class="product-info-row">
                        <!-- Updated product info display -->
                        <p class="product-info">${product.price.toFixed(2)} руб / ${grammageText}</p>
                    </div>
                </div>
            `;
      productCardLink.innerHTML = productCardHTML;

      productGrid.appendChild(productCardLink);
    });

    addCartIconListeners();
  }

  function addCartIconListeners() {
    const cartIcons = productGrid.querySelectorAll(".cart-icon");
    cartIcons.forEach((icon) => {
      // Prevent adding multiple listeners to the same icon if re-rendering
      if (!icon.hasAttribute("data-listener-added")) {
        icon.addEventListener("click", handleCartIconClick);
        icon.setAttribute("data-listener-added", "true");
      }
    });
  }

  function handleCartIconClick(event) {
    event.preventDefault(); // Prevent link navigation if icon is inside <a>
    event.stopPropagation(); // Stop event from bubbling to parent <a>
    const productId = event.currentTarget.dataset.productId;
    console.log(`Add to cart: Product ID ${productId}`);
    alert(`Product ID ${productId} - Add to cart (placeholder)`);
    // TODO: Implement actual "add to cart" API call
    // Example: addProductToApiCart(1, productId, 1); // Assuming cartId=1, quantity=1
  }

  function updateLoadMoreButtonVisibility() {
    if (loadMoreBtn) {
      // Show "Load More" only if there are potentially more products on the server
      // AND no client-side filters/sorting are active that would make "Load More" confusing.
      // If filters/sort are meant to work with "Load More" (server-side), this logic needs adjustment.
      const noClientFiltersActive = currentFilters.grammage === null;
      const noClientSortActive = currentSort.by === null;

      if (hasMoreProducts && noClientFiltersActive && noClientSortActive) {
        loadMoreBtn.style.display = "inline-block";
      } else {
        loadMoreBtn.style.display = "none";
      }
    }
  }

  function setupFilterAndSortListeners() {
    // Example: Grammage filter links in your HTML dropdown
    // <a href="#" id="filterGrammage300" data-grammage="300">300 гр</a>
    // <a href="#" id="filterGrammage500" data-grammage="500">500 гр</a>
    // <a href="#" id="filterGrammageClear" data-grammage="null">Clear Grammage</a>

    document.querySelectorAll("[data-grammage-filter]").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const newGrammage =
          e.currentTarget.dataset.grammageFilter === "null"
            ? null
            : parseInt(e.currentTarget.dataset.grammageFilter);

        if (currentFilters.grammage === newGrammage) {
          // Toggle off if same filter clicked
          currentFilters.grammage = null;
          e.currentTarget.classList.remove("active-filter");
        } else {
          currentFilters.grammage = newGrammage;
          // Visually update active filter
          document
            .querySelectorAll("[data-grammage-filter]")
            .forEach((el) => el.classList.remove("active-filter"));
          if (newGrammage !== null) {
            e.currentTarget.classList.add("active-filter");
          }
        }
        applyFiltersAndSort();
      });
    });

    // Example: Sort by price button/link
    // <a href="#" id="sortByPrice" data-sort-by="price">Sort by Price</a>
    document.querySelectorAll("[data-sort-by]").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const sortBy = e.currentTarget.dataset.sortBy;
        if (currentSort.by === sortBy) {
          currentSort.order = currentSort.order === "asc" ? "desc" : "asc"; // Toggle order
        } else {
          currentSort.by = sortBy;
          currentSort.order = "asc"; // Default to ascending
        }
        // Visually update active sort (e.g., add arrows for asc/desc)
        console.log(
          `Sorting by ${currentSort.by}, order: ${currentSort.order}`,
        );
        applyFiltersAndSort();
      });
    });

    if (loadMoreBtn) {
      loadMoreBtn.addEventListener("click", () => fetchAndRenderProducts(true));
    }
  }

  // --- INITIALIZATION ---
  fetchAndRenderProducts(false); // Fetch initial batch of products
  setupFilterAndSortListeners(); // Setup listeners for filter/sort UI elements
});
