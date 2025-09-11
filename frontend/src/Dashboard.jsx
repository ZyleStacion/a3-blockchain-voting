import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [activeProposals, setActiveProposals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch active proposals when component loads
  useEffect(() => {
    fetchActiveProposals();
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

  const handleBuyTickets = () => {
    navigate('/buy-tickets');
  };

  const handleCreateProposal = () => {
    navigate('/create-proposal');
  };

  const handleViewProposal = (proposalId) => {
    navigate(`/vote/${proposalId}`);
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome to Your Dashboard</h1>
        <p>Manage your voting activities and view results here.</p>
      </div>
      
      <div className="dashboard-content">
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