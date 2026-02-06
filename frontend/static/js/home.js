// Load featured products on homepage
document.addEventListener('DOMContentLoaded', function() {
    loadFeaturedProducts();
});

// Load featured products
async function loadFeaturedProducts() {
    try {
        const products = await window.apiRequest('/api/products/');
        
        if (products && products.length > 0) {
            // Show first 8 products as featured
            const featuredProducts = products.slice(0, 8);
            displayFeaturedProducts(featuredProducts);
        }
    } catch (error) {
        console.error('Error loading featured products:', error);
    }
}

// Display featured products
function displayFeaturedProducts(products) {
    const featuredProductsEl = document.getElementById('featuredProducts');
    
    if (!featuredProductsEl) return;
    
    featuredProductsEl.innerHTML = products.map(product => createFeaturedProductCard(product)).join('');
}

// Create featured product card
function createFeaturedProductCard(product) {
    const inStock = product.stock_quantity > 0;
    
    return `
        <div class="product-card">
            <img src="${window.getProductImage(product.image_url)}" 
                 alt="${product.name}" 
                 class="product-image"
                 onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'">
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-description">${product.description || ''}</p>
                <div class="product-price">${window.formatPrice(product.price)}</div>
                <button class="add-to-cart-btn" 
                        onclick="addToCartFromHome(${product.id})" 
                        ${!inStock ? 'disabled' : ''}>
                    ${inStock ? 'Add to Cart' : 'Out of Stock'}
                </button>
            </div>
        </div>
    `;
}

// Add to cart from homepage
async function addToCartFromHome(productId) {
    if (!window.isLoggedIn()) {
        window.showMessage('Please login to add items to cart', 'error');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
        return;
    }
    
    try {
        const result = await window.apiRequest('/api/cart/', {
            method: 'POST',
            body: JSON.stringify({
                product_id: productId,
                quantity: 1
            })
        });
        
        if (result) {
            window.showMessage('Product added to cart!', 'success');
            window.updateCartCount();
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
    }
}