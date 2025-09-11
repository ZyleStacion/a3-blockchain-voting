import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

function BuyTickets() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    user_id: '',
    amount: 1
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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

    try {
      const response = await fetch('http://localhost:8000/vote/buy-tickets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: formData.user_id,
          amount: parseInt(formData.amount)
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
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="user_id">User ID:</label>
            <input
              type="text"
              id="user_id"
              name="user_id"
              placeholder="Enter your user ID"
              value={formData.user_id}
              onChange={handleChange}
              required
            />
          </div>
          
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
            disabled={loading}
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
