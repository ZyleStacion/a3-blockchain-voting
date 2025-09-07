import './Navbar.css'

function Navbar() {
    return (
        <nav className="navbar">
            <div className="navbar-logo">
                <h1>BlockAid</h1>
            </div>
            <ul className="navbar-links">
                <li><a href="#dashboard">Dashboard</a></li>
                <li><a href="#register">Register</a></li>
                <li><a href="#login">Login</a></li>
            </ul>
        </nav>
    )
}

export default Navbar;