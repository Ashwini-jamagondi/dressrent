// Navigation component with profile icon
const API_URL = 'http://127.0.0.1:8000';

async function loadNavigationProfileIcon() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        const response = await fetch(`${API_URL}/api/users/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const userData = await response.json();
            const profileIcons = document.querySelectorAll('.profile-icon');
            
            profileIcons.forEach(icon => {
                if (userData.profile_photo_url) {
                    icon.innerHTML = `<img src="${API_URL}${userData.profile_photo_url}" alt="Profile">`;
                } else {
                    icon.innerHTML = '👤';
                }
                
                // Add user's name as tooltip
                if (userData.full_name || userData.username) {
                    icon.title = userData.full_name || userData.username;
                }
            });
        }
    } catch (error) {
        console.error('Error loading profile icon:', error);
    }
}

// Call this when page loads
document.addEventListener('DOMContentLoaded', loadNavigationProfileIcon);