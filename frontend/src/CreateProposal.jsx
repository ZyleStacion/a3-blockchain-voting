import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

function CreateProposal() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    options: ['', '']
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleOptionChange = (index, value) => {
    const newOptions = [...formData.options];
    newOptions[index] = value;
    setFormData({
      ...formData,
      options: newOptions
    });
  };

  const addOption = () => {
    setFormData({
      ...formData,
      options: [...formData.options, '']
    });
  };

  const removeOption = (index) => {
    if (formData.options.length > 2) {
      const newOptions = formData.options.filter((_, i) => i !== index);
      setFormData({
        ...formData,
        options: newOptions
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate options
    const validOptions = formData.options.filter(option => option.trim() !== '');
    if (validOptions.length < 2) {
      setError('Please provide at least 2 options');
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
          options: validOptions
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
    <div className="auth-container">
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
            <label>Voting Options:</label>
            {formData.options.map((option, index) => (
              <div key={index} style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                <input
                  type="text"
                  placeholder={`Option ${index + 1}`}
                  value={option}
                  onChange={(e) => handleOptionChange(index, e.target.value)}
                  style={{ flex: 1 }}
                  required
                />
                {formData.options.length > 2 && (
                  <button
                    type="button"
                    onClick={() => removeOption(index)}
                    style={{
                      background: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      padding: '8px 12px',
                      cursor: 'pointer'
                    }}
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={addOption}
              style={{
                background: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                padding: '8px 16px',
                cursor: 'pointer',
                marginTop: '10px'
              }}
            >
              Add Option
            </button>
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
