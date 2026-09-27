import { motion } from 'framer-motion';

export function LoadingSpinner({ size = 24 }) {
  return (
    <div style={{ width: size, height: size }} className="relative">
      {/* Track */}
      <svg viewBox="0 0 24 24" className="w-full h-full absolute inset-0">
        <circle
          cx="12"
          cy="12"
          r="10"
          fill="none"
          stroke="rgba(45,212,191,0.15)"
          strokeWidth="2.5"
        />
      </svg>
      {/* Spinning arc */}
      <motion.svg
        viewBox="0 0 24 24"
        className="w-full h-full absolute inset-0"
        animate={{ rotate: 360 }}
        transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
      >
        <circle
          cx="12"
          cy="12"
          r="10"
          fill="none"
          stroke="#2dd4bf"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeDasharray="20 43"
        />
      </motion.svg>
    </div>
  );
}

export function SuccessCheckmark() {
  return (
    <div className="relative w-20 h-20 mx-auto">
      {/* Burst ring */}
      <motion.div
        className="absolute inset-0"
        initial={{ scale: 0.6, opacity: 0 }}
        animate={{ scale: 1.4, opacity: [0, 0.5, 0] }}
        transition={{ duration: 0.8, delay: 0.3 }}
      >
        <svg viewBox="0 0 80 80" className="w-full h-full">
          <circle
            cx="40"
            cy="40"
            r="36"
            fill="none"
            stroke="#4ade80"
            strokeWidth="1.5"
            opacity="0.4"
          />
        </svg>
      </motion.div>

      {/* Circle */}
      <motion.div
        className="absolute inset-0 flex items-center justify-center"
        initial={{ scale: 0 }}
        animate={{ scale: [0, 1.08, 1] }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <svg viewBox="0 0 80 80" className="w-full h-full">
          <circle
            cx="40"
            cy="40"
            r="34"
            fill="rgba(74,222,128,0.08)"
            stroke="#4ade80"
            strokeWidth="2.5"
          />
        </svg>
      </motion.div>

      {/* Checkmark */}
      <motion.div
        className="absolute inset-0 flex items-center justify-center"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: [0, 1.15, 1], opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.25, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <svg
          width="28"
          height="28"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#4ade80"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </motion.div>
    </div>
  );
}
