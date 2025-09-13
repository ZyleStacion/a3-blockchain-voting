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
    }, []);

    const handleLogout = () => {
        // Clear user data from localStorage
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setIsLoggedIn(false);
        navigate('/');
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
                <li><Link to="/signup">Register</Link></li>
                {isLoggedIn ? (
                    <li><button onClick={handleLogout} className="navbar-logout-btn">Logout</button></li>
                ) : (
                    <li><Link to="/login">Login</Link></li>
                )}
            </ul>
        </nav>
    )
}

export default Navbar;