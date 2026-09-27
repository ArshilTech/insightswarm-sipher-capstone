function Marquee() {
const items = [
  "Multi-Agent Planning",
  "Web-Scale Retrieval",
  "Citation-Backed Synthesis",
  "Real-Time Agent Traces",
  "Automated PDF Reports",
  "Parallel Research",
]

  return (
    <section className="relative left-1/2 w-screen -translate-x-1/2 overflow-hidden border-y border-[rgba(7,46,42,0.08)] bg-white/35 py-[14px] backdrop-blur-[6px]">
      <div className="flex w-max animate-[marqueeScroll_32s_linear_infinite]">
        
        {[...items, ...items].map((item, index) => (
          <div
            key={index}
            className="flex items-center"
          >
            <span className="px-[22px] font-['JetBrains_Mono'] text-[0.72rem] font-medium tracking-[0.12em] text-[#0f766e]">
              {item}
            </span>

            <span className="h-[4px] w-[4px] rounded-full bg-[#0d9488]/40" />
          </div>
        ))}

      </div>
    </section>
  )
}

export default Marquee