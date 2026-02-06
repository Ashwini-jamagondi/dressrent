// Load user orders on page load
document.addEventListener('DOMContentLoaded', function() {
    if (!window.requireAuth()) return;
    loadOrders();
});

// Load all user orders
async function loadOrders() {
    const ordersContainer = document.getElementById('ordersContainer');
    const loading = document.getElementById('loading');
    
    if (loading) loading.style.display = 'block';
    
    try {
        const orders = await window.apiRequest('/api/orders/');
        
        if (loading) loading.style.display = 'none';
        
        if (!orders || orders.length === 0) {
            displayNoOrders();
            return;
        }
        
        displayOrders(orders);
    } catch (error) {
        console.error('Error loading orders:', error);
        if (loading) loading.style.display = 'none';
        
        if (ordersContainer) {
            ordersContainer.innerHTML = `
                <div class="error-message">
                    <p>Failed to load orders. Please try again.</p>
                </div>
            `;
        }
    }
}

// Display no orders message
function displayNoOrders() {
    const ordersContainer = document.getElementById('ordersContainer');
    
    if (!ordersContainer) return;
    
    ordersContainer.innerHTML = `
        <div class="empty-orders">
            <img src="https://images.unsplash.com/photo-1607083206968-13611e3d76db?w=300" alt="No Orders">
            <h3>No Orders Yet</h3>
            <p>You haven't placed any orders yet</p>
            <a href="/products" class="cta-btn">Start Shopping</a>
        </div>
    `;
}

// Display orders
function displayOrders(orders) {
    const ordersContainer = document.getElementById('ordersContainer');
    
    if (!ordersContainer) return;
    
    // Sort orders by date (newest first)
    const sortedOrders = orders.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    ordersContainer.innerHTML = sortedOrders.map(order => createOrderCard(order)).join('');
}

// Create order card HTML
function createOrderCard(order) {
    const orderDate = new Date(order.created_at).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    const statusClass = getStatusClass(order.status);
    const statusText = order.status.charAt(0).toUpperCase() + order.status.slice(1);
    
    return `
        <div class="order-card">
            <div class="order-header">
                <div class="order-info">
                    <h3>Order #${order.id}</h3>
                    <p class="order-date">Placed on ${orderDate}</p>
                </div>
                <div class="order-status ${statusClass}">
                    ${statusText}
                </div>
            </div>
            
            <div class="order-body">
                <div class="order-items">
                    ${order.order_items.map(item => `
                        <div class="order-item">
                            <img src="${window.getProductImage(item.product.image_url)}" 
                                 alt="${item.product.name}"
                                 onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'">
                            <div class="order-item-details">
                                <h4>${item.product.name}</h4>
                                <p>Quantity: ${item.quantity}</p>
                                <p class="order-item-price">${window.formatPrice(item.price_at_purchase)}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="order-address">
                    <h4>Shipping Address</h4>
                    <p>${order.shipping_address}</p>
                </div>
            </div>
            
            <div class="order-footer">
                <div class="order-total">
                    <strong>Total:</strong> ${window.formatPrice(order.total_amount)}
                </div>
                <button class="view-details-btn" onclick="viewOrderDetails(${order.id})">
                    View Details
                </button>
            </div>
        </div>
    `;
}

// Get status class for styling
function getStatusClass(status) {
    const statusMap = {
        'pending': 'status-pending',
        'confirmed': 'status-confirmed',
        'shipped': 'status-shipped',
        'delivered': 'status-delivered',
        'cancelled': 'status-cancelled'
    };
    
    return statusMap[status.toLowerCase()] || 'status-pending';
}

// View order details
async function viewOrderDetails(orderId) {
    try {
        const order = await window.apiRequest(`/api/orders/${orderId}`);
        
        if (order) {
            showOrderDetailsModal(order);
        }
    } catch (error) {
        console.error('Error loading order details:', error);
        window.showMessage('Failed to load order details', 'error');
    }
}

// Show order details in modal
function showOrderDetailsModal(order) {
    const orderDate = new Date(order.created_at).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const modalHTML = `
        <div class="modal-overlay" onclick="closeOrderModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h2>Order Details - #${order.id}</h2>
                    <button class="modal-close" onclick="closeOrderModal()">×</button>
                </div>
                
                <div class="modal-body">
                    <div class="detail-section">
                        <h3>Order Information</h3>
                        <p><strong>Order Date:</strong> ${orderDate}</p>
                        <p><strong>Status:</strong> <span class="${getStatusClass(order.status)}">${order.status.toUpperCase()}</span></p>
                        <p><strong>Total Amount:</strong> ${window.formatPrice(order.total_amount)}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h3>Items Ordered</h3>
                        ${order.order_items.map(item => `
                            <div class="modal-order-item">
                                <img src="${window.getProductImage(item.product.image_url)}" alt="${item.product.name}">
                                <div>
                                    <h4>${item.product.name}</h4>
                                    <p>Quantity: ${item.quantity}</p>
                                    <p>Price: ${window.formatPrice(item.price_at_purchase)}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="detail-section">
                        <h3>Shipping Address</h3>
                        <p>${order.shipping_address}</p>
                    </div>
                </div>
                
                <div class="modal-footer">
                    <button class="modal-btn" onclick="closeOrderModal()">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// Close order modal
function closeOrderModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) modal.remove();
}

// Cancel order (if needed)
async function cancelOrder(orderId) {
    if (!confirm('Are you sure you want to cancel this order?')) return;
    
    try {
        // This endpoint would need to be implemented in backend
        const result = await window.apiRequest(`/api/orders/${orderId}/cancel`, {
            method: 'PUT'
        });
        
        if (result) {
            window.showMessage('Order cancelled successfully', 'success');
            loadOrders(); // Reload orders
        }
    } catch (error) {
        console.error('Error cancelling order:', error);
        window.showMessage('Failed to cancel order', 'error');
    }
}