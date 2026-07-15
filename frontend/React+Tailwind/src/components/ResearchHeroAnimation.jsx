import { motion } from 'framer-motion';

export default function ResearchHeroAnimation() {
  return (
    <div className="relative w-36 h-36 sm:w-40 sm:h-40 mx-auto">
      {/* Outer orbit ring - dashed, rotating clockwise */}
      <motion.div
        className="absolute inset-0"
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      >
        <svg viewBox="0 0 160 160" className="w-full h-full">
          <circle
            cx="80"
            cy="80"
            r="72"
            fill="none"
            stroke="rgba(45,212,191,0.2)"
            strokeWidth="1.5"
            strokeDasharray="8 14"
          />
        </svg>
      </motion.div>

      {/* Inner orbit ring - dashed, rotating counter-clockwise */}
      <motion.div
        className="absolute inset-4"
        animate={{ rotate: -360 }}
        transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
      >
        <svg viewBox="0 0 128 128" className="w-full h-full">
          <circle
            cx="64"
            cy="64"
            r="56"
            fill="none"
            stroke="rgba(45,212,191,0.15)"
            strokeWidth="1"
            strokeDasharray="6 18"
          />
        </svg>
      </motion.div>

      {/* Pulsing center glow */}
      <motion.div
        className="absolute inset-0 flex items-center justify-center"
        animate={{ scale: [0.85, 1.05, 0.85], opacity: [0.3, 0.6, 0.3] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
      >
        <div
          className="w-20 h-20 rounded-full"
          style={{
            background:
              'radial-gradient(circle, rgba(45,212,191,0.2) 0%, transparent 70%)',
          }}
        />
      </motion.div>

      {/* Center magnifying glass icon */}
      <motion.div
        className="absolute inset-0 flex items-center justify-center"
        animate={{ rotate: [-5, 5, -5] }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
      >
        <svg
          width="52"
          height="52"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#2dd4bf"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
          {/* Search lines inside the glass */}
          <line
            x1="8"
            y1="8"
            x2="14"
            y2="8"
            stroke="rgba(45,212,191,0.4)"
            strokeWidth="1.2"
          />
          <line
            x1="8"
            y1="11"
            x2="12"
            y2="11"
            stroke="rgba(45,212,191,0.3)"
            strokeWidth="1.2"
          />
          <line
            x1="8"
            y1="14"
            x2="13"
            y2="14"
            stroke="rgba(45,212,191,0.25)"
            strokeWidth="1.2"
          />
        </svg>
      </motion.div>

      {/* Floating document 1 */}
      <motion.div
        className="absolute"
        style={{ top: '10%', left: '5%' }}
        animate={{
          y: [-4, 6, -4],
          x: [-2, 4, -2],
          rotate: [-8, 5, -8],
          opacity: [0.5, 0.8, 0.5],
        }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
      >
        <svg width="22" height="28" viewBox="0 0 22 28" fill="none">
          <rect
            x="1"
            y="1"
            width="20"
            height="26"
            rx="3"
            stroke="rgba(45,212,191,0.5)"
            strokeWidth="1.2"
            fill="rgba(45,212,191,0.05)"
          />
          <line
            x1="5"
            y1="8"
            x2="17"
            y2="8"
            stroke="rgba(45,212,191,0.3)"
            strokeWidth="1"
          />
          <line
            x1="5"
            y1="12"
            x2="14"
            y2="12"
            stroke="rgba(45,212,191,0.25)"
            strokeWidth="1"
          />
          <line
            x1="5"
            y1="16"
            x2="16"
            y2="16"
            stroke="rgba(45,212,191,0.2)"
            strokeWidth="1"
          />
        </svg>
      </motion.div>

      {/* Floating document 2 */}
      <motion.div
        className="absolute"
        style={{ top: '15%', right: '2%' }}
        animate={{
          y: [3, -5, 3],
          x: [2, -3, 2],
          rotate: [5, -10, 5],
          opacity: [0.4, 0.7, 0.4],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 0.8,
        }}
      >
        <svg width="18" height="24" viewBox="0 0 18 24" fill="none">
          <rect
            x="1"
            y="1"
            width="16"
            height="22"
            rx="2.5"
            stroke="rgba(45,212,191,0.4)"
            strokeWidth="1"
            fill="rgba(45,212,191,0.04)"
          />
          <line
            x1="4"
            y1="7"
            x2="14"
            y2="7"
            stroke="rgba(45,212,191,0.25)"
            strokeWidth="0.8"
          />
          <line
            x1="4"
            y1="11"
            x2="11"
            y2="11"
            stroke="rgba(45,212,191,0.2)"
            strokeWidth="0.8"
          />
        </svg>
      </motion.div>

      {/* Floating document 3 */}
      <motion.div
        className="absolute"
        style={{ bottom: '8%', left: '8%' }}
        animate={{
          y: [2, -6, 2],
          x: [-3, 2, -3],
          rotate: [3, -7, 3],
          opacity: [0.35, 0.65, 0.35],
        }}
        transition={{
          duration: 7,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 1.5,
        }}
      >
        <svg width="16" height="20" viewBox="0 0 16 20" fill="none">
          <rect
            x="1"
            y="1"
            width="14"
            height="18"
            rx="2"
            stroke="rgba(45,212,191,0.35)"
            strokeWidth="1"
            fill="rgba(45,212,191,0.03)"
          />
          <line
            x1="4"
            y1="6"
            x2="12"
            y2="6"
            stroke="rgba(45,212,191,0.2)"
            strokeWidth="0.8"
          />
          <line
            x1="4"
            y1="10"
            x2="9"
            y2="10"
            stroke="rgba(45,212,191,0.15)"
            strokeWidth="0.8"
          />
        </svg>
      </motion.div>

      {/* Floating particles */}
      {[
        { top: '65%', right: '5%', size: 5, delay: 0, dur: 4 },
        { top: '70%', left: '15%', size: 4, delay: 1.2, dur: 5 },
        { top: '25%', right: '25%', size: 3, delay: 2, dur: 4.5 },
      ].map((p, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{
            top: p.top,
            left: p.left,
            right: p.right,
            width: p.size,
            height: p.size,
            background: '#2dd4bf',
          }}
          animate={{
            scale: [0.6, 1.2, 0.6],
            opacity: [0.3, 0.8, 0.3],
            y: [-3, 5, -3],
          }}
          transition={{
            duration: p.dur,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: p.delay,
          }}
        />
      ))}
    </div>
  );
}
