import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [activeProposals, setActiveProposals] = useState([]);
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch active proposals when component loads
  useEffect(() => {
    fetchActiveProposals();
    fetchUserInfo();
  }, []);

  const fetchActiveProposals = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/vote/active-proposals');
      if (response.ok) {
        const proposals = await response.json();
        setActiveProposals(proposals);
      }
    } catch (err) {
      setError('Failed to fetch active proposals');
      console.error('Error fetching proposals:', err);
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

  const handleViewProposal = (proposalId) => {
    navigate(`/vote/${proposalId}`);
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
          ) : activeProposals.length > 0 ? (
            <div className="proposals-list">
              {activeProposals.slice(0, 3).map(proposal => (
                <div key={proposal._id} className="proposal-item">
                  <h4>{proposal.title}</h4>
                  <p>{proposal.description.substring(0, 100)}...</p>
                  <button 
                    className="dashboard-button"
                    onClick={() => handleViewProposal(proposal._id)}
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