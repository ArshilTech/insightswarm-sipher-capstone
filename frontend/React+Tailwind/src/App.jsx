import { Routes, Route, Navigate } from 'react-router-dom'
import SubmitPage from './pages/SubmitPage'
import ReportPage from './pages/ReportPage'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-teal-500/30">
      <Routes>
        {/* Core Submission Routing */}
        <Route path="/" element={<SubmitPage />} />
        
        {/* Dynamic Parameterized Report Route */}
        <Route path="/report/:runId" element={<ReportPage />} />
        
        {/* Wildcard Catch-all Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}