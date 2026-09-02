"use client"

import * as React from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import {
  ArrowLeftIcon,
  CheckIcon,
  PlayIcon,
  TriangleAlertIcon,
} from "lucide-react"
import { toast } from "sonner"

import { useAnalysis } from "@/lib/analysis/store"
import { STEPS } from "@/lib/analysis/steps"
import { StepShell } from "@/components/analysis/step-shell"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"

export default function ReviewStep() {
  const router = useRouter()
  const { config, stepIssues, firstInvalidSlug, run, runStatus } = useAnalysis()
  const running = runStatus === "running"

  const p = config.parameters
  const d = config.deviationFactors

  async function handleRun() {
    if (firstInvalidSlug) {
      router.push(`/analysis/${firstInvalidSlug}`)
      return
    }
    toast.promise(run().then(() => router.push("/analysis/results")), {
      loading: "Running stage-stacking sweep…",
      success: "Sweep complete",
      error: (err) => (err instanceof Error ? err.message : "The solver returned an error"),
    })
  }

  const facts: [string, string][] = [
    ["Stages", String(p.stages)],
    ["Speed lines", String(p.speeds)],
    ["Points / curve", String(p.pointsPerCurve)],
    ["Units", d.siUnits ? "SI" : "US customary"],
    ["Design speed", `${p.rpm.toLocaleString()} rev/min`],
    ["Design mass flow", `${p.massFlow} ${d.siUnits ? "kg/s" : "lbm/s"}`],
    ["Inlet total pressure", `${p.inletPressure} ${d.siUnits ? "kPa" : "psia"}`],
    ["Inlet total temperature", `${p.inletTemperature} ${d.siUnits ? "K" : "°R"}`],
  ]

  return (
    <StepShell
      slug="review"
      footer={
        <div className="flex flex-col gap-3 border-t pt-4 sm:flex-row sm:items-center sm:justify-between">
          <Button
            variant="outline"
            render={<Link href="/analysis/characteristics" />}
          >
            <ArrowLeftIcon />
            Design Characteristics
          </Button>
          <Button size="lg" onClick={handleRun} disabled={running}>
            {running ? <Spinner /> : <PlayIcon />}
            {firstInvalidSlug ? "Fix inputs to run" : "Run analysis"}
          </Button>
        </div>
      }
    >
      <div className="flex flex-col gap-5">
        <Card>
          <CardContent className="p-5">
            <p className="mb-4 text-sm font-medium">Deck summary</p>
            <dl className="grid gap-x-6 gap-y-3 sm:grid-cols-2">
              {facts.map(([k, v]) => (
                <div key={k} className="flex items-baseline justify-between gap-3 border-b pb-2 text-sm last:border-0 sm:last:border-b">
                  <dt className="text-muted-foreground">{k}</dt>
                  <dd className="text-right font-medium tabular">{v}</dd>
                </div>
              ))}
            </dl>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-2">
            <ul className="divide-y">
              {STEPS.filter((s) => s.slug !== "review").map((step) => {
                const issue = stepIssues[step.slug]
                return (
                  <li key={step.id}>
                    <Link
                      href={`/analysis/${step.slug}`}
                      className="hover:bg-muted/50 flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm"
                    >
                      <span
                        className={
                          issue
                            ? "text-destructive bg-destructive/10 flex size-6 items-center justify-center rounded-md"
                            : "text-primary bg-primary/10 flex size-6 items-center justify-center rounded-md"
                        }
                      >
                        {issue ? (
                          <TriangleAlertIcon className="size-3.5" />
                        ) : (
                          <CheckIcon className="size-3.5" />
                        )}
                      </span>
                      <span className="flex-1 font-medium">{step.title}</span>
                      <span
                        className={
                          issue
                            ? "text-destructive text-xs"
                            : "text-muted-foreground text-xs"
                        }
                      >
                        {issue ?? "Ready"}
                      </span>
                    </Link>
                  </li>
                )
              })}
            </ul>
          </CardContent>
        </Card>
      </div>
    </StepShell>
  )
}
