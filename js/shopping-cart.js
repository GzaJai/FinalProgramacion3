export const getCart = () => {
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
                quantity: 1,
                image_url: product.image_url
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

    const item = cart.find(p => p.id === id);
    if (!item) return;

    if (item.quantity > 1) {
        item.quantity--;
    } else {
        const index = cart.findIndex(p => p.id === id);
        cart.splice(index, 1);
    }

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
        
        const items = cart.slice(i, i + 3);
        items.forEach(item => {
            console.log(item);
            
            html += `
                <div class="col-sm-6 col-xl-3">
                    <div class="box shopping-cart-item">
                    <h4>${item.name}</h4>
                    <div class="img-box">
                            <img src=${item.image_url} alt="">
                        </div>
                        <div class="detail-box">
                            <h6><span>$${item.price}</span></h6>
                        </div>
                        <div class="modify-quantity">
                            <button class="decrement-btn" data-id="${item.id}">-</button>
                            <span>${item.quantity}</span>
                            <button class="increment-btn" data-id="${item.id}">+</button>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `</div>`;
    }

    container.innerHTML = html;

    cart.forEach(element => {
        total += element.quantity * element.price;
    });

    totalDisplay.textContent = " $ " + total;
}

// Event delegation: un solo listener permanente en el contenedor
const container = document.getElementById("cart-container");
if (container) {
    container.addEventListener("click", (e) => {
        const decrementBtn = e.target.closest(".decrement-btn");
        const incrementBtn = e.target.closest(".increment-btn");

        if (decrementBtn) {
            const id = Number(decrementBtn.dataset.id);
            decrementQuantity(id);
            return;
        }

        if (incrementBtn) {
            const id = Number(incrementBtn.dataset.id);
            addToCart(id);
        }
    });
}

if (document.getElementById("cart-container") && document.getElementById("cart-total-amount")) {
    renderCart();
}