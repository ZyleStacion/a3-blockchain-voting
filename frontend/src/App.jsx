import './App.css'
import { Routes, Route } from 'react-router-dom'
import Navbar from './Navbar'
import Footer from './Footer'
import Home from './Home'
import Login from './Login'
import Signup from './Signup'
import Dashboard from './Dashboard'

function App() {
  return (
    <>
      {/* Navigation Bar */}
      <Navbar />
      
      {/* Routes */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>

      {/* Spacer to push footer to bottom */}
      <div className="spacer"></div>

      {/* Footer */}
      <Footer />
    </>
  )
}

export default App;