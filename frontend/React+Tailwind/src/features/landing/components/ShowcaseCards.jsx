const cards = [
  {
    type: "workspace",
    title: "InsightSwarm Workspace",
    description:
      "Submit a research topic, watch agents work in real time, and download a complete report.",
    features: [
      "Real-time progress tracking",
      "Citation-backed PDF export",
      "Built for researchers",
    ],
    button: "Open Workspace",
  },
  {
    type: "dashboard",
    title: "Activity Dashboard",
    description:
      "Inspect agent traces and manage past research runs.",
    features: [
      "Live agent traces",
      "Downloadable past research runs",
      "Built for operators",
    ],
    button: "Open Dashboard",
  },
]

function WorkspaceIcon() {
  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      className="h-7 w-7"
    >
      <rect
        x="6"
        y="10"
        width="36"
        height="28"
        rx="4"
        stroke="currentColor"
        strokeWidth="2.5"
      />
      <path
        d="M6 18h36"
        stroke="currentColor"
        strokeWidth="2.5"
      />
      <circle cx="11" cy="14" r="1.5" fill="currentColor" />
      <circle cx="16" cy="14" r="1.5" fill="currentColor" />
      <circle cx="21" cy="14" r="1.5" fill="currentColor" />
      <path
        d="M14 26l4 4 8-8"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function DashboardIcon() {
  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      className="h-7 w-7"
    >
      <rect
        x="6"
        y="6"
        width="36"
        height="36"
        rx="4"
        stroke="currentColor"
        strokeWidth="2.5"
      />
      <path
        d="M6 18h36"
        stroke="currentColor"
        strokeWidth="2.5"
      />
      <path
        d="M18 18v24"
        stroke="currentColor"
        strokeWidth="2.5"
      />
      <rect
        x="22"
        y="24"
        width="8"
        height="3"
        rx="1"
        fill="currentColor"
        opacity="0.6"
      />
      <rect
        x="22"
        y="30"
        width="12"
        height="3"
        rx="1"
        fill="currentColor"
        opacity="0.4"
      />
      <rect
        x="22"
        y="36"
        width="6"
        height="3"
        rx="1"
        fill="currentColor"
        opacity="0.25"
      />
      <circle
        cx="12"
        cy="24"
        r="2"
        fill="currentColor"
        opacity="0.5"
      />
      <circle
        cx="12"
        cy="30"
        r="2"
        fill="currentColor"
        opacity="0.5"
      />
      <circle
        cx="12"
        cy="36"
        r="2"
        fill="currentColor"
        opacity="0.5"
      />
      <circle cx="11" cy="12" r="1.5" fill="currentColor" />
      <circle cx="16" cy="12" r="1.5" fill="currentColor" />
    </svg>
  )
}

function ShowcaseCards({ onDashboardClick, onWorkspaceClick, onWorkspaceAuthRequired }) {
  function handleCardClick(card) {
    const token = localStorage.getItem("insightswarm_token")

    if (card.type === "workspace") {
      if (!token) {
        if (onWorkspaceAuthRequired) {
          onWorkspaceAuthRequired()
        } else {
          onDashboardClick()
        }
        return
      }
      onWorkspaceClick()
      return
    }

    if (card.type === "dashboard") {
      if (!token) {
        onDashboardClick()
        return
      }
    }

    const dashboardUrl = `${window.location.protocol}//${window.location.hostname}:8501`
    window.open(dashboardUrl, "_blank")
  }

  return (
    <section className="grid grid-cols-1 gap-7 px-1 md:grid-cols-2 [perspective:1400px]">
      {cards.map((card) => (
        <article
          key={card.type}
          onClick={() => handleCardClick(card)}
          className={`
            group relative cursor-pointer overflow-hidden rounded-[22px]
            border border-[rgba(7,46,42,0.1)]
            bg-[linear-gradient(165deg,rgba(255,255,255,0.9),rgba(255,255,255,0.6))]
            backdrop-blur-[14px]
            shadow-[0_8px_24px_rgba(7,46,42,0.08)]
            transition-all duration-[400ms]
            [transform-style:preserve-3d]
            hover:-translate-y-1
            hover:shadow-[0_18px_45px_rgba(7,46,42,0.14)]
          `}
        >
          {/* Hover glow */}
          <div
            className={`
              pointer-events-none absolute inset-[-1px] rounded-[inherit]
              opacity-0 transition-opacity duration-500
              group-hover:opacity-100
              ${
                card.type === "workspace"
                  ? "bg-[radial-gradient(ellipse_at_25%_15%,rgba(34,211,238,0.18),transparent_60%)]"
                  : "bg-[radial-gradient(ellipse_at_75%_15%,rgba(17,94,86,0.16),transparent_60%)]"
              }
            `}
          />

          {/* Content */}
          <div className="relative z-[1] p-[38px_34px_34px]">

            {/* Top */}
            <div className="mb-[26px] flex items-center justify-between">

              {/* Icon */}
              <div
                className={`
                  flex h-[58px] w-[58px] items-center justify-center
                  rounded-[14px] text-white
                  shadow-[0_2px_8px_rgba(7,46,42,0.08)]
                  transition duration-[350ms]
                  group-hover:scale-[1.08]
                  group-hover:-rotate-[4deg]
                  ${
                    card.type === "workspace"
                      ? "bg-gradient-to-br from-[#0d9488] to-[#22d3ee]"
                      : "bg-gradient-to-br from-[#115e56] to-[#0d9488]"
                  }
                `}
              >
                {card.type === "workspace" ? (
                  <WorkspaceIcon />
                ) : (
                  <DashboardIcon />
                )}
              </div>

            </div>

            {/* Title */}
            <h2 className="mb-3 font-['Space_Grotesk'] text-[1.45rem] font-semibold leading-[1.25] tracking-[-0.01em] text-[#072e2a]">
              {card.title}
            </h2>

            {/* Description */}
            <p className="mb-5 text-[0.94rem] leading-[1.65] text-[#3f5f5a]">
              {card.description}
            </p>

            {/* Features */}
            <ul className="mb-7 flex flex-col gap-[9px]">
              {card.features.map((feature) => (
                <li
                  key={feature}
                  className="flex items-center gap-[9px] text-[0.86rem] text-[#3f5f5a]"
                >
                  <span className="h-[5px] w-[5px] shrink-0 rounded-full bg-[#14b8a6]" />
                  {feature}
                </li>
              ))}
            </ul>

            {/* CTA */}
            <div
              className={`
                inline-flex items-center gap-2
                overflow-hidden rounded-[10px]
                px-[22px] py-[11px]
                font-['Space_Grotesk']
                text-[0.9rem] font-semibold text-white
                shadow-[0_2px_8px_rgba(7,46,42,0.08)]
                transition duration-300
                ${
                  card.type === "workspace"
                    ? "bg-gradient-to-br from-[#0d9488] to-[#22d3ee]"
                    : "bg-gradient-to-br from-[#115e56] to-[#0d9488]"
                }
              `}
            >
              <span>{card.button}</span>

              <svg
                width="18"
                height="18"
                viewBox="0 0 20 20"
                fill="none"
                className="transition-transform duration-300 group-hover:translate-x-[3px]"
              >
                <path
                  d="M4 10h12m0 0l-4-4m4 4l-4 4"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>

          </div>
        </article>
      ))}
    </section>
  )
}

export default ShowcaseCards
