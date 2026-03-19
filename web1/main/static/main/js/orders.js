// Order Management Functions

/**
 * Cancel an order with confirmation
 */
function cancelOrder(orderId) {
  const dialog = document.createElement("div");
  dialog.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  `;

  dialog.innerHTML = `
    <div style="background: white; border-radius: 8px; padding: 24px; max-width: 400px; box-shadow: 0 10px 40px rgba(0,0,0,0.2)">
      <h2 style="margin: 0 0 16px 0; font-size: 18px; font-weight: 600; color: #222">
        <i class="fa-solid fa-exclamation-triangle" style="color: #faad14; margin-right: 8px"></i>
        Xác nhận hủy đơn hàng
      </h2>
      <p style="margin: 0 0 24px 0; color: #666; font-size: 14px">
        Bạn có chắc chắn muốn hủy đơn hàng này? Hành động này không thể hoàn tác.
      </p>
      <div style="display: flex; gap: 12px">
        <button onclick="this.parentElement.parentElement.parentElement.remove()" style="flex: 1; padding: 10px 16px; background: #f0f0f0; border: none; border-radius: 3px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.3s" onmouseover="this.style.background='#e0e0e0'" onmouseout="this.style.background='#f0f0f0'">
          Không, tôi bỏ qua
        </button>
        <button onclick="confirmCancelOrder(${orderId})" style="flex: 1; padding: 10px 16px; background: #ff4d4f; color: white; border: none; border-radius: 3px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.3s" onmouseover="this.style.background='#ff7875'" onmouseout="this.style.background='#ff4d4f'">
          Có, hủy đơn hàng
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(dialog);
}

/**
 * Confirm cancel order and make request
 */
function confirmCancelOrder(orderId) {
  // Remove dialog
  const dialogs = document.querySelectorAll('[style*="position: fixed"]');
  dialogs.forEach((d) => {
    if (d.style.background && d.style.background.includes("rgba")) {
      d.remove();
    }
  });

  // Show loading
  const loadingDiv = document.createElement("div");
  loadingDiv.id = "loading-overlay";
  loadingDiv.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 1001;
  `;
  loadingDiv.innerHTML = `
    <div style="background: white; padding: 24px; border-radius: 8px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.2)">
      <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f0f0f0; border-top-color: #1890ff; border-radius: 50%; animation: spin 1s linear infinite"></div>
      <p style="margin: 16px 0 0 0; color: #666; font-size: 14px">Đang xử lý...</p>
    </div>
    <style>
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    </style>
  `;
  document.body.appendChild(loadingDiv);

  // Make AJAX request to cancel order
  const csrfToken =
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    getCookie("csrftoken");
  const cancelUrl = `/orders/${orderId}/cancel/`;

  fetch(cancelUrl, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "X-Requested-With": "XMLHttpRequest",
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (response.ok) {
        return response.json().catch(() => ({}));
      }
      throw new Error("Failed to cancel order");
    })
    .then((data) => {
      // Remove loading overlay
      const loading = document.getElementById("loading-overlay");
      if (loading) loading.remove();

      // Find and remove the order card from DOM with animation
      const orderCards = document.querySelectorAll(
        '[style*="background: white"][style*="border-radius: 3px"][style*="padding: 20px"]',
      );
      let found = false;

      orderCards.forEach((card) => {
        const orderIdText = card.querySelector(
          '[style*="font-weight: 600"]',
        )?.textContent;
        if (orderIdText && orderIdText.includes(`#${orderId}`)) {
          // Add fade out animation
          card.style.animation = "fadeOut 0.3s ease-out forwards";

          // Remove after animation
          setTimeout(() => {
            card.remove();

            // Update count in Tất cả tab
            updateOrderCount();

            // Check if any orders left
            const remainingCards = document.querySelectorAll(
              '[style*="background: white"][style*="border-radius: 3px"][style*="padding: 20px"]',
            );
            if (remainingCards.length === 1) {
              // Only header remains
              // Show empty state
              location.reload();
            }

            // Show success message
            showSuccessNotification("Đơn hàng đã bị hủy thành công!");
          }, 300);
          found = true;
        }
      });

      if (!found) {
        location.reload();
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      // Remove loading overlay
      const loading = document.getElementById("loading-overlay");
      if (loading) loading.remove();

      showErrorNotification("Có lỗi xảy ra, vui lòng thử lại!");
    });
}

/**
 * Update order count in the "Tất cả" tab
 */
function updateOrderCount() {
  const allTab = document.querySelector(
    'a[href*="?status=all"], a[href="?status=all"]',
  );
  if (!allTab) return;

  const countSpan = allTab.querySelector('span[style*="background: #f0f0f0"]');
  if (countSpan) {
    const currentCount = parseInt(countSpan.textContent) || 0;
    if (currentCount > 0) {
      countSpan.textContent = (currentCount - 1).toString();
    }
  }
}

/**
 * Get CSRF token from cookies
 */
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

/**
 * View order details
 */
function viewOrderDetail(orderId) {
  window.location.href = `/orders/${orderId}/`;
}

/**
 * Show success message
 */
