import './App.css'
import Footer from './Footer'
import Navbar from './Navbar'

function App() {
  return (
    <>
      {/* Navigation Bar */}
      <Navbar />
      
      {/* Logo, title and description */}
      <div className="home-view">
        <div className="content-main">
          <div className="logo">
            <p className="emoji-main" alt="Trophy Emoji">🏆</p>
          </div>
          <div className="home-text">
            <h1>BlockAid</h1>
            <p>Welcome to our blockchain voting app🚀</p>
          </div>
        </div>
      </div>

      {/* Call to action: ask users to donate */}
      <div className="call-to-action">
        <div className="cta-text">
          <h2>Donate Now</h2>
          <p>Disclaimer</p>
        </div>
        <div className="cta-button">
          <button>Cast my vote</button>
        </div>
      </div>

      {/* Spacer to push footer to bottom */}
      <div className="spacer"></div>

      {/* Footer */}
      <Footer />
    </>
  )
}

export default App;