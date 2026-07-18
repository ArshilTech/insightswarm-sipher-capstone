import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const PIPELINE_STEPS = [
  { label: 'Initiated', icon: 'initiated', detail: 'Research swarm activated' },
  { label: 'Scraping Sources', icon: 'sources', detail: 'Crawling the web for data' },
  { label: 'Searching the Web', icon: 'search', detail: 'Deep searching relevant content' },
  { label: 'Collecting Data', icon: 'collect', detail: 'Aggregating information streams' },
  { label: 'Analyzing Patterns', icon: 'analyze', detail: 'Neural pattern recognition' },
  { label: 'Refining Insights', icon: 'refine', detail: 'Distilling key findings' },
  { label: 'Generating Report', icon: 'report', detail: 'Compiling final document' },
];

const STEP_DURATION = 2200; // ms per step

function StepIcon({ type, isActive, isCompleted }) {
  const stroke = isCompleted || isActive ? '#0f766e' : '#64748b';
  const fill = isCompleted || isActive ? 'rgba(20, 184, 166, 0.12)' : 'transparent';
  const commonProps = {
    width: 16,
    height: 16,
    viewBox: '0 0 24 24',
    fill,
    stroke,
    strokeWidth: '1.8',
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
  };

  switch (type) {
    case 'initiated':
      return (
        <svg {...commonProps}>
          <path d="M4 12h16" />
          <path d="M12 4v16" />
          <path d="M6 6l12 12" />
          <path d="M18 6 6 18" />
        </svg>
      );
    case 'sources':
      return (
        <svg {...commonProps}>
          <rect x="4" y="4" width="16" height="16" rx="2" />
          <path d="M8 8h8" />
          <path d="M8 12h6" />
          <path d="M8 16h4" />
        </svg>
      );
    case 'search':
      return (
        <svg {...commonProps}>
          <circle cx="11" cy="11" r="5" />
          <path d="m15 15 4 4" />
        </svg>
      );
    case 'collect':
      return (
        <svg {...commonProps}>
          <rect x="4" y="5" width="16" height="14" rx="2" />
          <path d="M8 9h8" />
          <path d="M8 13h5" />
          <path d="M8 17h3" />
        </svg>
      );
    case 'analyze':
      return (
        <svg {...commonProps}>
          <path d="M6 18V10" />
          <path d="M12 18V6" />
          <path d="M18 18v-7" />
        </svg>
      );
    case 'refine':
      return (
        <svg {...commonProps}>
          <path d="M7 7h10" />
          <path d="M7 12h6" />
          <path d="M7 17h3" />
          <path d="M16 17l2-2" />
          <path d="m18 15 1 1" />
        </svg>
      );
    case 'report':
    default:
      return (
        <svg {...commonProps}>
          <path d="M7 3h7l4 4v14H7z" />
          <path d="M14 3v4h4" />
          <path d="M9 12h6" />
          <path d="M9 16h4" />
        </svg>
      );
  }
}

