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
      console.log('Fetching charities from:', 'http://localhost:8000/charities/get-all');
      
      const response = await fetch('http://localhost:8000/charities/get-all');
      
      console.log('Charities response status:', response.status, response.statusText);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Charities data received:', data);
      console.log('Individual charities:', data.charities?.map(c => ({ 
        id: c.id, 
        name: c.name, 
        idType: typeof c.id 
      })));
      
      setCharities(data.charities || []);
    } catch (err) {
      console.error('Error fetching charities:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to load charities';
      setError('Failed to load charities: ' + errorMessage);
    } finally {
      setLoadingCharities(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    console.log(`Form field changed: ${name} = ${value} (type: ${typeof value})`);
    
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate charity selection
    if (!formData.charity_id || formData.charity_id === '') {
      setError('Please select a charity for your proposal.');
      setLoading(false);
      return;
    }

    const charityId = parseInt(formData.charity_id);
    if (isNaN(charityId)) {
      setError('Invalid charity selection. Please select a valid charity.');
      setLoading(false);
      return;
    }

    const requestData = {
      title: formData.title,
      description: formData.description,
      charity_id: charityId
    };

    console.log('Sending proposal request:', requestData);
    console.log('Original charity_id value:', formData.charity_id, 'Type:', typeof formData.charity_id);

    try {
      const response = await fetch('http://localhost:8000/vote/create-proposal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      console.log('Response status:', response.status, response.statusText);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error occurred' }));
        throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Proposal creation result:', result);
      
      if (result.success) {
        alert(`Proposal created successfully! ID: ${result.id}`);
        navigate('/dashboard');
      } else {
        throw new Error(result.message || 'Failed to create proposal');
      }

    } catch (err) {
      console.error('Proposal creation error:', err);
      
      // Handle different error types properly
      let errorMessage = 'An unknown error occurred';
      
      if (typeof err === 'string') {
        errorMessage = err;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      } else if (err && typeof err === 'object') {
        errorMessage = err.detail || err.message || JSON.stringify(err);
      }
      
      setError(errorMessage);
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
                  <option key={charity.id} value={String(charity.id)}>
                    {charity.name} - {charity.contact_email}
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
          
          {error && <div className="error-message">{error}</div>}
          
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
