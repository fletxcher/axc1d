"use client"

import * as React from "react"

import type { OperatingPoint } from "@/lib/analysis/types"
import {
  Card,
  CardAction,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  buildStageSeries,
  LineFamilyChart,
} from "@/components/analysis/results/charts"

export function StageExplorer({
  points,
  stages,
  si,
}: {
  points: OperatingPoint[]
  stages: number
  si: boolean
}) {
  const [stage, setStage] = React.useState("1")
  const stageNumber = Number(stage)

  // Absolute outlet total pressure / temperature: these carry the accumulated
  // inter-stage state, so each stage sits at its own level in the stack even
  // when the geometry is identical. (The nondimensional ψ(φ)/η(φ) map is a
  // property of the geometry alone, so shared-geometry stages overlay there.)
  const poutSeries = buildStageSeries(
    points,
    stageNumber,
    "phi",
    "outletTotalPressure"
  )
  const toutSeries = buildStageSeries(
    points,
    stageNumber,
    "phi",
    "outletTotalTemperature"
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Stage explorer</CardTitle>
        <p className="text-muted-foreground text-sm">
          Outlet total pressure and temperature for one stage, across every case
        </p>
        <CardAction>
          <Select value={stage} onValueChange={(v) => setStage(String(v))}>
            <SelectTrigger className="w-32">
              <SelectValue>{(v) => `Stage ${v}`}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {Array.from({ length: stages }, (_, i) => (
                <SelectItem key={i} value={String(i + 1)}>
                  Stage {i + 1}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent className="grid gap-4 lg:grid-cols-2">
        <div>
          <p className="text-muted-foreground mb-1 text-xs font-medium">
            Outlet total pressure ({si ? "kPa" : "psia"}) vs φ
          </p>
          <LineFamilyChart
            series={poutSeries}
            xLabel="φ"
            numberFormat={(n) => n.toFixed(2)}
            className="aspect-[16/11] w-full"
          />
        </div>
        <div>
          <p className="text-muted-foreground mb-1 text-xs font-medium">
            Outlet total temperature ({si ? "K" : "°R"}) vs φ
          </p>
          <LineFamilyChart
            series={toutSeries}
            xLabel="φ"
            numberFormat={(n) => n.toFixed(1)}
            className="aspect-[16/11] w-full"
          />
        </div>
      </CardContent>
    </Card>
  )
}
