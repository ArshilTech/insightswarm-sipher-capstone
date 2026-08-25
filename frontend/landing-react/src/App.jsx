import { useState } from "react"
import AuthModal from "./components/AuthModal"
import Navbar from "./components/Navbar"
import Hero from "./components/Hero"
import ShowcaseCards from "./components/ShowcaseCards"
import Footer from "./components/Footer"
import Marquee from "./components/Marquee"
import SwarmBackground from "./components/SwarmBackground"
import HowItWorks from "./components/HowItWorks"

function App() {
  const [authOpen, setAuthOpen] = useState(false)
  const [authMode, setAuthMode] = useState("signup")
  const [authMessage, setAuthMessage] = useState("")
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem("insightswarm_user")
      return savedUser ? JSON.parse(savedUser) : null
    } catch {
      return null
    }
  })

  function openSignup() {
    setAuthMode("signup")
    setAuthMessage("")
    setAuthOpen(true)
  }

  function openSignin() {
    setAuthMode("signin")
    setAuthMessage(
      "Sign in to access your Activity Dashboard"
    )
    setAuthOpen(true)
  }

  function handleLogin(token, profile) {
    if (profile) {
      setUser(profile)
    } else {
      try {
        const savedUser = localStorage.getItem("insightswarm_user")
        setUser(savedUser ? JSON.parse(savedUser) : null)
      } catch {
        setUser(null)
      }
    }
    setAuthOpen(false)
  }

  function handleLogout() {
    localStorage.removeItem("insightswarm_token")
    localStorage.removeItem("insightswarm_user")
    setUser(null)
    try {
      const bc = new BroadcastChannel("insightswarm_auth")
      bc.postMessage({ type: "LOGOUT" })
      bc.close()
    } catch {
      // ignore
    }
  }

  function openWorkspaceSignin() {
    setAuthMode("signin")
    setAuthMessage(
      "Sign in to access InsightSwarm Workspace"
    )
    setAuthOpen(true)
  }

  return (
    <div className="relative min-h-screen overflow-x-hidden text-[#072e2a]">

      <SwarmBackground />

      <div className="relative z-[2] mx-auto max-w-[1180px] px-7 pb-[60px] pt-7">

        <Navbar
          user={user}
          onGetStarted={openSignup}
          onLogout={handleLogout}
        />

        <main>
          <Hero />
          <Marquee />
          <HowItWorks />
          <ShowcaseCards
            onDashboardClick={openSignin}
            onWorkspaceClick={() => window.location.assign("/workspace")}
            onWorkspaceAuthRequired={openWorkspaceSignin}
          />
        </main>

        <Footer />

      </div>

      <AuthModal
        isOpen={authOpen}
        initialMode={authMode}
        contextMessage={authMessage}
        onClose={() => setAuthOpen(false)}
        onLogin={handleLogin}
      />

    </div>
  )
}

export default App
