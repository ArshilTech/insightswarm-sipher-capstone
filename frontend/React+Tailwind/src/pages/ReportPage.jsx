import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

const LOADING_STEPS = [
  'Initializing neural engine...',
  'Ingesting source documents...',
  'Extracting key entities...',
  'Synthesizing final insights...',
  'Formatting report output...'
]

const BACKEND_BASE = 'http://127.0.0.1:8000'
const API_BASE = `${BACKEND_BASE}/api`

export default function ReportPage() {
  const { runId } = useParams()
  const navigate = useNavigate()
  const [report, setReport] = useState(null)
  const [status, setStatus] = useState('loading') // 'loading' | 'completed' | 'failed'
  const [loadingTextIdx, setLoadingTextIdx] = useState(0)

  // Cycle through loading text to provide an agentic feel during fetching
  useEffect(() => {
    if (status !== 'loading') return
    const interval = setInterval(() => {
      setLoadingTextIdx((prev) => (prev + 1) % LOADING_STEPS.length)
    }, 2000)
    return () => clearInterval(interval)
  }, [status])

  // Fetch production data based on URL parameter with polling if the report is not ready yet
  useEffect(() => {
    if (!runId) return

    let isMounted = true
    let timeoutId = null

    const fetchReport = async () => {
      try {
        const response = await fetch(`${API_BASE}/research/${runId}/report`)
        
        if (response.status === 404) {
          // Report not created yet (backend generation in progress). Retry in 3s.
          if (isMounted) {
            timeoutId = setTimeout(fetchReport, 3000)
          }
          return
        }

        if (!response.ok) throw new Error(`Status: ${response.status}`)
        const data = await response.json()
        
        if (isMounted) {
          setReport(data)
          setStatus(data.status || 'completed')
        }
      } catch (error) {
        console.error('Error fetching research report:', error)
        if (isMounted) {
          setStatus('failed')
        }
      }
    }

    setStatus('loading')
    fetchReport()

    return () => {
      isMounted = false
      if (timeoutId) clearTimeout(timeoutId)
    }
  }, [runId])

  const getFullDownloadUrl = () => {
    if (!report?.download_url) return ''
    if (report.download_url.startsWith('/')) {
      return `${BACKEND_BASE}${report.download_url}`
    }
    return report.download_url
  }

  const getFullPreviewUrl = () => {
    const url = getFullDownloadUrl()
    return url ? `${url}?inline=true` : ''
  }

  const getSourcesCount = () => {
    if (report?.content_json?.sources !== undefined && report.content_json.sources !== null) {
      return report.content_json.sources
    }
    const md = report?.content_json?.raw_markdown || ''
    const citations = md.match(/\[\d+\]/g)
    if (citations) {
      const uniqueCitations = new Set(citations.map(c => c.slice(1, -1)))
      if (uniqueCitations.size > 0) return uniqueCitations.size
    }
    const links = md.match(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g)
    if (links) {
      return new Set(links).size
    }
    return 4 // fallback default
  }

  const getPagesCount = () => {
    if (report?.content_json?.pages !== undefined && report.content_json.pages !== null) {
      return report.content_json.pages
    }
    const md = report?.content_json?.raw_markdown || ''
    if (!md) return 1
    const words = md.trim().split(/\s+/).length
    return Math.max(1, Math.ceil(words / 350))
  }

  const getReadTime = () => {
    const md = report?.content_json?.raw_markdown || ''
    if (!md) return '1 min read'
    const words = md.trim().split(/\s+/).length
    const minutes = Math.max(1, Math.ceil(words / 200))
    return `${minutes} min read`
  }

  const handleDownload = () => {
    const downloadUrl = getFullDownloadUrl()
    if (!downloadUrl) return
    const link = document.createElement('a')
    link.href = downloadUrl
    link.setAttribute('download', `${report.title || 'research-report'}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  const formatDate = (dateString) => {
    const date = dateString ? new Date(dateString) : new Date()
    return date.toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' })
  }

  // 1. PRODUCTION LOADING STATE
  if (status === 'loading' || !report) {
    return (
      <div className="relative flex h-screen w-screen overflow-hidden bg-slate-50 text-slate-900">
        <div className="flex h-full w-full flex-row z-10">
          <div className="flex h-full w-full flex-col justify-between border-r border-slate-200 bg-white p-8 lg:w-[420px] shrink-0">
            <div className="space-y-8 animate-pulse">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-5">
                <div className="h-2 w-2 rounded-full bg-teal-400 animate-ping" />
                <span className="font-mono text-[10px] tracking-widest text-teal-600 uppercase font-bold">
                  Synthesizing...
                </span>
              </div>
              
              <div className="h-24 rounded-xl border border-teal-100/40 bg-teal-50/20 p-4 flex flex-col justify-center overflow-hidden">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={loadingTextIdx}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    transition={{ duration: 0.3 }}
                    className="font-mono text-xs text-teal-700"
                  >
                    {'>'} {LOADING_STEPS[loadingTextIdx]}
                  </motion.div>
                </AnimatePresence>
                <div className="mt-3 h-1 w-full overflow-hidden rounded-full bg-teal-100/50">
                  <motion.div 
                    className="h-full bg-teal-500 rounded-full"
                    initial={{ width: "0%" }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div className="h-6 w-3/4 rounded bg-slate-100" />
                <div className="h-4 w-full rounded bg-slate-100" />
                <div className="h-4 w-5/6 rounded bg-slate-100" />
              </div>
            </div>
          </div>
          
          <div className="hidden h-full flex-1 flex-col bg-slate-50/50 lg:flex items-center justify-center p-8">
            <div className="h-full w-full rounded-2xl border border-slate-200/60 bg-white/50 backdrop-blur-sm shadow-sm flex items-center justify-center">
              <div className="relative flex items-center justify-center">
                <div className="absolute h-16 w-16 animate-ping rounded-full border border-teal-200 opacity-50" />
                <div className="h-8 w-8 animate-spin rounded-full border-2 border-teal-600 border-t-transparent" />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // 2. PRODUCTION FAILED STATE
  if (status === 'failed') {
    return (
      <div className="relative flex h-screen w-screen items-center justify-center overflow-hidden bg-slate-50 text-slate-900">
        <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="max-w-md w-full rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-lg shadow-slate-200/50">
          <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-full bg-red-50 text-xl font-bold text-red-500 border border-red-100">
            !
          </div>
          <h3 className="text-md font-semibold tracking-tight text-slate-900">Unable to Load Report</h3>
          <p className="mt-2 text-xs text-slate-500 leading-relaxed px-4">
            We couldn't retrieve this document. The link may be invalid, or a temporary network error occurred.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="mt-6 w-full rounded-xl bg-slate-900 px-6 py-3.5 text-xs font-bold tracking-wider text-white transition hover:bg-slate-800 shadow-sm"
          >
            RETRY CONNECTION
          </button>
        </motion.div>
      </div>
    )
  }

  // 3. PRODUCTION COMPLETED STATE 
  return (
    <div className="relative flex h-screen w-screen overflow-hidden bg-slate-50 text-slate-900">
      <div className="relative flex h-full w-full flex-col justify-between overflow-y-auto border-r border-slate-200 bg-white p-8 lg:w-[420px] shrink-0 z-10">
        <motion.div 
          initial="hidden" 
          animate="visible" 
          variants={{
            hidden: { opacity: 0 },
            visible: { opacity: 1, transition: { staggerChildren: 0.1 } }
          }}
          className="space-y-8"
        >
          <motion.div variants={{ hidden: { opacity: 0, y: -10 }, visible: { opacity: 1, y: 0 } }} className="flex items-center justify-between border-b border-slate-100 pb-5">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-teal-500 shadow-[0_0_8px_rgba(20,184,166,0.8)]" />
              <span className="font-mono text-[10px] tracking-widest text-teal-700 uppercase font-bold">
                Synthesis Complete
              </span>
            </div>
            <span className="font-mono text-[10px] text-slate-400">ID: {runId}</span>
          </motion.div>

          <motion.div variants={{ hidden: { opacity: 0, x: -10 }, visible: { opacity: 1, x: 0 } }} className="space-y-4">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 leading-tight font-sans">
              {report.title || 'Untitled Report'}
            </h1>
          </motion.div>

          <motion.div variants={{ hidden: { opacity: 0, y: 10 }, visible: { opacity: 1, y: 0 } }} className="space-y-4">
            <h2 className="text-[10px] font-bold tracking-widest text-slate-400 uppercase font-mono">
              Document Analytics
            </h2>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl border border-slate-100 bg-slate-50/50 p-4">
                <p className="font-mono text-[10px] text-slate-500 uppercase">Sources</p>
                <p className="mt-1 text-2xl font-bold text-slate-900">{getSourcesCount()}</p>
              </div>
              <div className="rounded-xl border border-slate-100 bg-slate-50/50 p-4">
                <p className="font-mono text-[10px] text-slate-500 uppercase">Pages</p>
                <p className="mt-1 text-2xl font-bold text-slate-900">{getPagesCount()}</p>
              </div>
            </div>
          </motion.div>

          <motion.div variants={{ hidden: { opacity: 0, y: 10 }, visible: { opacity: 1, y: 0 } }} className="rounded-xl border border-slate-100 bg-slate-50/50 p-4 text-xs space-y-3 font-mono text-slate-600">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Generated</span>
              <span className="text-slate-900 font-medium bg-white px-2 py-1 rounded border border-slate-100">{formatDate(report.created_at)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Read Time</span>
              <span className="text-slate-900 font-medium bg-white px-2 py-1 rounded border border-slate-100">{getReadTime()}</span>
            </div>
          </motion.div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="pt-6">
          <button
            onClick={handleDownload}
            className="group relative w-full overflow-hidden rounded-xl bg-teal-800 py-3.5 text-xs font-bold tracking-wider text-white shadow-lg shadow-teal-900/20 transition-all hover:bg-teal-900 active:scale-[0.98]"
          >
            DOWNLOAD EXPORT (PDF)
          </button>
          <button
            onClick={() => navigate('/')}
            className="group relative mt-3 flex w-full items-center justify-center gap-2 overflow-hidden rounded-xl border border-teal-600/20 bg-white py-3.5 text-xs font-bold tracking-wider text-teal-700 shadow-sm transition-all hover:border-teal-500/40 hover:bg-teal-50 active:scale-[0.98]"
          >
            <span>✨</span>
            <span>NEW REPORT</span>
          </button>
        </motion.div>
      </div>

      <div className="hidden h-full flex-1 flex-col bg-slate-50 lg:flex z-10 p-6 xl:p-8">
        <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2, duration: 0.4 }} className="h-full w-full overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-xl flex flex-col">
          <div className="h-12 border-b border-slate-100 bg-white px-5 flex items-center justify-between shrink-0 text-xs text-slate-600">
            <span className="font-semibold text-slate-700">Document Viewer</span>
          </div>
          <iframe
            title="Research PDF Preview"
            src={getFullPreviewUrl() || '/sample.pdf'}
            className="h-full w-full flex-1 border-0 bg-slate-100/50"
          />
        </motion.div>
      </div>
    </div>
  )
}