function showSuccessNotification(message) {
  const notification = document.createElement("div");
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-left: 4px solid #52c41a;
    padding: 16px 20px;
    border-radius: 3px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    z-index: 2000;
    animation: slideIn 0.3s ease-out;
  `;
  notification.innerHTML = `
    <div style="display: flex; align-items: center; gap: 12px; color: #52c41a">
      <i class="fa-solid fa-check-circle" style="font-size: 20px"></i>
      <div>
        <p style="margin: 0; font-weight: 600; color: #222">${message}</p>
        <p style="margin: 4px 0 0 0; font-size: 12px; color: #999">Tự động tắt trong 3 giây</p>
      </div>
    </div>
    <style>
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
    </style>
  `;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease-in forwards";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

/**
 * Show error message
 */
function showErrorNotification(message) {
  const notification = document.createElement("div");
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-left: 4px solid #ff4d4f;
    padding: 16px 20px;
    border-radius: 3px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    z-index: 2000;
    animation: slideIn 0.3s ease-out;
  `;
  notification.innerHTML = `
    <div style="display: flex; align-items: center; gap: 12px; color: #ff4d4f">
      <i class="fa-solid fa-exclamation-circle" style="font-size: 20px"></i>
      <div>
        <p style="margin: 0; font-weight: 600; color: #222">${message}</p>
        <p style="margin: 4px 0 0 0; font-size: 12px; color: #999">Tự động tắt trong 3 giây</p>
      </div>
    </div>
    <style>
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
    </style>
  `;
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOut 0.3s ease-in forwards";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

/**
 * Approve order with review note (Admin only)
 */
let currentOrderId = null;
let currentAction = null;

function approveOrderWithNote(orderId) {
  currentOrderId = orderId;
  currentAction = "approve";
  showReviewNoteModal("Xác nhận đơn hàng #" + orderId);
}

function rejectOrderWithNote(orderId) {
  currentOrderId = orderId;
  currentAction = "reject";
  showReviewNoteModal("Từ chối đơn hàng #" + orderId);
}

function showReviewNoteModal(title) {
  const modal = document.createElement("div");
  modal.className = "review-note-modal";
  modal.id = "review-modal";
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  `;

  modal.innerHTML = `
    <div style="background: white; padding: 24px; border-radius: 8px; max-width: 500px; box-shadow: 0 10px 40px rgba(0,0,0,0.2)">
      <h2 style="margin: 0 0 16px 0; font-size: 18px; font-weight: 600; color: #222">${title}</h2>
      <p style="margin: 0 0 12px 0; color: #666; font-size: 13px">Ghi chú cho khách hàng (tùy chọn):</p>
      <textarea id="review-note" placeholder="Nhập ghi chú..." style="width: 100%; padding: 10px; border: 1px solid #d9d9d9; border-radius: 3px; font-size: 13px; font-family: inherit; min-height: 100px; resize: vertical; margin: 12px 0; box-sizing: border-box"></textarea>
      <div style="display: flex; gap: 12px; margin-top: 16px">
        <button onclick="closeReviewModal()" style="flex: 1; padding: 10px; background: #f0f0f0; color: #222; border: none; border-radius: 3px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.3s">Hủy</button>
        <button onclick="submitAdminReview()" style="flex: 1; padding: 10px; background: ${currentAction === "approve" ? "#52c41a" : "#ff4d4f"}; color: white; border: none; border-radius: 3px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.3s">
          ${currentAction === "approve" ? "Xác nhận" : "Từ chối"}
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
}

function closeReviewModal() {
  const modal = document.getElementById("review-modal");
  if (modal) modal.remove();
  currentOrderId = null;
  currentAction = null;
}

function submitAdminReview() {
  if (!currentOrderId || !currentAction) return;

  const reviewNote = document.getElementById("review-note")?.value || "";
  const csrfToken =
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    getCookie("csrftoken");

  // Show loading
  const modal = document.getElementById("review-modal");
  if (modal) {
    modal.style.opacity = "0.5";
    modal.style.pointerEvents = "none";
  }

  fetch(`/admin-panel/order/${currentOrderId}/${currentAction}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "X-Requested-With": "XMLHttpRequest",
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: `review_note=${encodeURIComponent(reviewNote)}`,
  })
    .then((response) => response.json())
    .then((data) => {
      closeReviewModal();
      if (data.success) {
        showSuccessNotification(data.message);
        // Reload page after 2 seconds
        setTimeout(() => location.reload(), 2000);
      } else {
        showErrorNotification(data.message || "Có lỗi xảy ra!");
        if (modal) {
          modal.style.opacity = "1";
          modal.style.pointerEvents = "auto";
        }
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showErrorNotification("Có lỗi xảy ra, vui lòng thử lại!");
      closeReviewModal();
    });
}

/**
 * Initialize order page
 */
document.addEventListener("DOMContentLoaded", function () {
  // Add keyboard shortcuts
  document.addEventListener("keydown", function (e) {
    // Escape to close dialogs
    if (e.key === "Escape") {
      const dialogs = document.querySelectorAll('[style*="position: fixed"]');
      dialogs.forEach((d) => {
        if (d.style.background && d.style.background.includes("rgba")) {
          d.remove();
        }
      });
    }
  });

  // Check for messages in URL params or data attributes
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("success") === "true") {
    showSuccessNotification("Thao tác thành công!");
  }
  if (urlParams.get("error") === "true") {
    showErrorNotification("Đã xảy ra lỗi, vui lòng thử lại!");
  }
});
