import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

function CreateProposal() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: ''
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

    try {
      const response = await fetch('http://localhost:8000/vote/create-proposal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: formData.title,
          description: formData.description,
          options: ['Yes', 'No']
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
              This proposal will have <strong>Yes/No</strong> voting options
            </p>
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button 
            type="submit" 
            className="auth-button"
            disabled={loading}
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
