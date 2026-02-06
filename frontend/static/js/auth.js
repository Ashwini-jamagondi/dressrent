// auth.js - Authentication JavaScript for Login and Register

// Show/Hide Forms
function showLoginForm() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
}

function showRegisterForm() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    const messageEl = document.getElementById('loginMessage');
    
    // Clear previous messages
    messageEl.className = 'form-message';
    messageEl.style.display = 'none';
    
    try {
        // Create form data for OAuth2
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_URL}/api/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }
        
        // Store token in memory (not localStorage)
        window.setAuthToken(data.access_token);
        
        // Get user info
        const userResponse = await fetch(`${API_URL}/api/users/me`, {
            headers: {
                'Authorization': `Bearer ${data.access_token}`
            }
        });
        
        if (userResponse.ok) {
            const userData = await userResponse.json();
            window.setCurrentUser(userData);
        }
        
        // Show success message
        messageEl.textContent = 'Login successful! Redirecting...';
        messageEl.className = 'form-message success';
        messageEl.style.display = 'block';
        
        // Redirect to home page
        setTimeout(() => {
            window.location.href = '/home';
        }, 1000);
        
    } catch (error) {
        messageEl.textContent = error.message;
        messageEl.className = 'form-message error';
        messageEl.style.display = 'block';
    }
}

// Handle Register
async function handleRegister(event) {
    event.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const fullName = document.getElementById('registerFullName').value;
    const phone = document.getElementById('registerPhone').value;
    const password = document.getElementById('registerPassword').value;
    const confirmPassword = document.getElementById('registerConfirmPassword').value;
    const messageEl = document.getElementById('registerMessage');
    
    // Clear previous messages
    messageEl.className = 'form-message';
    messageEl.style.display = 'none';
    
    // Validate passwords match
    if (password !== confirmPassword) {
        messageEl.textContent = 'Passwords do not match!';
        messageEl.className = 'form-message error';
        messageEl.style.display = 'block';
        return;
    }
    
    // Validate password length
    if (password.length < 6) {
        messageEl.textContent = 'Password must be at least 6 characters long!';
        messageEl.className = 'form-message error';
        messageEl.style.display = 'block';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                username: username,
                password: password,
                full_name: fullName || null,
                phone: phone || null
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Registration failed');
        }
        
        // Show success message
        messageEl.textContent = 'Registration successful! Please login.';
        messageEl.className = 'form-message success';
        messageEl.style.display = 'block';
        
        // Clear form
        document.getElementById('registerEmail').value = '';
        document.getElementById('registerUsername').value = '';
        document.getElementById('registerFullName').value = '';
        document.getElementById('registerPhone').value = '';
        document.getElementById('registerPassword').value = '';
        document.getElementById('registerConfirmPassword').value = '';
        
        // Switch to login form after 2 seconds
        setTimeout(() => {
            showLoginForm();
        }, 2000);
        
    } catch (error) {
        messageEl.textContent = error.message;
        messageEl.className = 'form-message error';
        messageEl.style.display = 'block';
    }
}

// Check if already logged in on page load
document.addEventListener('DOMContentLoaded', function() {
    if (window.isLoggedIn()) {
        // Already logged in, redirect to products
        window.location.href = '/products';
    }
});
// Attach event listeners when page loads
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('#loginForm form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    const registerForm = document.querySelector('#registerForm form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Check if already logged in
    if (window.isLoggedIn && window.isLoggedIn()) {
        window.location.href = '/home';
    }
});