// API Base URL
const API_URL = 'http://127.0.0.1:8000';

// Get authentication token from memory
let authToken = null;
let currentUser = null;

// Initialize auth on page load
document.addEventListener('DOMContentLoaded', function() {
    // Note: Token is stored in memory only, not localStorage
    // Users will need to login again when they refresh the page
    checkAuth();
    updateCartCount();
});

// Check if user is authenticated
function checkAuth() {
    if (authToken && currentUser) {
        updateNavForLoggedIn();
    } else {
        updateNavForLoggedOut();
    }
}

// Update navigation for logged-in users
function updateNavForLoggedIn() {
    const loginLink = document.getElementById('loginLink');
    const userProfile = document.getElementById('userProfile');
    const logoutBtn = document.getElementById('logoutBtn');
    const userName = document.getElementById('userName');
    
    if (loginLink) loginLink.style.display = 'none';
    if (userProfile) {
        userProfile.style.display = 'block';
        if (userName && currentUser) {
            userName.textContent = currentUser.username;
        }
    }
    if (logoutBtn) {
        logoutBtn.style.display = 'block';
        logoutBtn.onclick = handleLogout;
    }
}

// Update navigation for logged-out users
function updateNavForLoggedOut() {
    const loginLink = document.getElementById('loginLink');
    const userProfile = document.getElementById('userProfile');
    const logoutBtn = document.getElementById('logoutBtn');
    
    if (loginLink) loginLink.style.display = 'block';
    if (userProfile) userProfile.style.display = 'none';
    if (logoutBtn) logoutBtn.style.display = 'none';
}

// Handle logout
function handleLogout() {
    authToken = null;
    currentUser = null;
    updateNavForLoggedOut();
    window.location.href = '/home';
}

// Check if user is logged in
function isLoggedIn() {
    return authToken !== null;
}

// Require authentication
function requireAuth() {
    if (!isLoggedIn()) {
        showMessage('Please login to continue', 'error');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
        return false;
    }
    return true;
}

// Make authenticated API request
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (authToken) {
        defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, finalOptions);
        
        if (response.status === 401) {
            // Token expired or invalid
            authToken = null;
            currentUser = null;
            showMessage('Session expired. Please login again.', 'error');
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
            return null;
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showMessage(error.message, 'error');
        return null;
    }
}

// Update cart count in navigation
async function updateCartCount() {
    if (!isLoggedIn()) {
        const cartCount = document.getElementById('cartCount');
        if (cartCount) cartCount.textContent = '0';
        return;
    }
    
    try {
        const cartItems = await apiRequest('/api/cart/');
        const cartCount = document.getElementById('cartCount');
        if (cartCount && cartItems) {
            const totalItems = cartItems.reduce((sum, item) => sum + item.quantity, 0);
            cartCount.textContent = totalItems;
        }
    } catch (error) {
        console.error('Error updating cart count:', error);
    }
}

// Show message to user
function showMessage(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Add styles
    Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 25px',
        background: type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#667eea',
        color: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
        zIndex: '10000',
        animation: 'slideIn 0.3s ease-out'
    });
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add CSS animations for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Format price
function formatPrice(price) {
    return `₹${parseFloat(price).toFixed(2)}`;
}

// Get product image URL with fallback
function getProductImage(imageUrl) {
    // If product has image_url, use it; otherwise use category-based placeholder
    if (imageUrl && imageUrl !== 'https://via.placeholder.com/300') {
        return imageUrl;
    }
    return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400';
}

// Filter by category (for homepage)
function filterByCategory(category) {
    window.location.href = `/products?category=${category}`;
}

// Export functions for use in other files
window.API_URL = API_URL;
window.authToken = authToken;
window.currentUser = currentUser;
window.setAuthToken = (token) => { authToken = token; };
window.setCurrentUser = (user) => { currentUser = user; };
window.getAuthToken = () => authToken;
window.getCurrentUser = () => currentUser;
window.apiRequest = apiRequest;
window.requireAuth = requireAuth;
window.isLoggedIn = isLoggedIn;
window.updateCartCount = updateCartCount;
window.showMessage = showMessage;
window.formatPrice = formatPrice;
window.getProductImage = getProductImage;
window.filterByCategory = filterByCategory;
window.checkAuth = checkAuth;