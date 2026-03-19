document.addEventListener("DOMContentLoaded", function () {
  const addBtns = document.querySelectorAll(".btn-add");
  const cartCountEl = document.getElementById("cart-count");
  let count = Number(cartCountEl ? cartCountEl.textContent : 0) || 0;

  addBtns.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      count += 1;
      if (cartCountEl) cartCountEl.textContent = count;
      btn.classList.add("added");
      btn.innerHTML = '<i class="fa-solid fa-check"></i> Đã thêm';
      setTimeout(() => {
        btn.classList.remove("added");
        btn.innerHTML = '<i class="fa-solid fa-cart-shopping"></i> Thêm';
      }, 1200);
    });
  });

  // Search
  const searchBtn = document.getElementById("search-btn");
  const searchInput = document.getElementById("search-input");
  if (searchBtn && searchInput) {
    searchBtn.addEventListener("click", () => {
      const q = searchInput.value.trim();
      if (!q) return searchInput.focus();
      // navigate to search url (adjust as needed)
      window.location.href = "/?q=" + encodeURIComponent(q);
    });
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") searchBtn.click();
    });
  }

  // Wishlist toggle
  const wishlistBtn = document.getElementById("btn-wishlist");
  if (wishlistBtn) {
    wishlistBtn.addEventListener("click", () => {
      wishlistBtn.classList.toggle("active");
      const icon = wishlistBtn.querySelector("i");
      if (wishlistBtn.classList.contains("active"))
        icon.className = "fa-solid fa-heart";
      else icon.className = "fa-regular fa-heart";
    });
  }
});
