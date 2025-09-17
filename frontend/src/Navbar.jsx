import './Navbar.css'
import { Link, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'

function Navbar() {
    const navigate = useNavigate();
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        // Check if user is logged in by checking for token
        const token = localStorage.getItem('token');
        setIsLoggedIn(!!token);
        
        // Listen for storage changes (when user logs in/out in another tab)
        const handleStorageChange = () => {
            const currentToken = localStorage.getItem('token');
            setIsLoggedIn(!!currentToken);
        };
        
        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
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