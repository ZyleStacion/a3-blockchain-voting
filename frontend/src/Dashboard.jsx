import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [activeProposals, setActiveProposals] = useState([]);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedProposal, setSelectedProposal] = useState(null);
  const [voteData, setVoteData] = useState({ tickets: 1, option: '' });
  const [submitting, setSubmitting] = useState(false);

  // Fetch active proposals when component loads
  useEffect(() => {
    fetchActiveProposals();
    fetchUserInfo();
  }, []);

const fetchActiveProposals = async () => {
  try {
    setLoading(true);
    const response = await fetch('http://localhost:8000/charities/get-active');  
    if (response.ok) {
      const data = await response.json();
      // Map charity data to proposals format for compatibility
      const charityProposals = data.charities.map(charity => ({
        _id: charity.id,
        proposal_id: charity.id,
        title: charity.name,
        description: charity.description,
        contact_email: charity.contact_email,
        status: charity.status,         // NEW: include status
        open_time: charity.open_time,   // NEW: include open time
        close_time: charity.close_time  // NEW: include close time
      }));
      setActiveProposals(charityProposals);
    } else {
      setActiveProposals([]);
    }
  } catch (err) {
    setError('Failed to fetch active charities');
    console.error('Error fetching charities:', err);
    setActiveProposals([]);
  } finally {
    setLoading(false);
  }
};

  const fetchUserInfo = async () => {
    try {
      const response = await fetch('http://localhost:8000/auth/user-info', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const user = await response.json();
        setUserInfo(user);
      }
    } catch (err) {
      console.error('Error fetching user info:', err);
    }
  };

  const handleBuyTickets = () => {
    navigate('/buy-tickets');
  };

  const handleCreateProposal = () => {
    navigate('/create-proposal');
  };

  const handleViewProposal = (proposal) => {
    setSelectedProposal(proposal);
    setVoteData({ tickets: 1, option: '' });
  };

  const handleCloseVoting = () => {
    setSelectedProposal(null);
    setVoteData({ tickets: 1, option: '' });
  };

  const handleVoteChange = (e) => {
    setVoteData({
      ...voteData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmitVote = async (e) => {
    e.preventDefault();
    if (!userInfo || !selectedProposal) return;

    setSubmitting(true);
    try {
      const response = await fetch('http://localhost:8000/vote/submit-vote', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          user_id: userInfo.user_id,
          proposal_id: selectedProposal.proposal_id || selectedProposal._id,
          tickets: parseInt(voteData.tickets),
          option: voteData.option
        })
      });

      if (response.ok) {
        alert('Vote submitted successfully!');
        handleCloseVoting();
        // Refresh user info to update ticket count
        await fetchUserInfo();
      } else {
        const errorData = await response.json();
        alert(`Failed to submit vote: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error submitting vote:', error);
      alert('Failed to submit vote. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = async () => {
    try {
      // Call backend logout endpoint
      const token = localStorage.getItem('token');
      if (token) {
        await fetch('http://localhost:8000/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
      // Continue with frontend logout even if API fails
    } finally {
      // Clear user data from localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Dispatch custom event to notify navbar and other components
      window.dispatchEvent(new Event('authStateChanged'));
      
      // Redirect to home page
      navigate('/');
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome to Your Dashboard</h1>
        <p>Manage your voting activities and view results here.</p>
      </div>
      
      <div className="dashboard-content">
        <div className="dashboard-card">
          <h3>Your Account</h3>
          {userInfo ? (
            <div className="user-info">
              <p><strong>Username:</strong> {userInfo.username}</p>
              <p><strong>User ID:</strong> {userInfo.user_id || userInfo.id}</p>
              <p><strong>Donation Balance:</strong> ${userInfo.donation_balance || 0}</p>
              <p><strong>Voting Tickets:</strong> {userInfo.voting_tickets || 0}</p>
              <button className="dashboard-button logout-btn" onClick={handleLogout}>
                Logout
              </button>
            </div>
          ) : (
            <p>Please login/register to view your account information</p>
          )}
        </div>

        <div className="dashboard-card">
          <h3>Buy Tickets</h3>
          <p>Purchase voting tickets to participate in proposals.</p>
          <button className="dashboard-button" onClick={handleBuyTickets}>
            Buy Tickets
          </button>
        </div>
        
        <div className="dashboard-card">
          <h3>Create Proposal</h3>
          <p>Start a new voting proposal for the community.</p>
          <button className="dashboard-button" onClick={handleCreateProposal}>
            Create New Proposal
          </button>
        </div>
        
        <div className="dashboard-card">
          <h3>Active Proposals ({activeProposals.length})</h3>
          <p>Vote on active community proposals.</p>
          {loading ? (
            <p>Loading proposals...</p>
          ) : selectedProposal ? (
            <div className="voting-form" style={{ border: '2px solid #007bff', borderRadius: '8px', padding: '1rem', backgroundColor: '#f8f9fa' }}>
              <h4>Voting on: {selectedProposal.title}</h4>
              <p>{selectedProposal.description}</p>
              
              <form onSubmit={handleSubmitVote}>                
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label htmlFor="tickets" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Tickets to use:</label>
                  <input
                    type="number"
                    id="tickets"
                    name="tickets"
                    min="1"
                    max={userInfo?.voting_tickets || 1}
                    value={voteData.tickets}
                    onChange={handleVoteChange}
                    required
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}
                  />
                  <small style={{ color: '#666', fontSize: '0.9rem' }}>Available tickets: {userInfo?.voting_tickets || 0}</small>
                </div>
                
                <div className="form-buttons" style={{ display: 'flex', gap: '0.5rem', justifyContent: 'space-between' }}>
                  <button 
                    type="submit" 
                    className="dashboard-button"
                    disabled={submitting || !userInfo?.voting_tickets}
                    style={{ flex: 1 }}
                  >
                    {submitting ? 'Submitting...' : 'Submit Vote'}
                  </button>
                  <button 
                    type="button" 
                    className="dashboard-button"
                    onClick={handleCloseVoting}
                    style={{ flex: 1, backgroundColor: '#6c757d' }}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          ) : activeProposals.length > 0 ? (
            <div className="proposals-list">
              {activeProposals.slice(0, 3).map(proposal => (
                <div key={proposal._id} className="proposal-item">
                  <h4>{proposal.title}</h4>
                  <p>{proposal.description ? proposal.description.substring(0, 100) + '...' : 'No description'}</p>
                  <button 
                    className="dashboard-button"
                    onClick={() => handleViewProposal(proposal)}
                  >
                    Vote Now
                  </button>
                </div>
              ))}
              {activeProposals.length > 3 && (
                <button 
                  className="dashboard-button"
                  onClick={() => navigate('/proposals')}
                >
                  View All Proposals
                </button>
              )}
            </div>
          ) : (
            <p>No active proposals</p>
          )}
          {error && <p className="error">{error}</p>}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;