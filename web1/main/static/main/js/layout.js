// ================= LAYOUT JAVASCRIPT =================

document.addEventListener("DOMContentLoaded", function () {
  // Initialize cart count
  updateCartCount();

  // Handle add to cart buttons
  document.addEventListener("click", function (e) {
    if (e.target.closest(".btn-add-cart")) {
      handleAddToCart(e);
    }
  });

  // Handle search
  handleSearchFunctionality();
});

// Update cart count from localStorage or server
function updateCartCount() {
  const cartCount = document.getElementById("cart-count");
  if (!cartCount) return;

  // Try to get from server via API or localStorage
  const count = localStorage.getItem("cartCount") || "0";
  cartCount.textContent = count;
}

// Handle add to cart
function handleAddToCart(e) {
  const button = e.target.closest(".btn-add-cart");
  const href = button.getAttribute("href");

  if (href) {
    // Make request to add to cart
    fetch(href, {
      method: "GET",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Update cart count
          const count =
            parseInt(localStorage.getItem("cartCount") || "0") + data.quantity;
          localStorage.setItem("cartCount", count.toString());
          updateCartCount();

          // Show success message
          showNotification("Đã thêm sản phẩm vào giỏ hàng", "success");

          // Update button state
          button.textContent = "✓ Đã thêm";
          button.style.backgroundColor = "#10b981";
          setTimeout(() => {
            button.innerHTML =
              '<i class="fa-solid fa-cart-shopping"></i><span>Thêm</span>';
            button.style.backgroundColor = "";
          }, 2000);
        }
      })
      .catch((error) => {
        console.error("Error adding to cart:", error);
        // Fallback: just navigate to the link
        window.location.href = href;
      });
  }
}

// Handle search functionality
function handleSearchFunctionality() {
  const searchForm = document.querySelector(".search-box form");
  if (!searchForm) return;

  const searchInput = searchForm.querySelector(".search-input");

  // Optional: implement auto-search suggestions
  searchInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      searchForm.submit();
    }
  });
}

// Show notification
function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.textContent = message;

  const style = document.createElement("style");
  style.textContent = `
    .notification {
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 16px 24px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      z-index: 9999;
      animation: slideIn 0.3s ease;
    }

    .notification-success {
      background-color: #10b981;
      color: white;
    }

    .notification-error {
      background-color: #dc2626;
      color: white;
    }

    .notification-info {
      background-color: #2563eb;
      color: white;
    }

    @keyframes slideIn {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    @media (max-width: 768px) {
      .notification {
        top: 10px;
        right: 10px;
        left: 10px;
        max-width: 90vw;
      }
    }
  `;

  if (!document.querySelector("style[data-notification]")) {
    style.setAttribute("data-notification", "true");
    document.head.appendChild(style);
  }

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease forwards";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Handle category navigation
function handleCategoryNavigation() {
  const categoryItems = document.querySelectorAll(".category-item");
  categoryItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      // Optional: add active state
      categoryItems.forEach((el) => el.classList.remove("active"));
      this.classList.add("active");
    });
  });
}

// Initialize tooltips
function initializeTooltips() {
  const tooltipElements = document.querySelectorAll("[title]");
  tooltipElements.forEach((el) => {
    el.addEventListener("mouseenter", function () {
      const tooltip = document.createElement("div");
      tooltip.className = "tooltip";
      tooltip.textContent = this.getAttribute("title");
      this.appendChild(tooltip);
    });

    el.addEventListener("mouseleave", function () {
      const tooltip = this.querySelector(".tooltip");
      if (tooltip) tooltip.remove();
    });
  });
}

// Call initialization functions
document.addEventListener("DOMContentLoaded", function () {
  handleCategoryNavigation();
  initializeTooltips();
});
