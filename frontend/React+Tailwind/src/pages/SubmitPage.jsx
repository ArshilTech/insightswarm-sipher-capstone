import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import ResearchHeroAnimation from '../components/ResearchHeroAnimation';
import ResearchPipelineAnimation from '../components/ResearchPipelineAnimation';
import { LoadingSpinner } from '../components/Feedback';

const API_BASE = 'http://127.0.0.1:8000/api';

const headingWords = ['Launch', 'Research'];

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
    boxShadow: '0 0 20px rgba(13, 148, 136, 0.06)',
  },
  focused: {
    opacity: 1,
    y: 0,
    boxShadow: '0 0 60px rgba(13, 148, 136, 0.14)',
    transition: { duration: 0.6 },
  },
};

const headingVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.16,
    },
  },
};

const letterVariants = {
  hidden: { opacity: 0, y: 18 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 180,
      damping: 18,
      duration: 0.35,
    },
  },
};

const LANDING_URL = import.meta.env.VITE_LANDING_URL || 'http://localhost:3001';

export default function SubmitPage() {
  const navigate = useNavigate();
  const [topic, setTopic] = useState('');
  
  const handleBackToLanding = (e) => {
    if (window.opener) {
      e.preventDefault();
      window.close();
      // Fallback in case window.close() is blocked or doesn't work
      setTimeout(() => {
        window.location.href = LANDING_URL;
      }, 150);
    }
  };
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

  const handlePipelineComplete = useCallback(() => {
    if (runId) {
      navigate(`/report/${runId}`);
    }
  }, [runId, navigate]);

  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [typedText, setTypedText] = useState('');

  useEffect(() => {
    const currentWord = headingWords[currentWordIndex];
    const prefix = currentWordIndex === 0 ? '' : `${headingWords[0]} `;
    const targetText = currentWordIndex === 0 ? currentWord : `${prefix}${currentWord}`;
    const typingSpeed = 64;
    const wordCompletePause = 420;
    const fullPhrasePause = 520;
    let timeout;

    if (typedText !== targetText) {
      timeout = setTimeout(
        () => setTypedText(targetText.slice(0, typedText.length + 1)),
        typingSpeed
      );
    } else if (currentWordIndex < headingWords.length - 1) {
      timeout = setTimeout(() => {
        setCurrentWordIndex((index) => index + 1);
      }, wordCompletePause);
    } else {
      timeout = setTimeout(() => {
        setCurrentWordIndex(0);
        setTypedText('');
      }, fullPhrasePause);
    }

    return () => clearTimeout(timeout);
  }, [typedText, currentWordIndex]);

  const currentDisplay = typedText;

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-12 sm:py-16">
      {/* Back to Landing Page Button */}
      <motion.a
        href={LANDING_URL}
        onClick={handleBackToLanding}
        className="absolute left-4 top-4 z-20 flex items-center gap-2 rounded-xl border border-teal-900/10 bg-white/60 px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-slate-700 shadow-sm backdrop-blur-md transition-all duration-300 hover:border-teal-500/30 hover:bg-white/90 hover:text-teal-600 hover:shadow-[0_8px_20px_-6px_rgba(13,148,136,0.15)] sm:left-8 sm:top-8 sm:px-4 sm:py-2.5 sm:text-xs"
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2, duration: 0.4 }}
        whileHover={{ x: -2 }}
        whileTap={{ scale: 0.97 }}
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="19" y1="12" x2="5" y2="12" />
          <polyline points="12 19 5 12 12 5" />
        </svg>
        <span>Back to Home</span>
      </motion.a>

      <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(circle at top left, rgba(34, 211, 238, 0.18), transparent 36%), radial-gradient(circle at bottom right, rgba(13, 148, 136, 0.18), transparent 38%), linear-gradient(135deg, #eafcf9 0%, #e2f8f4 45%, #dcf3ee 100%)' }} />
      <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(120deg, rgba(255, 255, 255, 0.55), transparent 45%, rgba(13, 148, 136, 0.08))' }} />
      <div className="absolute left-[-8%] top-[-10%] h-48 w-48 rounded-full bg-cyan-300/25 blur-3xl" />
      <div className="absolute bottom-[-6%] right-[-4%] h-56 w-56 rounded-full bg-teal-500/20 blur-3xl" />
      <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "url('data:image/svg+xml,%3Csvg viewBox=\"0 0 256 256\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cfilter id=\"n\"%3E%3CfeTurbulence type=\"fractalNoise\" baseFrequency=\"0.9\" numOctaves=\"4\" stitchTiles=\"stitch\"/%3E%3C/filter%3E%3Crect width=\"100%25\" height=\"100%25\" filter=\"url(%23n)\"/%3E%3C/svg%3E')" }} />

      <motion.div
        className="relative z-10 w-full max-w-2xl"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={itemVariants} className="mb-8 text-center">
          <div className="mb-4">
            <ResearchHeroAnimation />
          </div>

          <motion.h1
            className="mb-3 font-display text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl"
            variants={headingVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.span
              key={currentWordIndex}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.18, ease: 'easeOut' }}
              className="inline-block"
            >
              {currentWordIndex === 1 ? (
                <>
                  <span>{currentDisplay.slice(0, 7)}</span>
                  <span className="bg-linear-to-r from-teal-600 via-teal-500 to-cyan-400 bg-clip-text text-transparent">
                    {currentDisplay.slice(7)}
                  </span>
                </>
              ) : (
                currentDisplay
              )}
            </motion.span>
          </motion.h1>

          <motion.p className="mx-auto max-w-md text-sm text-slate-700 sm:text-base">
            Feed your topic to the swarm. Our AI agents will research, synthesize,
            and deliver a comprehensive report.
          </motion.p>
        </motion.div>

        <AnimatePresence mode="wait">
          {!runId ? (
            <motion.div
              key="form"
              variants={glowVariants}
              animate={formFocused ? 'focused' : 'idle'}
              className="relative overflow-hidden rounded-4xl border border-teal-600/20 bg-white/70 p-6 shadow-[0_30px_80px_-28px_rgba(13,148,136,0.35)] backdrop-blur-2xl sm:p-10"
              ref={formRef}
              initial={{ opacity: 0, y: 30 }}
              exit={{ opacity: 0, y: -20, scale: 0.97, transition: { duration: 0.3 } }}
            >
              <div className="absolute inset-x-0 top-0 h-px bg-linear-to-r from-transparent via-teal-500/60 to-transparent" />
              <form onSubmit={handleSubmit} className="space-y-7">
                <motion.div variants={itemVariants}>
                  <label className="mb-2 block text-sm font-semibold uppercase tracking-[0.22em] text-teal-700/80" htmlFor="topic-input">
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
                    className="w-full rounded-2xl border border-teal-900/10 bg-white/80 px-4 py-3.5 text-[15px] text-slate-900 shadow-[inset_0_1px_0_rgba(255,255,255,0.95)] outline-none transition duration-300 placeholder:text-slate-400 focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"
                    disabled={loading}
                    autoComplete="off"
                  />
                </motion.div>

                <motion.div variants={itemVariants}>
                  <div className="mb-2 flex items-center justify-between">
                    <label className="mb-0 block text-sm font-semibold uppercase tracking-[0.22em] text-teal-700/80" htmlFor="instructions-input">
                      Additional Instructions
                      <span className="ml-1 text-[0.65rem] font-normal normal-case tracking-normal text-slate-500">
                        (optional)
                      </span>
                    </label>
                    <span className={`text-xs tabular-nums ${charCount > 500 ? 'text-rose-500' : 'text-slate-500'}`}>
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
                    className="w-full resize-none rounded-2xl border border-teal-900/10 bg-white/80 px-4 py-3.5 text-[15px] text-slate-900 shadow-[inset_0_1px_0_rgba(255,255,255,0.95)] outline-none transition duration-300 placeholder:text-slate-400 focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10"
                    rows={4}
                    maxLength={500}
                    disabled={loading}
                    style={{ lineHeight: '1.6' }}
                  />
                </motion.div>

                <AnimatePresence>
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, height: 0, y: -8 }}
                      animate={{ opacity: 1, height: 'auto', y: 0 }}
                      exit={{ opacity: 0, height: 0, y: -8 }}
                      transition={{ duration: 0.25 }}
                      className="flex items-center gap-3 rounded-2xl border border-rose-200 bg-rose-50/90 px-4 py-3"
                    >
                      <span className="text-base">⚠️</span>
                      <span className="text-sm font-medium text-rose-600">{error}</span>
                    </motion.div>
                  )}
                </AnimatePresence>

                <motion.div variants={itemVariants}>
                  <motion.button
                    type="submit"
                    className="flex w-full items-center justify-center gap-3 rounded-2xl bg-linear-to-r from-teal-600 via-teal-500 to-cyan-400 px-6 py-3.5 font-semibold text-slate-900 shadow-[0_16px_35px_-12px_rgba(13,148,136,0.45)] transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_20px_40px_-14px_rgba(13,148,136,0.55)] disabled:cursor-not-allowed disabled:opacity-60"
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

                <motion.p variants={itemVariants} className="text-center text-xs text-slate-500">
                  Output will be generated as a PDF report
                </motion.p>
              </form>
            </motion.div>
          ) : (
            <motion.div
              key="pipeline"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, transition: { duration: 0.2 } }}
            >
              <ResearchPipelineAnimation
                isActive={!!runId}
                onComplete={handlePipelineComplete}
                topic={topic}
              />
            </motion.div>
          )}
        </AnimatePresence>

        <motion.div variants={itemVariants} className="mt-8 flex items-center justify-center gap-2 text-center" />
      </motion.div>
    </div>
  );
}
