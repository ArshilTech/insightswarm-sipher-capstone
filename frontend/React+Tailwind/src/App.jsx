import { Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './features/landing/LandingPage'
import SubmitPage from './features/research/pages/SubmitPage'
import ReportPage from './features/research/pages/ReportPage'

export default function App() {
  return (
    <div className="min-h-screen selection:bg-teal-500/30">
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/workspace" element={<SubmitPage />} />
        
        {/* Dynamic Parameterized Report Route */}
        <Route path="/report/:runId" element={<ReportPage />} />
        
        {/* Wildcard Catch-all Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}
