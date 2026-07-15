import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ResearchHeroAnimation from '../components/ResearchHeroAnimation';
import { LoadingSpinner, SuccessCheckmark } from '../components/Feedback';

const API_BASE = 'http://127.0.0.1:8000/api';


const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.15,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24, scale: 0.97 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: 'spring',
      stiffness: 260,
      damping: 24,
    },
  },
};

const glowVariants = {
  idle: {
    opacity: 1,
    y: 0,
    boxShadow: '0 0 20px rgba(45, 212, 191, 0.05)',
  },
  focused: {
    opacity: 1,
    y: 0,
    boxShadow: '0 0 60px rgba(45, 212, 191, 0.12)',
    transition: { duration: 0.6 },
  },
};

export default function SubmitPage() {
  const [topic, setTopic] = useState('');
  const [instructions, setInstructions] = useState('');
  const depth = 'standard';
  const [loading, setLoading] = useState(false);
  const [runId, setRunId] = useState(null);
  const [error, setError] = useState('');
  const [formFocused, setFormFocused] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const formRef = useRef(null);

  const handleInstructionsChange = (e) => {
    const val = e.target.value;
    setInstructions(val);
    setCharCount(val.length);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!topic.trim()) {
      setError('Please enter a research topic');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_BASE}/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          instructions,
          depth,
          output_format: 'pdf',
        }),
      });

      if (!res.ok) throw new Error('Failed to start research');

      const data = await res.json();
      setRunId(data.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setTopic('');
    setInstructions('');
    setRunId(null);
    setError('');
    setCharCount(0);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center px-4 py-12 sm:py-16">
      {/* Background elements */}
      <div className="bg-blob bg-blob-1" />
      <div className="bg-blob bg-blob-2" />
      <div className="bg-blob bg-blob-3" />
      <div className="noise-overlay" />

      <motion.div
        className="relative z-10 w-full max-w-2xl"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header section with animated hero */}
        <motion.div variants={itemVariants} className="text-center mb-8">
          <div className="mb-4">
            <ResearchHeroAnimation />
          </div>

          <motion.h1
            className="font-[family-name:var(--font-display)] text-3xl sm:text-4xl font-bold tracking-tight mb-3"
            style={{ color: 'var(--color-text-primary)' }}
          >
            Launch{' '}
            <span
              className="bg-clip-text text-transparent"
              style={{
                backgroundImage:
                  'linear-gradient(135deg, var(--color-accent), var(--color-teal-300))',
              }}
            >
              Research
            </span>
          </motion.h1>

          <motion.p
            className="text-sm sm:text-base max-w-md mx-auto"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            Feed your topic to the swarm. Our AI agents will research, synthesize,
            and deliver a comprehensive report.
          </motion.p>
        </motion.div>

        {/* Main form card */}
        <AnimatePresence mode="wait">
          {!runId ? (
            <motion.div
              key="form"
              variants={glowVariants}
              animate={formFocused ? 'focused' : 'idle'}
              className="clay-card p-6 sm:p-10"
              ref={formRef}
              initial={{ opacity: 0, y: 30 }}
              exit={{ opacity: 0, y: -20, scale: 0.97, transition: { duration: 0.3 } }}
            >
              <form onSubmit={handleSubmit} className="space-y-7">
                {/* Topic field */}
                <motion.div variants={itemVariants}>
                  <label className="field-label" htmlFor="topic-input">
                    <span className="label-icon">🎯</span>
                    Research Topic
                  </label>
                  <input
                    id="topic-input"
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    onFocus={() => setFormFocused(true)}
                    onBlur={() => setFormFocused(false)}
                    placeholder="e.g., Impact of quantum computing on cryptography"
                    className="clay-input"
                    disabled={loading}
                    autoComplete="off"
                  />
                </motion.div>

                {/* Instructions field */}
                <motion.div variants={itemVariants}>
                  <div className="flex items-center justify-between mb-2">
                    <label className="field-label mb-0" htmlFor="instructions-input">
                      <span className="label-icon">📝</span>
                      Additional Instructions
                      <span
                        className="text-[0.65rem] font-normal normal-case tracking-normal ml-1"
                        style={{ color: 'var(--color-text-muted)' }}
                      >
                        (optional)
                      </span>
                    </label>
                    <span
                      className="text-xs tabular-nums"
                      style={{
                        color:
                          charCount > 500
                            ? 'var(--color-error)'
                            : 'var(--color-text-muted)',
                      }}
                    >
                      {charCount}/500
                    </span>
                  </div>
                  <textarea
                    id="instructions-input"
                    value={instructions}
                    onChange={handleInstructionsChange}
                    onFocus={() => setFormFocused(true)}
                    onBlur={() => setFormFocused(false)}
                    placeholder="Focus on recent developments, include case studies, compare methodologies..."
                    className="clay-input resize-none"
                    rows={4}
                    maxLength={500}
                    disabled={loading}
                    style={{ lineHeight: '1.6' }}
                  />
                </motion.div>


                {/* Error message */}
                <AnimatePresence>
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, height: 0, y: -8 }}
                      animate={{ opacity: 1, height: 'auto', y: 0 }}
                      exit={{ opacity: 0, height: 0, y: -8 }}
                      transition={{ duration: 0.25 }}
                      className="rounded-xl px-4 py-3 flex items-center gap-3"
                      style={{
                        background: 'var(--color-error-bg)',
                        border: '1px solid rgba(248, 113, 113, 0.2)',
                      }}
                    >
                      <span className="text-base">⚠️</span>
                      <span
                        className="text-sm font-medium"
                        style={{ color: 'var(--color-error)' }}
                      >
                        {error}
                      </span>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Submit button */}
                <motion.div variants={itemVariants}>
                  <motion.button
                    type="submit"
                    className="clay-btn-primary w-full flex items-center justify-center gap-3"
                    disabled={loading || !topic.trim()}
                    whileHover={!loading && topic.trim() ? { scale: 1.015 } : {}}
                    whileTap={!loading && topic.trim() ? { scale: 0.985 } : {}}
                  >
                    {loading ? (
                      <>
                        <LoadingSpinner size={22} />
                        <span>Initiating Research...</span>
                      </>
                    ) : (
                      <>
                        <svg
                          width="20"
                          height="20"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M22 2L11 13" />
                          <path d="M22 2L15 22L11 13L2 9L22 2Z" />
                        </svg>
                        <span>Start Research</span>
                      </>
                    )}
                  </motion.button>
                </motion.div>

                {/* Footer info */}
                <motion.p
                  variants={itemVariants}
                  className="text-center text-xs"
                  style={{ color: 'var(--color-text-muted)' }}
                >
                  Output will be generated as a PDF report
                </motion.p>
              </form>
            </motion.div>
          ) : (
            /* ═══ Success state ═══ */
            <motion.div
              key="success"
              className="clay-card p-8 sm:p-10 text-center"
              initial={{ opacity: 0, y: 30, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, damping: 20 }}
            >
              <div className="mb-6">
                <SuccessCheckmark />
              </div>

              <h2
                className="font-[family-name:var(--font-display)] text-xl sm:text-2xl font-bold mb-3"
                style={{ color: 'var(--color-text-primary)' }}
              >
                Research Initiated!
              </h2>

              <p
                className="text-sm mb-6"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                Your research swarm is now gathering and analyzing data. Track
                progress on the status page.
              </p>

              {/* Run ID display */}
              <div
                className="rounded-xl px-5 py-4 mb-6 inline-block"
                style={{
                  background: 'var(--color-success-bg)',
                  border: '1px solid rgba(74, 222, 128, 0.15)',
                }}
              >
                <span
                  className="text-xs uppercase tracking-widest font-semibold block mb-1"
                  style={{ color: 'var(--color-text-muted)' }}
                >
                  Run ID
                </span>
                <code
                  className="text-sm font-mono font-semibold"
                  style={{ color: 'var(--color-success)' }}
                >
                  {runId}
                </code>
              </div>

              {/* Topic summary */}
              <div
                className="rounded-xl px-5 py-4 mb-8 text-left"
                style={{
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid var(--color-border-subtle)',
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm">🎯</span>
                  <span
                    className="text-xs uppercase tracking-widest font-semibold"
                    style={{ color: 'var(--color-text-muted)' }}
                  >
                    Topic
                  </span>
                </div>
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {topic}
                </p>
                {instructions && (
                  <>
                    <div className="flex items-center gap-2 mt-4 mb-2">
                      <span className="text-sm">📝</span>
                      <span
                        className="text-xs uppercase tracking-widest font-semibold"
                        style={{ color: 'var(--color-text-muted)' }}
                      >
                        Instructions
                      </span>
                    </div>
                    <p
                      className="text-sm leading-relaxed"
                      style={{ color: 'var(--color-text-secondary)' }}
                    >
                      {instructions}
                    </p>
                  </>
                )}
                <div
                  className="flex items-center gap-4 mt-4 pt-3"
                  style={{ borderTop: '1px solid var(--color-border-subtle)' }}
                >
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs">📄</span>
                    <span
                      className="text-xs font-medium"
                      style={{ color: 'var(--color-accent)' }}
                    >
                      PDF Report
                    </span>
                  </div>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex gap-3">
                <motion.button
                  className="clay-btn-primary flex-1 flex items-center justify-center gap-2"
                  whileHover={{ scale: 1.015 }}
                  whileTap={{ scale: 0.985 }}
                  onClick={() => {

                  }}
                >
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <polyline points="12,6 12,12 16,14" />
                  </svg>
                  Track Progress
                </motion.button>

                <motion.button
                  type="button"
                  className="depth-pill"
                  style={{ flex: 'none', padding: '14px 20px' }}
                  onClick={handleReset}
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                >
                  <span className="pill-icon">✨</span>
                  <span className="pill-label">New</span>
                </motion.button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Bottom branding */}
        <motion.div
          variants={itemVariants}
          className="text-center mt-8 flex items-center justify-center gap-2"
        >
          <div
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: 'var(--color-accent)', opacity: 0.5 }}
          />
          <span
            className="text-xs tracking-wider uppercase font-medium"
            style={{ color: 'var(--color-text-muted)' }}
          >
            InsightSwarm
          </span>
          <div
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: 'var(--color-accent)', opacity: 0.5 }}
          />
        </motion.div>
      </motion.div>
    </div>
  );
}
