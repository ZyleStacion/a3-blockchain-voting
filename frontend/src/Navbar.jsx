import './Navbar.css'
import { Link, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'

function Navbar() {
    const navigate = useNavigate();
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        // Function to check authentication status
        const checkAuthStatus = () => {
            const token = localStorage.getItem('token');
            setIsLoggedIn(!!token);
        };

        // Initial check
        checkAuthStatus();
        
        // Listen for storage changes (when user logs in/out in another tab)
        const handleStorageChange = () => {
            checkAuthStatus();
        };
        
        // Listen for custom auth events (for same-tab login/logout)
        const handleAuthChange = () => {
            checkAuthStatus();
        };

        // Add event listeners
        window.addEventListener('storage', handleStorageChange);
        window.addEventListener('authStateChanged', handleAuthChange);
        
        // Check auth status periodically as a fallback
        const authCheckInterval = setInterval(checkAuthStatus, 1000);
        
        return () => {
            window.removeEventListener('storage', handleStorageChange);
            window.removeEventListener('authStateChanged', handleAuthChange);
            clearInterval(authCheckInterval);
        };
    }, []);

    const handleLogout = async () => {
        try {
            // Call backend logout endpoint
            const token = localStorage.getItem('token');
            if (token) {
                await fetch('http://localhost:8000/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
            }
        } catch (error) {
            console.error('Logout API call failed:', error);
            // Continue with frontend logout even if API fails
        } finally {
            // Clear user data from localStorage
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setIsLoggedIn(false);
            
            // Dispatch custom event to notify other components
            window.dispatchEvent(new Event('authStateChanged'));
            
            navigate('/');
        }
    };

    return (
        <nav className="navbar">
            <div className="navbar-logo">
                <Link to="/">
                    <h1>BlockAid</h1>
                </Link>
            </div>
            <ul className="navbar-links">
                <li><Link to="/dashboard">Dashboard</Link></li>
                {!isLoggedIn && <li><Link to="/signup">Register</Link></li>}
                <li>
                    {isLoggedIn ? (
                        <button onClick={handleLogout} className="navbar-logout-btn">Logout</button>
                    ) : (
                        <Link to="/login">Login</Link>
                    )}
                </li>
            </ul>
        </nav>
    )
}

export default Navbar;