export default function ResearchPipelineAnimation({ isActive, onComplete, topic }) {
  const [activeStep, setActiveStep] = useState(-1);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [allDone, setAllDone] = useState(false);

  useEffect(() => {
    if (!isActive) return;

    // Start after a brief delay
    const startDelay = setTimeout(() => setActiveStep(0), 300);

    return () => clearTimeout(startDelay);
  }, [isActive]);

  useEffect(() => {
    if (activeStep < 0 || !isActive) return;

    if (activeStep >= PIPELINE_STEPS.length) {
      // All steps done
      setAllDone(true);
      const completeTimeout = setTimeout(() => {
        onComplete?.();
      }, 800);
      return () => clearTimeout(completeTimeout);
    }

    const timer = setTimeout(() => {
      setCompletedSteps((prev) => [...prev, activeStep]);
      setActiveStep((prev) => prev + 1);
    }, STEP_DURATION);

    return () => clearTimeout(timer);
  }, [activeStep, isActive, onComplete]);

  const progress = PIPELINE_STEPS.length > 0
    ? (completedSteps.length / PIPELINE_STEPS.length) * 100
    : 0;

  return (
    <motion.div
      className="rounded-4xl border border-teal-600/20 bg-white/70 p-8 shadow-[0_30px_80px_-28px_rgba(13,148,136,0.35)] backdrop-blur-2xl sm:p-10"
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 200, damping: 20 }}
    >
      {/* Header */}
      <div className="mb-2 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-3 inline-flex items-center gap-2 rounded-full border border-teal-200 bg-teal-50/80 px-4 py-1.5"
        >
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-teal-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-teal-500" />
          </span>
          <span className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-700">
            Processing
          </span>
        </motion.div>

        {topic && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mx-auto max-w-sm truncate text-sm text-slate-500"
          >
            &ldquo;{topic}&rdquo;
          </motion.p>
        )}
      </div>

      {/* Timeline */}
      <div className="relative mx-auto mt-6 max-w-sm pl-10">
        {/* Vertical line track (background) */}
        <div className="absolute left-[18px] top-1 bottom-1 w-[2px] rounded-full bg-slate-200" />

        {/* Vertical line fill (animated) */}
        <motion.div
          className="absolute left-[18px] top-1 w-[2px] rounded-full"
          style={{
            background: 'linear-gradient(180deg, #14b8a6, #2dd4bf, #06b6d4)',
            boxShadow: '0 0 8px rgba(45, 212, 191, 0.5)',
            transformOrigin: 'top',
          }}
          initial={{ height: 0 }}
          animate={{ height: `${progress}%` }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        />

        {/* Steps */}
        {PIPELINE_STEPS.map((step, index) => {
          const isCompleted = completedSteps.includes(index);
          const isCurrentlyActive = activeStep === index;
          const isPending = !isCompleted && !isCurrentlyActive;

          return (
            <motion.div
              key={step.label}
              className="relative mb-5 flex items-start gap-4 last:mb-0"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 + index * 0.06, duration: 0.3 }}
            >
              {/* Node dot */}
              <div className="relative z-10 flex-shrink-0">
                <AnimatePresence mode="wait">
                  {isCompleted ? (
                    <motion.div
                      key="completed"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 15 }}
                      className="flex h-[22px] w-[22px] items-center justify-center rounded-full bg-teal-500 shadow-[0_0_12px_rgba(20,184,166,0.5)]"
                      style={{ marginLeft: '-3px' }}
                    >
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    </motion.div>
                  ) : isCurrentlyActive ? (
                    <motion.div
                      key="active"
                      className="timeline-node-active flex h-[22px] w-[22px] items-center justify-center rounded-full border-2 border-teal-500 bg-teal-50"
                      style={{ marginLeft: '-3px' }}
                      initial={{ scale: 0.6 }}
                      animate={{ scale: 1 }}
                    >
                      <motion.div
                        className="h-2 w-2 rounded-full bg-teal-500"
                        animate={{ scale: [1, 1.3, 1] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                      />
                    </motion.div>
                  ) : (
                    <motion.div
                      key="pending"
                      className="flex h-4 w-4 items-center justify-center rounded-full border-2 border-slate-300 bg-white"
                    />
                  )}
                </AnimatePresence>
              </div>

              {/* Content */}
              <div className={`flex-1 pb-1 transition-all duration-300 ${isPending ? 'opacity-40' : 'opacity-100'}`}>
                <div className="flex items-center gap-2">
                  <span
                    className={`flex h-7 w-7 items-center justify-center rounded-full border transition-all duration-300 ${
                      isCompleted
                        ? 'border-teal-200 bg-teal-50/80'
                        : isCurrentlyActive
                          ? 'border-teal-300 bg-teal-50/70'
                          : 'border-slate-200 bg-white/80'
                    } ${isPending ? 'opacity-70' : 'opacity-100'}`}
                  >
                    <StepIcon type={step.icon} isActive={isCurrentlyActive} isCompleted={isCompleted} />
                  </span>
                  <span
                    className={`text-sm font-semibold transition-colors duration-300 ${
                      isCompleted
                        ? 'text-teal-700'
                        : isCurrentlyActive
                          ? 'text-slate-900'
                          : 'text-slate-400'
                    }`}
                  >
                    {step.label}
                  </span>
                  {isCompleted && (
                    <motion.span
                      initial={{ opacity: 0, x: -5 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="text-[10px] font-medium text-teal-500"
                    >
                      Done
                    </motion.span>
                  )}
                </div>
                {isCurrentlyActive && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-0.5 text-xs text-slate-500"
                  >
                    {step.detail}
                  </motion.p>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Bottom status */}
      <AnimatePresence>
        {allDone && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 flex items-center justify-center gap-2 rounded-2xl border border-emerald-200 bg-emerald-50/80 py-3 text-sm font-semibold text-emerald-700"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            Research complete — loading report...
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress bar at the very bottom */}
      <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-slate-100">
        <motion.div
          className="h-full rounded-full"
          style={{
            background: 'linear-gradient(90deg, #14b8a6, #2dd4bf, #06b6d4)',
          }}
          initial={{ width: '0%' }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        />
      </div>
    </motion.div>
  );
}
