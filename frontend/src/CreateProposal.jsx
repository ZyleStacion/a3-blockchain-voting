import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

function CreateProposal() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    selectedCharities: []
  });
  const [charities, setCharities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fetchingCharities, setFetchingCharities] = useState(true);

  // Fetch charities when component loads
  useEffect(() => {
    fetchCharities();
  }, []);

  const fetchCharities = async () => {
    try {
      setFetchingCharities(true);
      const response = await fetch('http://localhost:8000/charities/get-all');
      if (response.ok) {
        const data = await response.json();
        setCharities(data.charities || []);
      } else {
        setError('Failed to fetch charities');
      }
    } catch (err) {
      setError('Failed to fetch charities');
      console.error('Error fetching charities:', err);
    } finally {
      setFetchingCharities(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleCharitySelect = (e) => {
    const charityId = parseInt(e.target.value);
    if (charityId && !formData.selectedCharities.includes(charityId)) {
      setFormData({
        ...formData,
        selectedCharities: [...formData.selectedCharities, charityId]
      });
    }
  };

  const removeCharity = (charityId) => {
    setFormData({
      ...formData,
      selectedCharities: formData.selectedCharities.filter(id => id !== charityId)
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.selectedCharities.length === 0) {
      setError('Please select at least one charity option');
      setLoading(false);
      return;
    }

    try {
      // Get charity names for the options
      const selectedCharityNames = formData.selectedCharities.map(charityId => {
        const charity = charities.find(c => c.id === charityId);
        return charity ? charity.name : `Charity ${charityId}`;
      });

      const response = await fetch('http://localhost:8000/vote/create-proposal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: formData.title,
          description: formData.description,
          options: selectedCharityNames
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create proposal');
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
            <label>Charity Options:</label>
            {fetchingCharities ? (
              <p>Loading charities...</p>
            ) : charities.length === 0 ? (
              <p>No charities available. Please add some charities first.</p>
            ) : (
              <>
                <select 
                  onChange={handleCharitySelect} 
                  defaultValue=""
                  style={{
                    width: '100%',
                    padding: '12px 15px',
                    border: '2px solid #e1e5e9',
                    borderRadius: '8px',
                    fontSize: '1rem',
                    backgroundColor: 'white',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    boxSizing: 'border-box',
                    appearance: 'none',
                    backgroundImage: 'url("data:image/svg+xml,%3csvg xmlns=\'http://www.w3.org/2000/svg\' fill=\'none\' viewBox=\'0 0 20 20\'%3e%3cpath stroke=\'%236b7280\' stroke-linecap=\'round\' stroke-linejoin=\'round\' stroke-width=\'1.5\' d=\'M6 8l4 4 4-4\'/%3e%3c/svg%3e")',
                    backgroundPosition: 'right 12px center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: '16px',
                    paddingRight: '40px'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#007bff';
                    e.target.style.boxShadow = '0 0 0 3px rgba(0, 123, 255, 0.1)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = '#e1e5e9';
                    e.target.style.boxShadow = 'none';
                  }}
                  onMouseEnter={(e) => {
                    if (e.target !== document.activeElement) {
                      e.target.style.borderColor = '#b3d7ff';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (e.target !== document.activeElement) {
                      e.target.style.borderColor = '#e1e5e9';
                    }
                  }}
                >
                  <option value="">Select a charity to add</option>
                  {charities
                    .filter(charity => !formData.selectedCharities.includes(charity.id))
                    .map(charity => (
                      <option key={charity.id} value={charity.id}>
                        {charity.name}
                      </option>
                    ))
                  }
                </select>
                
                {formData.selectedCharities.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <p><strong>Selected charities:</strong></p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {formData.selectedCharities.map(charityId => {
                        const charity = charities.find(c => c.id === charityId);
                        return (
                          <div
                            key={charityId}
                            style={{
                              background: '#e3f2fd',
                              padding: '8px 12px',
                              borderRadius: '20px',
                              border: '1px solid #2196f3',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              fontSize: '0.9rem'
                            }}
                          >
                            {charity?.name || `Charity ${charityId}`}
                            <button
                              type="button"
                              onClick={() => removeCharity(charityId)}
                              style={{
                                background: 'transparent',
                                border: 'none',
                                color: '#f44336',
                                cursor: 'pointer',
                                fontSize: '1.2rem',
                                padding: '0',
                                width: '20px',
                                height: '20px',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                              }}
                              title="Remove charity"
                            >
                              ×
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button 
            type="submit" 
            className="auth-button"
            disabled={loading || formData.selectedCharities.length === 0}
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
