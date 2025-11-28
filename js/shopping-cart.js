const getCart = () => {
    return JSON.parse(localStorage.getItem("cart")) || [];
}

const saveCart = (cart) => {
    localStorage.setItem("cart", JSON.stringify(cart));
}

const addToCart = () => {
    const cart = getCart();

    const params = new URLSearchParams(window.location.search);
    const productId = parseInt(params.get("id"));

    fetch(`http://localhost:8000/products/${productId}`)
    .then(res => res.json())
    .then(product => {

        console.log(product);

        const existing = cart.find(item => item.id === product.id_key)

        if (existing) {
            existing.quantity++;
        } else {
            cart.push({
                id: product.id_key,
                name: product.name,
                price: product.price,
                quantity: 1
            })
        }

        saveCart(cart)
    })
}

const removeFromCart = (id) => {
    let cart = getCart();
    cart = cart.filter(item => item.id !== id);
    saveCart(cart);
    renderCart();
}

const addToCartBtn = document.getElementById("add-to-cart-btn")

if (addToCartBtn) {
    addToCartBtn.addEventListener("click", () => {
        addToCart()
    });
}

const renderCart = () => {
    const cart = getCart();
    const container = document.getElementById("cart-container");

    if (cart.length === 0) {
        container.innerHTML = "<p>Carrito vacío</p>"
        return;
    }

    container.innerHTML = cart.map(item => `
        <div class="cart-item">
            <img src="images/w${item.id}.png" width="80">
            <h4>${item.name}</h4>
            <p>$${item.price}</p>
            <p>Cantidad: ${item.quantity}</p>
            <button onclick="removeFromCart(${item.id})">Eliminar</button>
        </div>
        `).join("");
}

renderCart()