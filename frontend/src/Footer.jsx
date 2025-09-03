import './Footer.css'

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        {/* Left Section */}
        <div className="footer-section">
          <h3>BlockAid</h3>
          <ul className="footer-links">
            <li><a href="#vote">Vote</a></li>
            <li><a href="#results">Live Results</a></li>
          </ul>
        </div>

        {/* Middle Section */}
        <div className="footer-section">
          <h4>Navigation</h4>
          <ul className="footer-links">
            <li><a href="#dashboard">Dashboard</a></li>
            <li><a href="#register">Register</a></li>
            <li><a href="#login">Login</a></li>
          </ul>
        </div>

        {/* Right Section (Social Icons Placeholder) */}
        <div className="footer-section">
          <h4>Connect</h4>
          <div className="social-icons">
            <div className="social-icon">📧</div>
            <div className="social-icon">🐦</div>
            <div className="social-icon">📱</div>
          </div>
        </div>
      </div>
      
      {/* Copyright */}
      <div className="footer-bottom">
        <p>&copy; 2025 BlockAid. All rights reserved.</p>
      </div>
    </footer>
  )
}

export default Footer