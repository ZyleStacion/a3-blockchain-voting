import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

function CreateProposal() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    charity_id: ''
  });
  const [charities, setCharities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingCharities, setLoadingCharities] = useState(true);
  const [error, setError] = useState('');

  // Fetch available charities on component mount
  useEffect(() => {
    fetchCharities();
  }, []);

  const fetchCharities = async () => {
    try {
      setLoadingCharities(true);
      const response = await fetch('http://localhost:8000/charities/get-all');
      
      if (!response.ok) {
        throw new Error('Failed to fetch charities');
      }
      
      const data = await response.json();
      setCharities(data.charities || []);
    } catch (err) {
      setError('Failed to load charities: ' + err.message);
    } finally {
      setLoadingCharities(false);
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

    // ✅ prevent submitting with no charity
    if (!formData.charity_id) {
      setError("Please select a charity before submitting.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/vote/create-proposal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: formData.title,
          description: formData.description,
          // ✅ always send integer to match FastAPI schema
          charity_id: parseInt(formData.charity_id, 10)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        let message = 'Failed to create proposal';

        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            message = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            // FastAPI validation errors
            message = errorData.detail
              .map(err => `${err.loc.join('.')} - ${err.msg}`)
              .join('; ');
          } else if (typeof errorData.detail === 'object') {
            message = JSON.stringify(errorData.detail);
          }
        }

        throw new Error(message);
      }

      const result = await response.json();
      alert('Proposal created successfully!');
      navigate('/dashboard');

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container" style={{ paddingTop: '200px' }}>
      <div className="auth-form" style={{ maxWidth: '600px' }}>
        <h2>Create New Proposal</h2>
        <p>Submit a new voting proposal for the community</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Proposal Title:</label>
            <input
              type="text"
              id="title"
              name="title"
              placeholder="Enter proposal title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="description">Description:</label>
            <textarea
              id="description"
              name="description"
              placeholder="Describe your proposal in detail"
              value={formData.description}
              onChange={handleChange}
              rows="4"
              style={{ 
                width: '100%', 
                padding: '12px 15px',
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                fontSize: '1rem',
                resize: 'vertical',
                boxSizing: 'border-box'
              }}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="charity">Select Charity:</label>
            {loadingCharities ? (
              <div style={{ 
                padding: '12px 15px',
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                background: '#f8f9fa',
                textAlign: 'center'
              }}>
                Loading charities...
              </div>
            ) : (
              <select
                id="charity"
                name="charity_id"
                value={formData.charity_id}
                onChange={handleChange}
                required
                style={{
                  width: '100%',
                  padding: '12px 15px',
                  border: '2px solid #e1e5e9',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  background: 'white',
                  boxSizing: 'border-box',
                  appearance: 'none',
                  backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3E%3Cpolyline points=\'6,9 12,15 18,9\'%3E%3C/polyline%3E%3C/svg%3E")',
                  backgroundRepeat: 'no-repeat',
                  backgroundPosition: 'right 12px center',
                  backgroundSize: '20px',
                  paddingRight: '45px'
                }}
              >
                <option value="">Choose a charity...</option>
                {charities.map((charity) => (
                  <option key={charity.charity_id} value={String(charity.charity_id)}>
                    {charity.charity_id} — {charity.name} ({charity.contact_email || 'no email'})
                  </option>
                ))}
              </select>
            )}
            {charities.length === 0 && !loadingCharities && (
              <p style={{ 
                color: '#dc3545', 
                fontSize: '0.9rem', 
                marginTop: '5px' 
              }}>
                No charities available. Please contact an administrator.
              </p>
            )}
          </div>
          
          <div className="form-group">
            <label>Voting Information:</label>
            <div style={{ 
              background: '#f8f9fa',
              padding: '15px',
              borderRadius: '8px',
              border: '2px solid #e1e5e9',
              fontSize: '0.95rem',
              margin: '10px 0'
            }}>
              <p style={{ margin: '0 0 10px 0' }}>
                <strong>How it works:</strong>
              </p>
              <ul style={{ margin: '0', paddingLeft: '20px' }}>
                <li>Users will vote by allocating their tickets to support this proposal</li>
                <li>More tickets = stronger support for the selected charity</li>
                <li>Each user can cast up to 15 votes total across all proposals</li>
              </ul>
            </div>
          </div>
          
          <div className="form-group">
            <label>Voting Type:</label>
            <p style={{ 
              background: '#f8f9fa',
              padding: '15px',
              borderRadius: '8px',
              border: '2px solid #e1e5e9',
              fontSize: '1rem',
              margin: '10px 0',
              textAlign: 'center'
            }}>
              This proposal will receive <strong>ticket-based votes</strong> supporting the selected charity
            </p>
          </div>
          
          {error && (
            <div className="error-message" style={{ color: 'red', marginTop: '10px' }}>
              {error}
            </div>
          )}
          
          <button 
            type="submit" 
            className="auth-button"
            disabled={loading || loadingCharities || !formData.charity_id}
          >
            {loading ? 'Creating...' : 'Create Proposal'}
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

export default CreateProposal;
