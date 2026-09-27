import AgentConsole from "../../agent-console/AgentConsole"
function Hero() {
  return (
    <section className="grid grid-cols-1 items-center gap-12 px-1 py-16 md:grid-cols-[1.05fr_0.95fr] md:gap-12 md:py-16">
      
      {/* Left side */}
      <div>
        <h1 className="mb-[22px] flex flex-col gap-[6px] font-['Space_Grotesk'] text-[clamp(2.6rem,4.6vw,4rem)] font-bold leading-[1.06] tracking-[-0.03em] text-[#072e2a]">
          
          <span className="animate-[fadeUp_0.8s_ease_forwards] opacity-0 [animation-delay:0.2s]">
            Ask once
          </span>

          <span className="bg-gradient-to-r from-[#0f766e] via-[#0d9488] to-[#22d3ee] bg-[length:200%_200%] bg-clip-text text-transparent animate-[fadeUp_0.8s_ease_forwards,gradientFlow_8s_ease_infinite] opacity-0 [animation-delay:0.6s,0s]">
            A swarm of agents
          </span>

          <span className="animate-[fadeUp_0.8s_ease_forwards] opacity-0 [animation-delay:1s]">
            answers.
          </span>

        </h1>

        <p className="mb-7 max-w-[480px] text-[1.08rem] leading-[1.7] text-[#3f5f5a]">
          InsightSwarm plans, searches, and cross-checks in parallel -
          turning a single research question into a comprehensive,
          citation-backed report.
        </p>

        <div className="flex flex-wrap gap-[10px]">
          {[
            "Planning",
            "Web Retrieval",
            "Multi-Agent Synthesis",
            "Citation Tracking",
            "PDF Export",
          ].map((item) => (
            <span
              key={item}
              className="rounded-full border border-[rgba(7,46,42,0.1)] bg-white/60 px-[13px] py-[7px] font-['JetBrains_Mono'] text-[0.74rem] text-[#115e56] backdrop-blur-[8px] transition duration-300 hover:-translate-y-0.5 hover:border-[rgba(13,148,136,0.35)]"
            >
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center justify-center">
        <AgentConsole />
      </div>

    </section>
  )
}

export default Hero
