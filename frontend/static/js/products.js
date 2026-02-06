async function loadProducts() {
    const token = localStorage.getItem("access_token");

    try {
        const response = await fetch("http://127.0.0.1:8000/api/products", {
            headers: { "Authorization": `Bearer ${token}` }
        });

        const products = await response.json();
        const container = document.getElementById("productsContainer");

        products.forEach(product => {
            const div = document.createElement("div");
            div.className = "product-card";
            div.innerHTML = `
                <h3>${product.name}</h3>
                <p>Price: ₹${product.price}</p>
                <button onclick="addToCart(${product.id})">Add to Cart</button>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error("Error loading products:", error);
    }
}

async function addToCart(productId) {
    const token = localStorage.getItem("access_token");

    try {
        const response = await fetch("http://127.0.0.1:8000/api/cart", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });

        const data = await response.json();
        if (response.ok) {
            alert("Product added to cart!");
        } else {
            alert(data.detail);
        }
    } catch (error) {
        console.error("Error adding to cart:", error);
    }
}

window.onload = loadProducts;
