function HowItWorks() {
  const steps = [
    {
      number: "01",
      title: "Plan",
      description:
        "Your question is broken into research-ready subtopics an agent can act on independently.",
      video: "/animated/plan.mp4",
    },
    {
      number: "02",
      title: "Research",
      description:
        "Agents search, read and cross check resources in parallel instead of one step at a time",
      video: "/animated/research.mp4",
    },
    {
      number: "03",
      title: "Synthesize",
      description:
        "Finding are merged into a single citation-backend report,ready to read or export.",
      video: "/animated/synthesize.mp4",
    },
  ]

  return (
    <section className="px-1 pb-[68px] pt-2">

      {/* Section title */}
      <h2 className="mb-[40px] text-center font-['Space_Grotesk'] text-[clamp(1.6rem,2.6vw,2.1rem)] font-semibold tracking-[-0.02em] text-[#072e2a]">
        How the swarm works
      </h2>

      {/* Three steps */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">

        {steps.map((step) => (
          <div
            key={step.number}
            className="rounded-[16px] border border-[rgba(7,46,42,0.1)] bg-white/70 p-[30px_26px] backdrop-blur-[8px] transition duration-[350ms] hover:-translate-y-[6px] hover:shadow-[0_12px_30px_rgba(7,46,42,0.12)]"
          >

            {/* Number + video */}
            <div className="mb-4 flex items-center justify-between">

              <span className="inline-block rounded-[8px] bg-[rgba(13,148,136,0.1)] px-[10px] py-1 font-['JetBrains_Mono'] text-[0.85rem] text-[#14b8a6]">
                {step.number}
              </span>

              <video
                src={step.video}
                autoPlay
                muted
                loop
                playsInline
                className="h-[44px] w-[44px] rounded-[8px] object-cover shadow-[0_2px_8px_rgba(7,46,42,0.08)]"
              />

            </div>

            <h3 className="mb-[10px] font-['Space_Grotesk'] text-[1.15rem] font-semibold text-[#072e2a]">
              {step.title}
            </h3>

            <p className="text-[0.92rem] leading-[1.65] text-[#3f5f5a]">
              {step.description}
            </p>

          </div>
        ))}

      </div>
    </section>
  )
}

export default HowItWorks