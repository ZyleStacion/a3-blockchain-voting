import './Dashboard.css';

function Dashboard() {
  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome to Your Dashboard</h1>
        <p>Manage your voting activities and view results here.</p>
      </div>
      
      <div className="dashboard-content">
        <div className="dashboard-card">
          <h3>Active Votes</h3>
          <p>View and participate in ongoing voting sessions.</p>
          <button className="dashboard-button">View Votes</button>
        </div>
        
        <div className="dashboard-card">
          <h3>Create Vote</h3>
          <p>Start a new voting session for your organization.</p>
          <button className="dashboard-button">Create New Vote</button>
        </div>
        
        <div className="dashboard-card">
          <h3>Vote History</h3>
          <p>Check your previous voting history and results.</p>
          <button className="dashboard-button">View History</button>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;