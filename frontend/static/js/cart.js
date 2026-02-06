// Load cart on page load
document.addEventListener('DOMContentLoaded', function() {
    if (!window.requireAuth()) return;
    loadCart();
});

// Load cart items from API
async function loadCart() {
    try {
        const cartItems = await window.apiRequest('/api/cart/');
        
        if (cartItems && cartItems.length > 0) {
            displayCart(cartItems);
            calculateTotals(cartItems);
        } else {
            showEmptyCart();
        }
    } catch (error) {
        console.error('Error loading cart:', error);
        showEmptyCart();
    }
}

// Display empty cart message
function showEmptyCart() {
    const emptyCart = document.getElementById('emptyCart');
    const cartContent = document.getElementById('cartContent');
    
    if (emptyCart) emptyCart.style.display = 'block';
    if (cartContent) cartContent.style.display = 'none';
}

// Display cart items
function displayCart(cartItems) {
    const emptyCart = document.getElementById('emptyCart');
    const cartContent = document.getElementById('cartContent');
    const cartItemsEl = document.getElementById('cartItems');
    
    if (emptyCart) emptyCart.style.display = 'none';
    if (cartContent) cartContent.style.display = 'grid';
    
    if (!cartItemsEl) return;
    
    cartItemsEl.innerHTML = cartItems.map(item => createCartItemHTML(item)).join('');
}

// Create cart item HTML
function createCartItemHTML(item) {
    return `
        <div class="cart-item" data-cart-id="${item.id}">
            <img src="${window.getProductImage(item.product.image_url)}" 
                 alt="${item.product.name}" 
                 class="cart-item-image"
                 onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'">
            <div class="cart-item-details">
                <h3 class="cart-item-name">${item.product.name}</h3>
                <p class="cart-item-price">${window.formatPrice(item.product.price)}</p>
                <div class="cart-item-actions">
                    <div class="quantity-control">
                        <button onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                        <span>${item.quantity}</span>
                        <button onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                    </div>
                    <button class="remove-btn" onclick="removeFromCart(${item.id})">Remove</button>
                </div>
            </div>
        </div>
    `;
}

// Update item quantity
async function updateQuantity(cartItemId, newQuantity) {
    if (newQuantity < 1) {
        removeFromCart(cartItemId);
        return;
    }
    
    try {
        const result = await window.apiRequest(`/api/cart/${cartItemId}`, {
            method: 'PUT',
            body: JSON.stringify({
                quantity: newQuantity
            })
        });
        
        if (result) {
            loadCart();
            window.updateCartCount();
        }
    } catch (error) {
        console.error('Error updating quantity:', error);
    }
}

// Remove item from cart
async function removeFromCart(cartItemId) {
    if (!confirm('Remove this item from cart?')) return;
    
    try {
        const result = await window.apiRequest(`/api/cart/${cartItemId}`, {
            method: 'DELETE'
        });
        
        if (result) {
            window.showMessage('Item removed from cart', 'success');
            loadCart();
            window.updateCartCount();
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
    }
}

// Calculate and display totals
function calculateTotals(cartItems) {
    const subtotal = cartItems.reduce((sum, item) => {
        return sum + (item.product.price * item.quantity);
    }, 0);
    
    const shipping = subtotal > 500 ? 0 : 50; // Free shipping over ₹500
    const tax = subtotal * 0.18; // 18% GST
    const total = subtotal + shipping + tax;
    
    // Update UI
    const subtotalEl = document.getElementById('subtotal');
    const shippingEl = document.getElementById('shipping');
    const taxEl = document.getElementById('tax');
    const totalEl = document.getElementById('total');
    
    if (subtotalEl) subtotalEl.textContent = window.formatPrice(subtotal);
    if (shippingEl) shippingEl.textContent = shipping === 0 ? 'FREE' : window.formatPrice(shipping);
    if (taxEl) taxEl.textContent = window.formatPrice(tax);
    if (totalEl) totalEl.textContent = window.formatPrice(total);
}

// Proceed to checkout
async function proceedToCheckout() {
    try {
        // Get current cart items
        const cartItems = await window.apiRequest('/api/cart/');
        
        if (!cartItems || cartItems.length === 0) {
            window.showMessage('Your cart is empty', 'error');
            return;
        }
        
        // Calculate total
        const subtotal = cartItems.reduce((sum, item) => {
            return sum + (item.product.price * item.quantity);
        }, 0);
        
        const shipping = subtotal > 500 ? 0 : 50;
        const tax = subtotal * 0.18;
        const totalAmount = subtotal + shipping + tax;
        
        // Create order
        const result = await window.apiRequest('/api/orders/', {
            method: 'POST',
            body: JSON.stringify({
                shipping_address: 'Default Address' // You can make this dynamic
            })
        });
        
        if (result) {
            window.showMessage('Order placed successfully!', 'success');
            
            // Show order confirmation
            setTimeout(() => {
                alert(`Order #${result.id} has been placed!\n\nTotal: ${window.formatPrice(totalAmount)}\n\nThank you for shopping with us!`);
                window.location.href = '/products';
            }, 1000);
        }
    } catch (error) {
        console.error('Error during checkout:', error);
        window.showMessage('Failed to place order. Please try again.', 'error');
    }
}