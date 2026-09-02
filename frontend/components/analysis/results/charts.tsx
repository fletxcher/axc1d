"use client"

import * as React from "react"
import {
  CartesianGrid,
  Line,
  LineChart,
  XAxis,
  YAxis,
} from "recharts"

import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import type { OperatingPoint } from "@/lib/analysis/types"

/** Fixed categorical hue order; never cycled beyond slot 8. */
const HUES = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
  "var(--chart-6)",
  "var(--chart-7)",
  "var(--chart-8)",
]

export interface Series {
  key: string
  label: string
  points: { x: number; y: number }[]
}

export function buildSpeedSeries(
  operatingPoints: OperatingPoint[],
  yOf: (p: OperatingPoint) => number,
  xOf: (p: OperatingPoint) => number = (p) => p.correctedMassFlow
): Series[] {
  const bySpeed = new Map<number, { x: number; y: number }[]>()
  for (const p of operatingPoints) {
    if (p.stalled) continue
    const y = yOf(p)
    if (!Number.isFinite(y) || y <= 0) continue
    const list = bySpeed.get(p.speedFraction) ?? []
    list.push({ x: xOf(p), y })
    bySpeed.set(p.speedFraction, list)
  }
  return [...bySpeed.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([speed, points]) => ({
      key: `n${Math.round(speed * 100)}`,
      label: `N/N₀ ${speed.toFixed(2)}`,
      points: points.sort((a, b) => a.x - b.x),
    }))
}

/** Per-speed series for one stage, plotting two stage-level fields against each other. */
type StageNumericKey =
  | "phi"
  | "psi"
  | "eta"
  | "pressureRatio"
  | "temperatureRatio"
  | "massFlow"
  | "inletTotalPressure"
  | "outletTotalPressure"
  | "inletTotalTemperature"
  | "outletTotalTemperature"
  | "diffusionFactor"
  | "incidence"

export function buildStageSeries(
  operatingPoints: OperatingPoint[],
  stageNumber: number,
  xKey: StageNumericKey,
  yKey: StageNumericKey
): Series[] {
  const bySpeed = new Map<number, { x: number; y: number }[]>()
  for (const p of operatingPoints) {
    if (p.stalled) continue
    const stage = p.stages.find((s) => s.stage === stageNumber)
    if (!stage) continue
    const list = bySpeed.get(p.speedFraction) ?? []
    list.push({ x: stage[xKey], y: stage[yKey] })
    bySpeed.set(p.speedFraction, list)
  }
  return [...bySpeed.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([speed, points]) => ({
      key: `n${Math.round(speed * 100)}`,
      label: `N/N₀ ${speed.toFixed(2)}`,
      points: points.sort((a, b) => a.x - b.x),
    }))
}

export function LineFamilyChart({
  series,
  xLabel,
  xUnit,
  numberFormat = (n: number) => n.toFixed(2),
  className,
}: {
  series: Series[]
  /** Name of the x quantity, shown in the hover tooltip. */
  xLabel: string
  xUnit?: string
  numberFormat?: (n: number) => string
  className?: string
}) {
  const config: ChartConfig = React.useMemo(() => {
    const c: ChartConfig = {}
    series.forEach((s, i) => {
      c[s.key] = { label: s.label, color: HUES[Math.min(i, HUES.length - 1)] }
    })
    return c
  }, [series])

  return (
    <ChartContainer
      config={config}
      className={className ?? "aspect-[16/10] w-full"}
    >
      {/* Axis titles live in the card heading / caption, so the axes carry
          tick numbers only - no rotated labels colliding with them. */}
      <LineChart margin={{ top: 8, right: 16, bottom: 4, left: 8 }}>
        <CartesianGrid vertical={false} strokeDasharray="3 3" />
        <XAxis
          type="number"
          dataKey="x"
          domain={["dataMin", "dataMax"]}
          tickLine={false}
          axisLine={false}
          tickMargin={10}
          minTickGap={32}
          tickFormatter={(v) => numberFormat(Number(v))}
        />
        <YAxis
          type="number"
          dataKey="y"
          domain={["auto", "auto"]}
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          width={64}
          tickCount={5}
          tickFormatter={(v) => numberFormat(Number(v))}
        />
        <ChartTooltip
          content={
            <ChartTooltipContent
              labelFormatter={(_, payload) => {
                const x = payload?.[0]?.payload?.x
                return x != null
                  ? `${xLabel}: ${numberFormat(Number(x))}${xUnit ? ` ${xUnit}` : ""}`
                  : ""
              }}
            />
          }
        />
        {series.map((s, i) => (
          <Line
            key={s.key}
            data={s.points}
            dataKey="y"
            name={s.key}
            type="monotone"
            stroke={HUES[Math.min(i, HUES.length - 1)]}
            strokeWidth={2}
            dot={{ r: 2.5, strokeWidth: 0 }}
            activeDot={{ r: 4 }}
            isAnimationActive={false}
          />
        ))}
      </LineChart>
    </ChartContainer>
  )
}
