import './App.css'

function App() {
  return (
    <>
    {/* Logo, title and description */}
    <div class="home-view">
      <div class="content-main">
        <div class="logo">
          <p class="emoji-main" alt="Trophy Emoji">🏆</p>
        </div>
        <div class="home-text">
          <h1>BlockAid</h1>
          <p>Welcome to our blockchain voting app🚀</p>
        </div>
      </div>
    </div>

    {/* Call to action: ask users to donate */}
    <div class="call-to-action">
      <div class="cta-text">
        <h2>Donate Now</h2>
        <p>Disclaimer</p>
      </div>
      <div class="cta-button">
        <button>Cast my vote</button>
      </div>
    </div>
    </>
  )
}

export default App;