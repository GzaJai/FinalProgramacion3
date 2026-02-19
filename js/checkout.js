import { getCart } from './shopping-cart.js'

const continueButton = document.getElementById("continue-button");

continueButton.addEventListener("click", () => handleCheckout());

const handleCheckout = async () => {
    const addressForm = document.getElementById("address-form");

    
    const clientId = await getLoggedClient();

    if (!clientId) {
        alert("No hay sesión iniciada. Por favor, inicia sesión.");
        window.location.href = "login.html";
        return;
    }

    const addressData = {
        street: addressForm.street.value.trim(),
        number: addressForm.number.value.trim(),
        city: addressForm.city.value.trim()
    };

    if (!addressData.street || !addressData.number || !addressData.city) {
        alert("Por favor, completa todos los campos de dirección");
        return;
    }

    const existingAddressId = await existingAddress(addressData, clientId);

    let addressId;
    if (existingAddressId) {
        addressId = existingAddressId;
    } else {
        addressId = await createAddress(addressData, clientId);
        console.log("Nueva dirección creada. ID:", addressId);
    }

    if (!addressId) {
        alert("Error al crear o verificar la dirección");
        return;
    }

    const cart = getCart();

    if (cart.length === 0) {
        alert("El carrito está vacío");
        return;
    }

    let total = 0;
    cart.forEach(element => {
        total += element.quantity * element.price;
    });

    const billId = await createBill(clientId, total);

    if (!billId) {
        alert("Error al crear la factura");
        return;
    }

    console.log("Factura creada con ID:", billId);

    const orderId = await createOrder(clientId, total, billId);

    if (!orderId) {
        alert("Error al crear la orden");
        return;
    }

    console.log("Orden creada con ID:", orderId);

    const orderDetailsCreated = await createOrderDetails(orderId, cart);

    if (orderDetailsCreated) {
        alert("¡Compra realizada con éxito!");
        localStorage.removeItem("cart");
        window.location.href = "index.html";
    } else {
        alert("Error al procesar los detalles de la orden");
    }
};

const getLoggedClient = async () => {

    const token = sessionStorage.getItem("access_token");
    

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    try {
        console.log("Intentando obtener usuario autenticado...");
        
        const res = await fetch('https://finalprogramacion3-backend-production.up.railway.app/auth/me', {
            method: 'GET',
            headers: {
                "Authorization": `Bearer ${token}`,
                'Accept': 'application/json',
            },
        });

        console.log("Status de respuesta:", res.status);

        if (res.status === 403) {
            console.log("Acceso prohibido - no hay sesión activa");
            return null;
        }

        if (!res.ok) {
            console.log("Usuario no autenticado, status:", res.status);
            return null;
        }

        const userData = await res.json();
        const clientId = userData.client.id;
        
        console.log("Client ID recibido:", clientId);
        
        if (clientId && clientId !== "null" && clientId !== "") {
            return parseInt(clientId);
        }

        return null;
    } catch (err) {
        console.error("Error al verificar la sesión:", err);
        return null;
    }
};

const createBill = async (clientId, total) => {
    try {
        const billData = {
            bill_number: `BILL-${Date.now()}`,
            discount: 0,
            date: new Date().toISOString().split('T')[0],
            total: total,
            payment_type: 1,
            client_id: clientId
        };

        const res = await fetch('https://finalprogramacion3-backend-production.up.railway.app/bills', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(billData)
        });

        if (!res.ok) throw new Error("Error al crear la factura");
        
        const data = await res.json();
        return data.id_key;
    } catch (err) {
        console.error(err);
        return null;
    }
};

const createAddress = async (addressData, clientId) => {
    try {
        const payload = {
            ...addressData,
            client_id: clientId
        };

        const res = await fetch('https://finalprogramacion3-backend-production.up.railway.app/addresses/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("Error al cargar el domicilio");
        const data = await res.json();
        return data.id_key;
    } catch (err) {
        console.error(err);
        return null;
    }
};

const existingAddress = async (addressData, clientId) => {
    try {
        const res = await fetch('https://finalprogramacion3-backend-production.up.railway.app/addresses/');
        const addresses = await res.json();

        const existing = addresses.find(addr => 
            addr.client_id === clientId &&
            addr.street === addressData.street &&
            addr.number === addressData.number &&
            addr.city === addressData.city
        );

        return existing ? existing.id_key : null;
    } catch (err) {
        console.error(err);
        return null;
    }
};

const createOrder = async (clientId, total, billId) => {
    try {
        const orderData = {
            date: new Date().toISOString(),
            total: total,
            delivery_method: 1,
            status: 1,
            client_id: clientId,
            bill_id: billId 
        };

        const res = await fetch('https://finalprogramacion3-backend-production.up.railway.app/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });

        if (!res.ok) throw new Error("Error al crear la orden");
        
        const data = await res.json();
        return data.id_key;
    } catch (err) {
        console.error(err);
        return null;
    }
};

const createOrderDetails = async (orderId, cart) => {
    try {
        const promises = cart.map(item => {
            const orderDetail = {
                quantity: item.quantity,
                price: item.price,
                order_id: orderId,
                product_id: item.id
            };

            return fetch('https://finalprogramacion3-backend-production.up.railway.app/order_details', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderDetail)
            });
        });

        const results = await Promise.all(promises);
        
        for (let i = 0; i < results.length; i++) {
            if (!results[i].ok) {
                const errorText = await results[i].text();
                console.error(`Error en order detail ${i}:`, errorText);
            }
        }
        
        const allSuccessful = results.every(res => res.ok);
        
        return allSuccessful;
    } catch (err) {
        console.error("Error al crear order details:", err);
        return false;
    }
};