import { useState, useRef, useEffect } from "react"

function Navbar({ user, onGetStarted, onLogout }) {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  const initial = user?.email ? user.email[0].toUpperCase() : "U"

  return (
    <header className="flex items-center justify-between px-1 py-[10px]">
      
      {/* Brand */}
      <div className="flex items-center gap-[10px]">
        <span className="flex h-[34px] w-[34px] items-center justify-center rounded-[10px] bg-gradient-to-br from-[#0d9488] to-[#22d3ee] text-white shadow-[0_1px_2px_rgba(7,46,42,0.05),0_8px_20px_-10px_rgba(13,148,136,0.25)]">
          <img
            src="/favicon.svg"
            alt=""
            width="19"
            height="19"
          />
        </span>

        <span className="font-['Space_Grotesk'] text-[1.05rem] font-semibold tracking-[-0.01em] text-[#072e2a]">
          InsightSwarm
        </span>
      </div>

      {/* Auth Actions */}
      {user ? (
        <div className="relative" ref={dropdownRef}>
          {/* Avatar Icon Button */}
          <button
            onClick={() => setDropdownOpen((prev) => !prev)}
            aria-label="User Profile"
            className="flex h-[38px] w-[38px] items-center justify-center rounded-full bg-gradient-to-br from-[#0d9488] to-[#22d3ee] font-['Space_Grotesk'] text-sm font-bold text-white shadow-[0_2px_8px_rgba(13,148,136,0.35)] transition duration-200 hover:scale-105 active:scale-95 focus:outline-none focus:ring-2 focus:ring-[#0d9488]/40"
          >
            {initial}
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <div className="absolute right-0 top-12 z-[100] w-64 overflow-hidden rounded-[18px] border border-[rgba(7,46,42,0.12)] bg-white/95 p-4 shadow-[0_12px_36px_rgba(7,46,42,0.15)] backdrop-blur-xl animate-[modalEntry_0.2s_ease_forwards]">
              
              {/* User Email & Info */}
              <div className="flex items-center gap-3 pb-3 border-b border-[rgba(7,46,42,0.08)]">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#0d9488] to-[#22d3ee] font-['Space_Grotesk'] text-sm font-bold text-white shadow-xs">
                  {initial}
                </span>
                <div className="overflow-hidden">
                  <p className="font-['Space_Grotesk'] text-[0.72rem] font-bold uppercase tracking-wider text-[#0d9488]">
                    Signed in as
                  </p>
                  <p className="truncate font-['Plus_Jakarta_Sans'] text-[0.82rem] font-semibold text-[#072e2a]" title={user.email}>
                    {user.email}
                  </p>
                </div>
              </div>

              {/* Actions */}
              <div className="pt-2">
                <button
                  onClick={() => {
                    setDropdownOpen(false)
                    onLogout()
                  }}
                  className="flex w-full items-center justify-between rounded-[12px] px-3 py-2.5 font-['Space_Grotesk'] text-[0.85rem] font-semibold text-[#3f5f5a] transition duration-200 hover:bg-red-50 hover:text-red-600 active:scale-[0.98]"
                >
                  <span>Logout</span>
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                    <polyline points="16 17 21 12 16 7" />
                    <line x1="21" y1="12" x2="9" y2="12" />
                  </svg>
                </button>
              </div>

            </div>
          )}
        </div>
      ) : (
        /* Get Started */
        <button onClick={onGetStarted} className="group relative inline-flex items-center gap-2 overflow-hidden rounded-full bg-gradient-to-br from-[#0d9488] to-[#22d3ee] px-[22px] py-[10px] font-['Space_Grotesk'] text-[0.88rem] font-semibold tracking-[-0.01em] text-white shadow-[0_2px_8px_rgba(13,148,136,0.35)] transition duration-300 hover:-translate-y-[2px] hover:scale-[1.03] hover:shadow-[0_4px_18px_rgba(13,148,136,0.45)] active:translate-y-0 active:scale-[0.98]">
          
          <span className="absolute -inset-2 -z-0 rounded-full bg-gradient-to-r from-[#22d3ee]/50 via-[#0d9488]/50 to-[#22d3ee]/50 opacity-50 blur-[8px]">
          </span>

          <span className="relative z-10">
            Get Started
          </span>

          <svg
            className="relative z-10 transition-transform duration-300 group-hover:translate-x-[3px]"
            width="16"
            height="16"
            viewBox="0 0 20 20"
            fill="none"
          >
            <path
              d="M4 10h12m0 0l-4-4m4 4l-4 4"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>

        </button>
      )}

    </header>
  )
}

export default Navbar