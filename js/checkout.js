import { getCart } from './shopping-cart.js'

const continueButton = document.getElementById("continue-button");

continueButton.addEventListener("click", () => handleCheckout());

const handleCheckout = async () => {
    const clientForm = document.getElementById("client-form");
    const addressForm = document.getElementById("address-form");

    const email = clientForm.email.value.trim();
    const phone = clientForm.phoneNumber.value.trim();

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert("El email no es válido.");
        return;
    }

    const phoneRegex = /^\d{7,15}$/;
    if (!phoneRegex.test(phone)) {
        alert("El número de teléfono no es válido. Debe tener solo números y entre 7 y 15 dígitos.");
        return;
    }

    const clientData = {
        name: clientForm.firstName.value.trim(),
        lastname: clientForm.lastName.value.trim(),
        email: email,
        telephone: phone
    };

    let clientId = await existingClient(clientData);
    if (!clientId) {
        clientId = await createClient(clientData);
    }

    const addressData = {
        street: addressForm.street.value.trim(),
        number: addressForm.number.value.trim(),
        city: addressForm.city.value.trim()
    };

    const existingAddressId = await existingAddress(addressData, clientId);

    let addressId;
    if (existingAddressId) {
        addressId = existingAddressId;
    } else {
        addressId = await createAddress(addressData, clientId);
        console.log("Nueva dirección creada. ID:", addressId);
    }

    const cart = getCart();

    console.log(cart);
    
};

const createClient = async (clientData) => {
    try {
        const res = await fetch('http://localhost:8000/clients', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(clientData)
        });
        if (!res.ok) throw new Error("Error al cargar el cliente");
        const data = await res.json();
        return data.id_key;
    } catch (err) {
        console.error(err);
        return null;
    }
};

const existingClient = async (clientData) => {
    try {
        const res = await fetch('http://localhost:8000/clients');
        const clients = await res.json();
        const existing = clients.find(c => c.email === clientData.email);
        return existing ? existing.id_key : null;
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

        const res = await fetch('http://localhost:8000/addresses/', {
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
        const res = await fetch('http://localhost:8000/addresses/');
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

const createOrder = (clientData, addressData, cart) => {

    let total = 0;

    cart.forEach(element => {
        total += element.quantity * element.price;
    });

    // {
    //     "id_key": 0,
    //     "date": "2025-11-28T15:14:52.316Z",
    //     "total": 0,
    //     "delivery_method": 1,
    //     "status": 1,
    //     "client_id": 0,
    //     "bill_id": 0
    // }


}
