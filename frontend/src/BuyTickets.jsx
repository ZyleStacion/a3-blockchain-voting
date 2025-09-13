import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

function BuyTickets() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    amount: 1
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [userInfo, setUserInfo] = useState(null);

  // Fetch user info when component loads
  useEffect(() => {
    fetchUserInfo();
  }, []);

  const fetchUserInfo = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Please login to buy tickets');
        return;
      }

      const response = await fetch('http://localhost:8000/auth/user-info', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const user = await response.json();
        setUserInfo(user);
      } else {
        setError('Failed to fetch user information');
      }
    } catch (err) {
      setError('Please login to buy tickets');
      console.error('Error fetching user info:', err);
    }
  };

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
    setSuccess('');

    if (!userInfo) {
      setError('User information not available. Please refresh the page.');
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/vote/buy-tickets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: userInfo.user_id,
          ticket_purchase: parseInt(formData.amount)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to buy tickets');
      }

      const result = await response.json();
      setSuccess(`Successfully purchased ${formData.amount} tickets!`);
      
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Buy Voting Tickets</h2>
        <p>Purchase tickets to participate in community voting</p>
        
        {userInfo && (
          <div className="user-info" style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: '#f0f8ff', borderRadius: '5px' }}>
            <p><strong>Buying tickets for:</strong> {userInfo.username} (ID: {userInfo.user_id})</p>
            <p><strong>Current tickets:</strong> {userInfo.voting_tickets || 0}</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="amount">Number of Tickets:</label>
            <input
              type="number"
              id="amount"
              name="amount"
              placeholder="1"
              min="1"
              max="100"
              value={formData.amount}
              onChange={handleChange}
              required
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}
          
          <button 
            type="submit" 
            className="auth-button"
            disabled={loading || !userInfo}
          >
            {loading ? 'Processing...' : `Buy ${formData.amount} Ticket${formData.amount > 1 ? 's' : ''}`}
          </button>
        </form>
        
        <p>
          <a href="#" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </a>
        </p>
      </div>
    </div>
  );
}

export default BuyTickets;
