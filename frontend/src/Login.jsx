import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Auth.css';

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

 const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    console.log('Starting login process with:', { username: formData.username });

    try {
      console.log('Sending login request to:', 'http://localhost:8000/auth/login');
      
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Login failed with error:', errorData);
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      console.log('Login successful, received data:', data);

      // Check if we received the expected data structure
      if (!data.access_token) {
        console.error('No access token received:', data);
        throw new Error('Invalid response from server - missing access token');
      }

      // Save JWT token for authentication
      localStorage.setItem('token', data.access_token);
      console.log('Token saved to localStorage');
      
      // Save user info (optional)
      localStorage.setItem('user', JSON.stringify(data));
      console.log('User data saved to localStorage');

      // Dispatch custom event to notify navbar of auth state change
      window.dispatchEvent(new Event('authStateChanged'));

      // Redirect to dashboard
      console.log('Redirecting to dashboard...');
      navigate('/dashboard');
      
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message);
    } finally {
      console.log('Setting loading to false');
      setLoading(false);
    }
  };


  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Login to BlockAid</h2>
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username:</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password:</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          
          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <p>Don't have an account? <Link to="/signup">Sign up here</Link></p>
      </div>
    </div>
  );
}

export default Login;