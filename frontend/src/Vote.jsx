import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './Auth.css';

function Vote() {
  const { proposalId } = useParams();
  const navigate = useNavigate();
  const [proposal, setProposal] = useState(null);
  const [selectedOption, setSelectedOption] = useState('');
  const [tickets, setTickets] = useState(1);
  const [userId, setUserId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProposal();
  }, [proposalId]);

  const fetchProposal = async () => {
    try {
      const response = await fetch(`http://localhost:8000/vote/proposal/${proposalId}`);
      if (response.ok) {
        const proposalData = await response.json();
        setProposal(proposalData);
      } else {
        setError('Failed to fetch proposal');
      }
    } catch (err) {
      setError('Failed to fetch proposal');
      console.error('Error fetching proposal:', err);
    }
  };

  const handleSubmitVote = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!userId.trim()) {
      setError('Please enter your User ID');
      setLoading(false);
      return;
    }

    if (!selectedOption) {
      setError('Please select an option');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/vote/submit-vote', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          proposal_id: parseInt(proposalId),
          selected_option: selectedOption,
          tickets: parseInt(tickets)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit vote');
      }

      const result = await response.json();
      alert('Vote submitted successfully!');
      navigate('/dashboard');

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!proposal) {
    return (
      <div className="auth-container">
        <div className="auth-form">
          <div className="loading">Loading proposal...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-form" style={{ maxWidth: '600px' }}>
        <h2>{proposal.title}</h2>
        <p style={{ marginBottom: '2rem', color: '#666' }}>{proposal.description}</p>
        
        <form onSubmit={handleSubmitVote}>
          <div className="form-group">
            <label htmlFor="userId">Your User ID:</label>
            <input
              type="text"
              id="userId"
              placeholder="Enter your user ID"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Select your choice:</label>
            <div className="options-container" style={{ marginTop: '1rem' }}>
              {proposal.options.map((option, index) => (
                <label key={index} className="radio-option" style={{
                  display: 'block',
                  marginBottom: '12px',
                  padding: '12px',
                  border: selectedOption === option ? '2px solid #007bff' : '2px solid #e1e5e9',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}>
                  <input
                    type="radio"
                    name="option"
                    value={option}
                    checked={selectedOption === option}
                    onChange={(e) => setSelectedOption(e.target.value)}
                    style={{ marginRight: '10px' }}
                    required
                  />
                  <span style={{ fontWeight: selectedOption === option ? 'bold' : 'normal' }}>
                    {option}
                  </span>
                  {proposal.votes && proposal.votes[option] !== undefined && (
                    <span style={{ float: 'right', color: '#666', fontSize: '0.9em' }}>
                      ({proposal.votes[option]} votes)
                    </span>
                  )}
                </label>
              ))}
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="tickets">Number of tickets to use:</label>
            <input
              type="number"
              id="tickets"
              placeholder="1"
              min="1"
              max="10"
              value={tickets}
              onChange={(e) => setTickets(e.target.value)}
              required
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button 
            type="submit" 
            className="auth-button"
            disabled={loading || !selectedOption}
          >
            {loading ? 'Submitting...' : `Submit Vote (${tickets} ticket${tickets > 1 ? 's' : ''})`}
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

export default Vote;
