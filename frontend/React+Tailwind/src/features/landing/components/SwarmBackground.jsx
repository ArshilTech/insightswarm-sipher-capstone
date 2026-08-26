import { useEffect, useRef } from "react"

function SwarmBackground() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current

    if (!canvas) return

    const ctx = canvas.getContext("2d")

    let width
    let height
    let nodes

    const NODE_COUNT = 26
    const LINK_DIST = 150

    const prefersReduced = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches

    function resize() {
      width = canvas.width = window.innerWidth
      height = canvas.height = Math.min(
        window.innerHeight * 0.9,
        900
      )

      canvas.style.height = `${height}px`
    }

    function makeNodes() {
      nodes = Array.from({ length: NODE_COUNT }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
      }))
    }

    function step() {
      ctx.clearRect(0, 0, width, height)

      nodes.forEach((node) => {
        node.x += node.vx
        node.y += node.vy

        if (node.x < 0 || node.x > width) {
          node.vx *= -1
        }

        if (node.y < 0 || node.y > height) {
          node.vy *= -1
        }
      })

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i]
          const b = nodes[j]

          const dx = a.x - b.x
          const dy = a.y - b.y

          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < LINK_DIST) {
            ctx.strokeStyle = `rgba(13, 148, 136, ${
              0.12 * (1 - dist / LINK_DIST)
            })`

            ctx.lineWidth = 1

            ctx.beginPath()
            ctx.moveTo(a.x, a.y)
            ctx.lineTo(b.x, b.y)
            ctx.stroke()
          }
        }
      }

      nodes.forEach((node) => {
        ctx.fillStyle = "rgba(13, 148, 136, 0.35)"

        ctx.beginPath()
        ctx.arc(node.x, node.y, 1.8, 0, Math.PI * 2)
        ctx.fill()
      })

      if (!prefersReduced) {
        requestAnimationFrame(step)
      }
    }

    resize()
    makeNodes()
    step()

    let resizeTimer

    function handleResize() {
      clearTimeout(resizeTimer)

      resizeTimer = setTimeout(() => {
        resize()
        makeNodes()

        if (prefersReduced) {
          step()
        }
      }, 200)
    }

    window.addEventListener("resize", handleResize)

    return () => {
      window.removeEventListener("resize", handleResize)
      clearTimeout(resizeTimer)
    }
  }, [])

  return (
    <>
      {/* Swarm canvas */}
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 z-0 h-full w-full opacity-[0.55]"
      />

      {/* Gradient mesh */}
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 z-0 animate-[meshShift_22s_ease-in-out_infinite]"
        style={{
          background: `
            radial-gradient(
              680px 520px at 12% 8%,
              rgba(34, 211, 238, 0.16),
              transparent 60%
            ),
            radial-gradient(
              720px 560px at 88% 18%,
              rgba(13, 148, 136, 0.18),
              transparent 62%
            ),
            radial-gradient(
              640px 640px at 50% 78%,
              rgba(184, 236, 226, 0.55),
              transparent 65%
            ),
            radial-gradient(
              900px 700px at 100% 100%,
              rgba(17, 94, 86, 0.10),
              transparent 60%
            ),
            linear-gradient(
              180deg,
              #eafcf9 0%,
              #e2f8f4 40%,
              #dcf3ee 100%
            )
          `,
        }}
      />

      {/* Noise */}
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 z-[1] opacity-[0.025] mix-blend-multiply"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          backgroundRepeat: "repeat",
          backgroundSize: "256px 256px",
        }}
      />
    </>
  )
}

export default SwarmBackground