document.addEventListener("DOMContentLoaded", () => {
  const API_BASE_URL = "/api/v1";
  const sections = document.querySelectorAll(".section");
  const navLinks = document.querySelectorAll("header nav ul li a");
  const productGrid = document.querySelector(".product-grid");
  const inventoryList = document.querySelector(".inventory-list");
  const orderList = document.querySelector(".order-list");
  const loadMoreProductsBtn = document.getElementById("loadMoreProducts");
  const loadMoreOrdersBtn = document.getElementById("loadMoreOrders");
  const modal = document.getElementById("modal");
  const closeModalBtn = document.querySelector(".close-btn");
  const editProductForm = document.getElementById("editProductForm");
  const addInventoryForm = document.getElementById("addInventoryForm");
  let productOffset = 0;
  let orderOffset = 0;
  const limit = 12;
  let currentSortBy = "name";
  let currentSortOrder = "asc";

  // Get JWT from cookie
  const getToken = () => {
    const cookies = document.cookie.split(";").reduce((acc, cookie) => {
      const [name, value] = cookie.trim().split("=");
      acc[name] = value;
      return acc;
    }, {});
    return cookies["kurabye_access_token"] || "";
  };
  // API request helper
  const apiRequest = async (url, method = "GET", body = null) => {
    const token = getToken();
    const headers = {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    };
    const options = { method, headers };
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(`${API_BASE_URL}${url}`, options);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Request failed");
    }
    return response.status === 204 ? {} : await response.json();
  };

  // Show section
  const showSection = (sectionId) => {
    sections.forEach((section) => {
      section.style.display = section.id === sectionId ? "block" : "none";
    });
    navLinks.forEach((link) => {
      link.classList.toggle("active", link.dataset.section === sectionId);
    });
  };

  // Load products
  const loadProducts = async () => {
    try {
      const data = await apiRequest(
        `/admin/products?limit=${limit}&offset=${productOffset}&sorting_by=${currentSortBy}&sorting_order=${currentSortOrder}`,
      );
      data.forEach((product) => {
        const card = document.createElement("div");
        card.className = "product-card";
        card.innerHTML = `
                    <img src="${product.product_image}" alt="${product.name}" />
                    <h3>${product.name}</h3>
                    <p>Цена: ${product.price} ₽</p>
                    <p>Граммовка: ${product.grammage || "N/A"} г</p>
                    <button data-id="${product.product_id}" class="edit-btn">Редактировать</button>
                `;
        productGrid.appendChild(card);
      });
      productOffset += limit;
      loadMoreProductsBtn.style.display =
        data.length < limit ? "none" : "block";
    } catch (error) {
      alert(`Ошибка загрузки продуктов: ${error.message}`);
      window.location.replace("/");
    }
  };

  // Load inventory
  const loadInventory = async () => {
    try {
      const data = await apiRequest("/admin/inventory");
      inventoryList.innerHTML = "";
      data.forEach((item) => {
        const div = document.createElement("div");
        div.className = "inventory-item";
        div.innerHTML = `
                    <p>Продукт ID: ${item.product_id}</p>
                    <p>Склад: ${item.warehouse_name || item.warehouse_id}</p>
                    <p>Количество: ${item.stock_quantity}</p>
                    <button data-product-id="${item.product_id}" data-warehouse-id="${item.warehouse_id}" class="delete-btn">Удалить</button>
                `;
        inventoryList.appendChild(div);
      });
    } catch (error) {
      alert(`Ошибка загрузки инвентаря: ${error.message}`);
    }
  };

  // Load orders
  const loadOrders = async () => {
    try {
      const data = await apiRequest(
        `/admin/orders?limit=${limit}&offset=${orderOffset}&sorting_by=${currentSortBy}&sorting_order=${currentSortOrder}`,
      );
      data.forEach((order) => {
        const div = document.createElement("div");
        div.className = "order-item";
        div.innerHTML = `
                    <p>ID заказа: ${order.order_id}</p>
                    <p>Дата: ${new Date(order.created_at).toLocaleString()}</p>
                    <p>Адрес: ${order.shipping_address}</p>
                    <p>Комментарий: ${order.order_comment || "N/A"}</p>
                    <select data-id="${order.order_id}" class="status-select">
                        <option value="1" ${order.status_id === 1 ? "selected" : ""}>В обработке</option>
                        <option value="2" ${order.status_id === 2 ? "selected" : ""}>Отправлен</option>
                        <option value="3" ${order.status_id === 3 ? "selected" : ""}>Доставлен</option>
                    </select>
                    <button data-id="${order.order_id}" class="update-status-btn">Обновить статус</button>
                `;
        orderList.appendChild(div);
      });
      orderOffset += limit;
      loadMoreOrdersBtn.style.display = data.length < limit ? "none" : "block";
    } catch (error) {
      alert(`Ошибка загрузки заказов: ${error.message}`);
    }
  };

  // Edit product
  const editProduct = async (productId) => {
    try {
      const product = await apiRequest(`/admin/products/${productId}`);
      editProductForm.querySelector('[name="product_id"]').value =
        product.product_id;
      editProductForm.querySelector('[name="name"]').value = product.name;
      editProductForm.querySelector('[name="product_image"]').value =
        product.product_image;
      editProductForm.querySelector('[name="price"]').value = product.price;
      editProductForm.querySelector('[name="calculus"]').value =
        product.calculus;
      editProductForm.querySelector('[name="grammage"]').value =
        product.grammage || "";
      editProductForm.querySelector('[name="description"]').value =
        product.description || "";
      editProductForm.querySelector('[name="composition"]').value =
        product.composition.join(", ");
      editProductForm.querySelector('[name="energy"]').value = product.energy;
      editProductForm.querySelector('[name="fats"]').value = product.fats;
      editProductForm.querySelector('[name="carbohydrates"]').value =
        product.carbohydrates;
      editProductForm.querySelector('[name="proteins"]').value =
        product.proteins;
      editProductForm.querySelector('[name="is_active"]').checked =
        product.is_active;
      modal.style.display = "flex";
    } catch (error) {
      alert(`Ошибка загрузки продукта: ${error.message}`);
    }
  };

  // Update product
  editProductForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(editProductForm);
    const product = {
      product_id: parseInt(formData.get("product_id")),
      name: formData.get("name"),
      product_image: formData.get("product_image"),
      price: parseFloat(formData.get("price")),
      calculus: formData.get("calculus"),
      grammage: formData.get("grammage")
        ? parseInt(formData.get("grammage"))
        : null,
      description: formData.get("description") || null,
      composition: formData
        .get("composition")
        .split(",")
        .map((item) => item.trim()),
      energy: parseInt(formData.get("energy")),
      fats: parseInt(formData.get("fats")) || 0,
      carbohydrates: parseInt(formData.get("carbohydrates")) || 0,
      proteins: parseInt(formData.get("proteins")) || 0,
      is_active: formData.get("is_active") === "on",
    };
    try {
      await apiRequest(`/admin/products/${product.product_id}`, "PUT", product);
      modal.style.display = "none";
      productGrid.innerHTML = "";
      productOffset = 0;
      loadProducts();
    } catch (error) {
      alert(`Ошибка обновления продукта: ${error.message}`);
    }
  });

  // Add/Update inventory
  addInventoryForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(addInventoryForm);
    const inventory = {
      product_id: parseInt(formData.get("product_id")),
      warehouse_id: parseInt(formData.get("warehouse_id")),
      stock_quantity: parseInt(formData.get("stock_quantity")),
      warehouse_name: formData.get("warehouse_name") || null,
    };
    try {
      await apiRequest("/admin/inventory", "POST", inventory);
      loadInventory();
      addInventoryForm.reset();
    } catch (error) {
      alert(`Ошибка добавления инвентаря: ${error.message}`);
    }
  });

  // Delete inventory
  inventoryList.addEventListener("click", async (e) => {
    if (e.target.classList.contains("delete-btn")) {
      const productId = e.target.dataset.productId;
      const warehouseId = e.target.dataset.warehouseId;
      if (confirm("Удалить запись инвентаря?")) {
        try {
          await apiRequest(
            `/admin/inventory/${productId}/${warehouseId}`,
            "DELETE",
          );
          loadInventory();
        } catch (error) {
          alert(`Ошибка удаления инвентаря: ${error.message}`);
        }
      }
    }
  });

  // Update order status
  orderList.addEventListener("click", async (e) => {
    if (e.target.classList.contains("update-status-btn")) {
      const orderId = e.target.dataset.id;
      const select = orderList.querySelector(`select[data-id="${orderId}"]`);
      const statusId = parseInt(select.value);
      try {
        await apiRequest(
          `/admin/orders/${orderId}/status?status_id=${statusId}`,
          "PATCH",
        );
        alert("Статус заказа обновлен");
      } catch (error) {
        alert(`Ошибка обновления статуса: ${error.message}`);
      }
    }
  });

  // Navigation
  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const section = link.dataset.section;
      showSection(section);
      if (section === "products") {
        productGrid.innerHTML = "";
        productOffset = 0;
        loadProducts();
      } else if (section === "inventory") {
        loadInventory();
      } else if (section === "orders") {
        orderList.innerHTML = "";
        orderOffset = 0;
        loadOrders();
      }
    });
  });

  // Sorting
  document.querySelectorAll(".dropdown-content a").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      currentSortBy = link.dataset.sortBy;
      currentSortOrder = link.dataset.sortOrder;
      if (document.querySelector("#products").style.display !== "none") {
        productGrid.innerHTML = "";
        productOffset = 0;
        loadProducts();
      } else if (document.querySelector("#orders").style.display !== "none") {
        orderList.innerHTML = "";
        orderOffset = 0;
        loadOrders();
      }
    });
  });

  // Load more
  loadMoreProductsBtn.addEventListener("click", loadProducts);
  loadMoreOrdersBtn.addEventListener("click", loadOrders);

  // Modal handling
  productGrid.addEventListener("click", (e) => {
    if (e.target.classList.contains("edit-btn")) {
      const productId = e.target.dataset.id;
      editProduct(productId);
    }
  });

  closeModalBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });

  // Logout
  document.getElementById("logoutButton").addEventListener("click", () => {
    document.cookie =
      "kurabye_access_token=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
    window.location.href = "/login.html";
  });

  showSection("products");
  loadProducts();
});
