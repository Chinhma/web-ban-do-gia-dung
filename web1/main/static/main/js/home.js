const addButtons = document.querySelectorAll(".btn-add");

let cart = 0;

addButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    cart++;

    document.getElementById("cart-count").innerText = cart;
  });
});
