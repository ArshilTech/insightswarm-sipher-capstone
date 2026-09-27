import { useEffect, useState } from "react"

const lines = [
  {
    tag: "planner",
    text: "decomposing query into 4 subtopics",
  },
  {
    tag: "retriever",
    text: "scanning sources across the web",
  },
  {
    tag: "analyst",
    text: "cross-referencing findings",
  },
  {
    tag: "synthesizer",
    text: "drafting citations and structure",
  },
  {
    tag: "report",
    text: "ready for review and export",
  },
]

function AgentConsole() {
  const [lineIndex, setLineIndex] = useState(0)
  const [charIndex, setCharIndex] = useState(0)

  useEffect(() => {
    const currentLine = lines[lineIndex]

    if (charIndex < currentLine.text.length) {
      const timer = setTimeout(() => setCharIndex((previous) => previous + 1), 26)

      return () => clearTimeout(timer)
    }

    const timer = setTimeout(() => {
      if (lineIndex === lines.length - 1) {
        setLineIndex(0)
      } else {
        setLineIndex((previous) => previous + 1)
      }
      setCharIndex(0)
    }, lineIndex === lines.length - 1 ? 1300 : 260)

    return () => clearTimeout(timer)
  }, [lineIndex, charIndex])

  return (
    <div className="w-full max-w-[420px] overflow-hidden rounded-[26px] border border-[rgba(7,46,42,0.1)] bg-white/70 shadow-[0_4px_8px_rgba(7,46,42,0.06),0_30px_60px_-16px_rgba(13,148,136,0.32)] backdrop-blur-[16px]">
      
      {/* Console header */}
      <div className="flex items-center gap-[10px] border-b border-[rgba(7,46,42,0.06)] px-[18px] py-[14px]">

        <div className="flex gap-[6px]">
          <span className="h-2 w-2 rounded-full bg-[rgba(7,46,42,0.14)]" />
          <span className="h-2 w-2 rounded-full bg-[rgba(7,46,42,0.14)]" />
          <span className="h-2 w-2 rounded-full bg-[rgba(7,46,42,0.14)]" />
        </div>

        <span className="ml-1 mr-auto font-['JetBrains_Mono'] text-[0.76rem] text-[#3f5f5a]">
          Agent Activity
        </span>

        <span className="flex items-center gap-[6px] font-['JetBrains_Mono'] text-[0.7rem] text-red-500">
          <span className="h-[7px] w-[7px] animate-pulse rounded-full bg-red-500" />
          Live
        </span>

      </div>

      {/* Console body */}
      <div className="min-h-[210px] p-[18px] font-['JetBrains_Mono'] text-[0.82rem] leading-[1.9] text-[#3f5f5a]">

        {lines.slice(0, lineIndex + 1).map((line, index) => {
          const isCurrentLine = index === lineIndex
          const halfwayPoint = Math.floor(line.text.length / 2)
          // Show cursor only on current line while charIndex has not passed 50% of the text length
          const showCursor = isCurrentLine && charIndex <= halfwayPoint

          return (
            <div
              key={line.tag}
              className="whitespace-nowrap"
            >
              <span className="text-[#0f766e]">
                {line.tag} →
              </span>{" "}
              <span>
                {isCurrentLine
                  ? line.text.slice(0, charIndex)
                  : line.text}
              </span>

              {showCursor && (
                <span className="ml-[3px] inline-block h-[1.1em] w-[7px] translate-y-[2px] animate-pulse bg-[#0d9488]" />
              )}
            </div>
          )
        })}

      </div>
    </div>
  )
}

export default AgentConsole