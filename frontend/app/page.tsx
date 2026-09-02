import Link from "next/link"
import { ArrowRightIcon, ChartLineIcon, GaugeIcon, WindIcon } from "lucide-react"

import { SITE } from "@/lib/site"
import { AppHeader } from "@/components/app-header"
import { GitHubIcon } from "@/components/icons"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

const HIGHLIGHTS = [
  {
    icon: WindIcon,
    title: "Meanline stage stacking",
    body: "Each stage solved sequentially at the RMS radius, its outlet feeding the next inlet with mass-flow continuity enforced.",
  },
  {
    icon: GaugeIcon,
    title: "Off-design prediction",
    body: "Sweep speed lines and flow ranges with corrections for blade reset, off-design speed and flow deviation.",
  },
  {
    icon: ChartLineIcon,
    title: "Performance maps",
    body: "Pressure ratio, efficiency and per-stage diagnostics plotted across the full operating envelope in seconds.",
  },
]

export default function Home() {
  return (
    <div className="flex min-h-full flex-col">
      <AppHeader />

      <main className="flex-1">
        {/* Hero */}
        <section className="relative overflow-hidden">
          <div
            aria-hidden
            className="absolute inset-0 -z-10 opacity-[0.15] [background-image:linear-gradient(to_right,var(--border)_1px,transparent_1px),linear-gradient(to_bottom,var(--border)_1px,transparent_1px)] [background-size:44px_44px] [mask-image:radial-gradient(ellipse_at_top,black,transparent_75%)]"
          />
          <div className="mx-auto w-full max-w-7xl px-4 py-16 sm:px-6 lg:py-24">
            <div className="mx-auto max-w-2xl text-center">
              <h1 className="font-heading text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
                Axial compressor performance, from geometry to map.
              </h1>
              <p className="text-muted-foreground mt-4 text-lg text-pretty">
                {SITE.name} is a 1D meanline design tool for multistage axial
                compressors. Enter your geometry and design point, run the
                stage-stacking sweep, and read off the compressor map across the
                full range of speed and flow.
              </p>
              <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                <Button size="lg" render={<Link href="/analysis/parameters" />}>
                  Start an analysis
                  <ArrowRightIcon />
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  render={
                    <a href={SITE.repoUrl} target="_blank" rel="noreferrer" />
                  }
                >
                  <GitHubIcon className="size-4" />
                  View source
                </Button>
              </div>
            </div>

            <div className="mt-14 grid gap-4 sm:grid-cols-3">
              {HIGHLIGHTS.map(({ icon: Icon, title, body }) => (
                <Card key={title} className="bg-card/60">
                  <CardContent className="flex flex-col gap-2 p-5">
                    <span className="border-primary/25 bg-primary/10 text-primary flex size-9 items-center justify-center rounded-lg border">
                      <Icon className="size-4" />
                    </span>
                    <p className="mt-1 font-medium">{title}</p>
                    <p className="text-muted-foreground text-sm">{body}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="mt-8 border-t">
        <div className="text-muted-foreground mx-auto flex w-full max-w-7xl flex-col items-center justify-between gap-2 px-4 py-8 text-xs sm:flex-row sm:px-6">
          <p>
            © {new Date().getFullYear()} {SITE.name}
          </p>
          <a
            href={SITE.repoUrl}
            target="_blank"
            rel="noreferrer"
            className="hover:text-foreground inline-flex items-center gap-1.5 transition-colors"
          >
            <GitHubIcon className="size-3.5" />
            GitHub
          </a>
        </div>
      </footer>
    </div>
  )
}
