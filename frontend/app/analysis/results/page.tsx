"use client"

import Link from "next/link"
import {
  ChartLineIcon,
  FlaskConicalIcon,
  RotateCwIcon,
  TriangleAlertIcon,
} from "lucide-react"
import { toast } from "sonner"

import { useAnalysis } from "@/lib/analysis/store"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"
import { Spinner } from "@/components/ui/spinner"
import {
  buildSpeedSeries,
  LineFamilyChart,
} from "@/components/analysis/results/charts"
import { ResultsExportDialog } from "@/components/analysis/results/export-dialog"
import { ChartCard, StatCard } from "@/components/analysis/results/result-cards"
import { StageExplorer } from "@/components/analysis/results/stage-explorer"
import { OperatingPointsTable } from "@/components/analysis/results/operating-points-table"

export default function ResultsPage() {
  const { results, hydrated, run, runStatus, config } = useAnalysis()

  if (!hydrated) {
    return (
      <div className="text-muted-foreground flex h-64 items-center justify-center gap-2 text-sm">
        <Spinner /> Loading workspace…
      </div>
    )
  }

  if (!results) {
    return (
      <Empty className="my-10 border">
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <ChartLineIcon />
          </EmptyMedia>
          <EmptyTitle>No results yet</EmptyTitle>
          <EmptyDescription>
            Complete the input steps and run the stage-stacking sweep to see the
            compressor map and per-stage diagnostics here.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <Button render={<Link href="/analysis/review" />}>
            Go to Review &amp; Run
          </Button>
        </EmptyContent>
      </Empty>
    )
  }

  const d = results.design
  const points = results.operatingPoints
  const stalledCount = points.filter((p) => p.stalled).length
  const flowUnit = config.deviationFactors.siUnits ? "kg/s" : "lbm/s"

  const prSeries = buildSpeedSeries(points, (p) => p.overallPressureRatio)
  const etaSeries = buildSpeedSeries(points, (p) => p.overallEfficiency * 100)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-heading text-xl font-semibold tracking-tight">
              Results
            </h1>
            {results.stub ? (
              <Badge variant="secondary" className="gap-1">
                <FlaskConicalIcon />
                Placeholder solver
              </Badge>
            ) : results.units ? (
              <Badge variant="secondary">{results.units} units</Badge>
            ) : null}
          </div>
          <p className="text-muted-foreground mt-0.5 text-sm">
            {points.length} operating points across {results.speeds.length} speed
            lines · {results.runtimeMs} ms ·{" "}
            {new Date(results.generatedAt).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2">
          <ResultsExportDialog results={results} />
          <Button
            size="sm"
            disabled={runStatus === "running"}
            onClick={() =>
              toast.promise(run(), {
                loading: "Re-running sweep…",
                success: "Sweep updated",
                error: (err) =>
                  err instanceof Error ? err.message : "Solver error",
              })
            }
          >
            {runStatus === "running" ? <Spinner /> : <RotateCwIcon />}
            Re-run
          </Button>
        </div>
      </div>

      {stalledCount > 0 && (
        <div className="border-destructive/30 bg-destructive/5 text-destructive flex items-center gap-2 rounded-lg border px-3 py-2 text-sm">
          <TriangleAlertIcon className="size-4 shrink-0" />
          {stalledCount} operating point{stalledCount > 1 ? "s" : ""} fell outside
          a stage stall/choke window and are omitted from the maps.
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Peak pressure ratio"
          value={d.pressureRatio.toFixed(2)}
          sub="design speed"
        />
        <StatCard
          label="Peak efficiency"
          value={`${(d.efficiency * 100).toFixed(1)}%`}
          sub="adiabatic, overall"
        />
        <StatCard
          label="Surge margin"
          value={`${d.surgeMarginPct.toFixed(0)}%`}
          sub="peak-η to surge"
        />
        <StatCard
          label="Stages"
          value={String(d.stages)}
          sub={`${results.speeds.length} speed lines`}
        />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard
          title="Compressor map"
          subtitle={`Overall pressure ratio vs corrected inlet mass flow (${flowUnit})`}
        >
          <LineFamilyChart
            series={prSeries}
            xLabel="Corrected mass flow"
            xUnit={flowUnit}
            numberFormat={(n) => n.toFixed(2)}
          />
        </ChartCard>

        <ChartCard
          title="Efficiency map"
          subtitle={`Overall adiabatic efficiency (%) vs corrected inlet mass flow (${flowUnit})`}
        >
          <LineFamilyChart
            series={etaSeries}
            xLabel="Corrected mass flow"
            xUnit={flowUnit}
            numberFormat={(n) => n.toFixed(2)}
          />
        </ChartCard>
      </div>

      <StageExplorer
        points={points}
        stages={d.stages}
        si={config.deviationFactors.siUnits}
      />

      <OperatingPointsTable points={points} speeds={results.speeds} />
    </div>
  )
}
