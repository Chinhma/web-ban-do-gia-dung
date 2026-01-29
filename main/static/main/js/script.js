// State
let isLoggedIn = false;
let cartCount = 0;
const navCartBadgeInit = document.getElementById("navCartBadge");
if (navCartBadgeInit) {
  const v = parseInt(navCartBadgeInit.textContent || "0");
  if (!isNaN(v)) cartCount = v;
}

// DOM Elements
const navbarActions = document.getElementById("navbarActions");
const loginBtn = document.getElementById("loginBtn");
const registerBtn = document.getElementById("registerBtn");
const cartBadge = document.getElementById("cartBadge");
const categoryItems = document.querySelectorAll(".category-item");
const addToCartBtns = document.querySelectorAll(".add-to-cart");

// Update navbar based on login state (only if navbarActions exists)
function updateNavbar() {
  if (!navbarActions) return;
  if (isLoggedIn) {
    navbarActions.innerHTML = `
      <div class="user-info">👤 Xin chào!</div>
      <button class="btn btn-secondary" id="logoutBtn">Đăng xuất</button>
      <button class="cart-btn" id="cartBtn">
        🛒
        <span class="cart-badge" id="cartBadge">${cartCount}</span>
      </button>
    `;
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) logoutBtn.addEventListener("click", toggleLogin);
  } else {
    navbarActions.innerHTML = `
      <button class="btn btn-secondary" id="loginBtn">👤 Đăng nhập</button>
      <button class="btn btn-primary" id="registerBtn">Đăng ký</button>
      <button class="cart-btn" id="cartBtn">
        🛒
        <span class="cart-badge" id="cartBadge">${cartCount}</span>
      </button>
    `;
    const loginBtnNew = document.getElementById("loginBtn");
    if (loginBtnNew) loginBtnNew.addEventListener("click", toggleLogin);
  }
}

// Toggle login state
function toggleLogin() {
  isLoggedIn = !isLoggedIn;
  updateNavbar();
}

// Update cart badge
function updateCartBadge() {
  const badge = document.getElementById("cartBadge");
  if (badge) badge.textContent = cartCount;
  const navBadge = document.getElementById("navCartBadge");
  if (navBadge) navBadge.textContent = cartCount;
}

// Add to cart
function addToCart() {
  cartCount++;
  updateCartBadge();

  // Visual feedback
  const badge = document.getElementById("cartBadge");
  if (badge) {
    badge.style.transform = "scale(1.3)";
    setTimeout(() => {
      badge.style.transform = "scale(1)";
    }, 200);
  }
}

// Category click handler
categoryItems.forEach((item) => {
  item.addEventListener("click", function () {
    categoryItems.forEach((i) => i.classList.remove("active"));
    this.classList.add("active");
  });
});

// Add to cart buttons
addToCartBtns.forEach((btn) => {
  btn.addEventListener("click", function (e) {
    e.stopPropagation();
    addToCart();
  });
});

// Initial setup
if (loginBtn) loginBtn.addEventListener("click", toggleLogin);
// initialize cartCount from navbar badge if present
const navBadgeInit = document.getElementById("navCartBadge");
if (navBadgeInit) {
  const n = parseInt(navBadgeInit.textContent) || 0;
  cartCount = n;
}
updateCartBadge();

// --- Buy Now modal handling ---
document.addEventListener("DOMContentLoaded", function () {
  const buyNowButtons = document.querySelectorAll(".buy-now");
  const modal = document.getElementById("buyNowModal");
  const buyNowForm = document.getElementById("buyNowForm");
  const buyNowQty = document.getElementById("buyNowQty");
  const buyNowClose = document.getElementById("buyNowClose");
  const buyNowAddToCart = document.getElementById("buyNowAddToCart");
  let currentProductId = null;

  function openModal(id) {
    currentProductId = id;
    if (buyNowQty) buyNowQty.value = 1;
    if (modal) modal.classList.remove("hidden");
    if (buyNowForm) buyNowForm.action = `/buy_now/${id}/`;
  }

  function closeModal() {
    if (modal) modal.classList.add("hidden");
    currentProductId = null;
  }

  buyNowButtons.forEach((b) =>
    b.addEventListener("click", function (e) {
      const id = this.dataset.productId;
      openModal(id);
    }),
  );

  if (buyNowClose) buyNowClose.addEventListener("click", closeModal);
  // click outside to close
  if (modal)
    modal.addEventListener("click", function (e) {
      if (e.target === modal) closeModal();
    });

  // Add to cart from modal (AJAX)
  if (buyNowAddToCart) {
    buyNowAddToCart.addEventListener("click", function () {
      if (!currentProductId) return;
      const qty = buyNowQty ? parseInt(buyNowQty.value || 1) : 1;
      const url = `/cart/add/${currentProductId}/`;
      const csrftoken = document.querySelector(
        "#buyNowForm input[name=csrfmiddlewaretoken]",
      )?.value;
      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrftoken,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `quantity=${qty}`,
      })
        .then((r) => {
          if (r.ok) {
            // small visual feedback
            closeModal();
            cartCount++;
            updateCartBadge();
            alert("Đã thêm vào giỏ hàng");
          } else {
            alert("Không thể thêm vào giỏ hàng");
          }
        })
        .catch(() => alert("Lỗi mạng"));
    });
  }
});
