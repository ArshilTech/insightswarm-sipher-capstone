import { useEffect, useState } from "react"

const AUTH_API = "http://localhost:8000"
const TOKEN_KEY = "insightswarm_token"
const USER_KEY = "insightswarm_user"

function AuthModal({
  isOpen,
  initialMode = "signup",
  contextMessage = "",
  onClose,
  onLogin,
}) {
  const [mode, setMode] = useState(initialMode)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  // Keep mode synchronized when the modal is opened
  // for a different reason.
  useEffect(() => {
    if (isOpen) {
      setMode(initialMode)
      setError("")
      setPassword("")
      setConfirmPassword("")
    }
  }, [isOpen, initialMode])

  // Close with Escape
  useEffect(() => {
    function handleEscape(event) {
      if (event.key === "Escape" && isOpen) {
        onClose()
      }
    }

    document.addEventListener("keydown", handleEscape)

    return () => {
      document.removeEventListener("keydown", handleEscape)
    }
  }, [isOpen, onClose])

  // Prevent background scrolling while modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden"
    }

    return () => {
      document.body.style.overflow = ""
    }
  }, [isOpen])

  if (!isOpen) {
    return null
  }

  async function registerUser() {
    const response = await fetch(`${AUTH_API}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      const message = data.detail

      if (message === "REGISTER_USER_ALREADY_EXISTS") {
        throw new Error(
          "An account with this email already exists."
        )
      }

      if (typeof message === "string") {
        throw new Error(message)
      }

      if (Array.isArray(message)) {
        throw new Error(
          message.map((item) => item.msg || item).join(", ")
        )
      }

      throw new Error(
        "Registration failed. Please try again."
      )
    }

    return data
  }

  async function loginUser() {
    const body = new URLSearchParams()

    body.append("username", email)
    body.append("password", password)

    const response = await fetch(
      `${AUTH_API}/auth/jwt/login`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/x-www-form-urlencoded",
        },
        body,
      }
    )

    const data = await response.json()

    if (!response.ok) {
      const message = data.detail

      if (message === "LOGIN_BAD_CREDENTIALS") {
        throw new Error("Invalid email or password.")
      }

      if (message === "LOGIN_USER_NOT_VERIFIED") {
        throw new Error(
          "Please verify your email first."
        )
      }

      if (typeof message === "string") {
        throw new Error(message)
      }

      throw new Error(
        "Login failed. Please try again."
      )
    }

    return data
  }

  async function fetchCurrentUser(token) {
    const response = await fetch(
      `${AUTH_API}/users/me`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error("Session expired")
    }

    return response.json()
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setError("")

    const cleanEmail = email.trim()

    // Same basic validation as your original auth.js
    if (!cleanEmail || !password) {
      setError("Please fill in all fields.")
      return
    }

    if (mode === "signup") {
      if (password !== confirmPassword) {
        setError("Passwords do not match.")
        return
      }

      if (password.length < 8) {
        setError(
          "Password must be at least 8 characters."
        )
        return
      }
    }

    setLoading(true)

    try {
      if (mode === "signup") {
        await registerUser()

        // Same behavior as original:
        // after registration, switch to Sign In.
        setMode("signin")
        setPassword("")
        setConfirmPassword("")
        setError("")

        // Keep email filled so the user doesn't
        // have to type it again.
        setEmail(cleanEmail)

        return
      }

      const data = await loginUser()

      let profile = {
        email: cleanEmail,
      }

      try {
        profile = await fetchCurrentUser(
          data.access_token
        )
      } catch {
        profile = {
          email: cleanEmail,
        }
      }

      // Preserve the same localStorage keys
      // used by the original application.
      localStorage.setItem(
        TOKEN_KEY,
        data.access_token
      )

      localStorage.setItem(
        USER_KEY,
        JSON.stringify(profile)
      )

      if (onLogin) {
        onLogin(data.access_token, profile)
      }

      onClose()

    } catch (err) {
      setError(
        err.message ||
          "Something went wrong. Please try again."
      )
    } finally {
      setLoading(false)
    }
  }

  function switchMode(newMode) {
    setMode(newMode)
    setError("")
    setPassword("")
    setConfirmPassword("")
  }

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-[rgba(7,46,42,0.35)] p-5 backdrop-blur-[12px]"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose()
        }
      }}
    >
      <div
        className="relative w-full max-w-[420px] rounded-[22px] border border-white/50 bg-[linear-gradient(165deg,rgba(255,255,255,0.92),rgba(255,255,255,0.72))] p-[36px_32px_28px] shadow-[0_8px_32px_rgba(7,46,42,0.12),0_32px_64px_-16px_rgba(13,148,136,0.2),inset_0_1px_0_rgba(255,255,255,0.9)] backdrop-blur-[24px] animate-[modalEntry_0.45s_cubic-bezier(0.22,1,0.36,1)_0.1s_both]"
        onMouseDown={(event) => event.stopPropagation()}
      >

        {/* Close button */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="absolute right-4 top-4 flex h-[34px] w-[34px] items-center justify-center rounded-[10px] bg-[rgba(7,46,42,0.05)] text-[#718985] transition duration-200 hover:bg-[rgba(7,46,42,0.1)] hover:text-[#072e2a]"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
          >
            <path
              d="M5 5l10 10M15 5L5 15"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            />
          </svg>
        </button>

        {/* Header */}
        <div className="mb-6">
          <div className="mb-3 flex items-center gap-[9px] font-['Space_Grotesk'] text-[1rem] font-semibold text-[#072e2a]">
            <span className="flex h-[30px] w-[30px] items-center justify-center rounded-[8px] bg-gradient-to-br from-[#0d9488] to-[#22d3ee]">
              <img
                src="/favicon.svg"
                alt=""
                width="19"
                height="19"
              />
            </span>

            <span>InsightSwarm</span>
          </div>

          {contextMessage && (
            <p className="mb-3 text-[0.82rem] leading-[1.5] text-[#0f766e]">
              {contextMessage}
            </p>
          )}
        </div>

        {/* Tabs */}
        <div className="relative mb-6 flex h-[46px] rounded-[15px] bg-[rgba(7,46,42,0.05)] p-1">

          <div
            className={`absolute left-1 top-1 h-[38px] w-[calc(50%-4px)] rounded-[11px] bg-white shadow-[0_1px_4px_rgba(7,46,42,0.1)] transition-transform duration-[350ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] ${
              mode === "signin"
                ? "translate-x-full"
                : "translate-x-0"
            }`}
          />

          <button
            type="button"
            onClick={() => switchMode("signup")}
            className={`relative z-10 w-1/2 rounded-[11px] font-['Plus_Jakarta_Sans'] text-[0.86rem] font-semibold transition-colors duration-200 ${
              mode === "signup"
                ? "text-[#072e2a]"
                : "text-[#718985]"
            }`}
          >
            Sign Up
          </button>

          <button
            type="button"
            onClick={() => switchMode("signin")}
            className={`relative z-10 w-1/2 rounded-[11px] font-['Plus_Jakarta_Sans'] text-[0.86rem] font-semibold transition-colors duration-200 ${
              mode === "signin"
                ? "text-[#072e2a]"
                : "text-[#718985]"
            }`}
          >
            Sign In
          </button>

        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>

          <div className="flex flex-col gap-4">

            {/* Email */}
            <div className="flex flex-col gap-[6px]">
              <label
                htmlFor="auth-email"
                className="pl-[2px] font-['Plus_Jakarta_Sans'] text-[0.82rem] font-semibold text-[#3f5f5a]"
              >
                Email
              </label>

              <input
                id="auth-email"
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                placeholder="you@example.com"
                autoComplete="email"
                required
                className="w-full rounded-[14px] border-[1.5px] border-[rgba(7,46,42,0.12)] bg-white/60 px-4 py-3 font-['Plus_Jakarta_Sans'] text-[0.9rem] text-[#072e2a] outline-none transition duration-200 placeholder:text-[#718985] placeholder:opacity-60 focus:border-[#0d9488] focus:bg-white/85 focus:shadow-[0_0_0_3px_rgba(13,148,136,0.1)]"
              />
            </div>

            {/* Password */}
            <div className="flex flex-col gap-[6px]">
              <label
                htmlFor="auth-password"
                className="pl-[2px] font-['Plus_Jakarta_Sans'] text-[0.82rem] font-semibold text-[#3f5f5a]"
              >
                Password
              </label>

              <input
                id="auth-password"
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder={
                  mode === "signup"
                    ? "Min 8 characters"
                    : "Your password"
                }
                autoComplete={
                  mode === "signup"
                    ? "new-password"
                    : "current-password"
                }
                required
                minLength={mode === "signup" ? 8 : undefined}
                className="w-full rounded-[14px] border-[1.5px] border-[rgba(7,46,42,0.12)] bg-white/60 px-4 py-3 font-['Plus_Jakarta_Sans'] text-[0.9rem] text-[#072e2a] outline-none transition duration-200 placeholder:text-[#718985] placeholder:opacity-60 focus:border-[#0d9488] focus:bg-white/85 focus:shadow-[0_0_0_3px_rgba(13,148,136,0.1)]"
              />
            </div>

            {/* Confirm password */}
            {mode === "signup" && (
              <div className="flex flex-col gap-[6px]">
                <label
                  htmlFor="auth-confirm"
                  className="pl-[2px] font-['Plus_Jakarta_Sans'] text-[0.82rem] font-semibold text-[#3f5f5a]"
                >
                  Confirm Password
                </label>

                <input
                  id="auth-confirm"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(
                      event.target.value
                    )
                  }
                  placeholder="Re-enter password"
                  autoComplete="new-password"
                  required
                  minLength={8}
                  className="w-full rounded-[14px] border-[1.5px] border-[rgba(7,46,42,0.12)] bg-white/60 px-4 py-3 font-['Plus_Jakarta_Sans'] text-[0.9rem] text-[#072e2a] outline-none transition duration-200 placeholder:text-[#718985] placeholder:opacity-60 focus:border-[#0d9488] focus:bg-white/85 focus:shadow-[0_0_0_3px_rgba(13,148,136,0.1)]"
                />
              </div>
            )}

          </div>

          {/* Error */}
          {error && (
            <div className="mt-[10px] px-[2px] text-[0.82rem] font-medium text-[#dc2626] animate-[authShake_0.5s_ease]">
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="relative mt-5 flex w-full items-center justify-center rounded-[14px] bg-gradient-to-br from-[#0d9488] to-[#22d3ee] px-5 py-[13px] font-['Plus_Jakarta_Sans'] text-[0.92rem] font-semibold text-white shadow-[0_2px_12px_rgba(13,148,136,0.3)] transition duration-250 hover:-translate-y-px hover:shadow-[0_4px_20px_rgba(13,148,136,0.4)] active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {loading ? (
              <span className="h-5 w-5 animate-spin rounded-full border-[2.5px] border-white/30 border-t-white" />
            ) : (
              mode === "signup"
                ? "Create Account"
                : "Sign In"
            )}
          </button>

        </form>

        {/* Footer */}
        <div className="mt-5 text-center font-['Plus_Jakarta_Sans'] text-[0.84rem] text-[#718985]">
          {mode === "signup" ? (
            <span>
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => switchMode("signin")}
                className="font-semibold text-[#0d9488] hover:underline"
              >
                Sign in
              </button>
            </span>
          ) : (
            <span>
              Don't have an account?{" "}
              <button
                type="button"
                onClick={() => switchMode("signup")}
                className="font-semibold text-[#0d9488] hover:underline"
              >
                Sign up
              </button>
            </span>
          )}
        </div>

      </div>
    </div>
  )
}

export default AuthModal