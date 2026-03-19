// Cart functionality with AJAX support

document.addEventListener("DOMContentLoaded", function () {
  // Initialize cart count on page load
  updateCartCountDisplay();

  // Add to cart button click handler
  const addToCartButtons = document.querySelectorAll(".add-to-cart-btn");
  addToCartButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      addToCartAJAX(this);
    });
  });
});

function addToCartAJAX(button) {
  const productId = button.getAttribute("data-product-id");
  const productName = button.getAttribute("data-product-name");

  // Show loading state
  const originalHTML = button.innerHTML;
  button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang thêm...';
  button.disabled = true;

  // Get CSRF token for Django
  const csrfToken =
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    getCookie("csrftoken");

  // Send AJAX request
  fetch(`/cart/add/${productId}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": csrfToken,
    },
    body: "quantity=1",
    credentials: "same-origin",
  })
    .then((response) => {
      if (response.status === 401) {
        // Unauthorized - redirect to login
        showErrorNotification("Vui lòng đăng nhập để thêm vào giỏ hàng");
        setTimeout(() => {
          window.location.href = "/login/?next=" + window.location.pathname;
        }, 1500);
        return Promise.reject("Not authenticated");
      }
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      if (data.success) {
        // Update cart count
        updateCartCount(data.cart_count);

        // Show success message
        showSuccessNotification(data.message);

        // Reset button
        button.innerHTML = originalHTML;
        button.disabled = false;
      } else {
        throw new Error(data.message || "Lỗi khi thêm vào giỏ hàng");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showErrorNotification("Lỗi: " + error.message);

      // Reset button
      button.innerHTML = originalHTML;
      button.disabled = false;
    });
}

function updateCartCount(count) {
  const cartCountElement = document.getElementById("cart-count");
  if (cartCountElement) {
    cartCountElement.textContent = count;
    // Add animation
    cartCountElement.style.transform = "scale(1.2)";
    setTimeout(() => {
      cartCountElement.style.transform = "scale(1)";
    }, 200);
  }
}

function updateCartCountDisplay() {
  // Get the current cart count from the server
  const csrfToken = getCookie("csrftoken");

  fetch("/cart/count/", {
    method: "GET",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": csrfToken,
    },
    credentials: "same-origin",
  })
    .then((response) => response.json())
    .then((data) => {
      updateCartCount(data.cart_count);
    })
    .catch((error) => {
      console.error("Error fetching cart count:", error);
    });
}

function showSuccessNotification(message) {
  createNotification(message, "success");
}

function showErrorNotification(message) {
  createNotification(message, "error");
}

function createNotification(message, type) {
  // Remove existing notifications
  const existingNotification = document.querySelector(".cart-notification");
  if (existingNotification) {
    existingNotification.remove();
  }

  // Create notification element
  const notification = document.createElement("div");
  notification.className = `cart-notification cart-notification-${type}`;
  notification.textContent = message;
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === "success" ? "#52c41a" : "#ff4d4f"};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        font-size: 14px;
        font-weight: 500;
    `;

  document.body.appendChild(notification);

  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease-out";
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3000);
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Add styles for animations
const style = document.createElement("style");
style.textContent = `
    .add-to-cart-btn {
        transition: all 0.3s ease;
    }
    
    .add-to-cart-btn:hover:not(:disabled) {
        background-color: #333 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .add-to-cart-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }
    
    #cart-count {
        transition: transform 0.2s ease;
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
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
