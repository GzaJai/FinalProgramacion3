const getCart = () => {
    return JSON.parse(localStorage.getItem("cart")) || [];
}

const saveCart = (cart) => {
    localStorage.setItem("cart", JSON.stringify(cart));
}

const addToCart = (id) => {

    let productId

    if (id == null || id == undefined) {
        const params = new URLSearchParams(window.location.search);
        productId = parseInt(params.get("id"));
    } else {
        productId = id;
    }
    const cart = getCart();

    fetch(`http://localhost:8000/products/${productId}`)
    .then(res => res.json())
    .then(product => {

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
        renderCart()
    })
}

const removeFromCart = (id) => {
    let cart = getCart();
    cart = cart.filter(item => item.id !== id);
    saveCart(cart);
    renderCart();
}

const decrementQuantity = (id) => {
    const cart = getCart();

    const item = cart.find(product => product.id === id);
    if (!item) return;

    item.quantity--;

    const updatedCart = cart.filter(product => product.quantity > 0);

    saveCart(updatedCart);
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
    const totalDisplay = document.getElementById("cart-total-amount");

    let total = 0;

    if (cart.length === 0) {
        container.innerHTML = "<p>Carrito vacío</p>";
        totalDisplay.textContent = "$0";
        return;
    }

    let html = "";
    for (let i = 0; i < cart.length; i += 3) {
        html += `<div class="row">`;

        // Tomamos los siguientes 3 items (o menos si quedan menos de 3)
        const items = cart.slice(i, i + 3);
        items.forEach(item => {
            html += `
                <div class="col-sm-6 col-xl-3">
                    <div class="box shopping-cart-item">
                    <h4>${item.name}</h4>
                    <div class="img-box">
                            <img src="images/w${item.id}.png" alt="">
                        </div>
                        <div class="detail-box">
                            <h6><span>$${item.price}</span></h6>
                        </div>
                        <div class="modify-quantity">
                            <button onclick="decrementQuantity(${item.id})">-</button>
                            <span>${item.quantity}</span>
                            <button onclick="addToCart(${item.id})">+</button>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `</div>`; // cerramos la fila
    }

    container.innerHTML = html;

    // Calculamos total
    cart.forEach(element => {
        total += element.quantity * element.price;
    });

    totalDisplay.textContent = " $ " + total;
}


renderCart()