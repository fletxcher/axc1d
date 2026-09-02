"use client"

import * as React from "react"
import { TriangleAlertIcon } from "lucide-react"

import type { OperatingPoint } from "@/lib/analysis/types"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export function OperatingPointsTable({
  points,
  speeds,
}: {
  points: OperatingPoint[]
  speeds: number[]
}) {
  const [speed, setSpeed] = React.useState("all")
  const rows = points.filter(
    (p) => speed === "all" || Math.round(p.speedFraction * 100) === Number(speed)
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Operating points</CardTitle>
        <p className="text-muted-foreground text-sm">
          Converged overall performance for every point in the sweep
        </p>
        <CardAction>
          <Select value={speed} onValueChange={(v) => setSpeed(String(v))}>
            <SelectTrigger className="w-36">
              <SelectValue>
                {(v) =>
                  v === "all"
                    ? "All speeds"
                    : `N/N₀ ${(Number(v) / 100).toFixed(2)}`
                }
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All speeds</SelectItem>
              {speeds.map((s) => (
                <SelectItem key={s} value={String(Math.round(s * 100))}>
                  N/N₀ {s.toFixed(2)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardAction>
      </CardHeader>
      <CardContent className="p-0">
        <Separator />
        <div className="max-h-[420px] overflow-auto">
          <Table>
            <TableHeader className="bg-card sticky top-0">
              <TableRow>
                <TableHead>N/N₀</TableHead>
                <TableHead>Pt</TableHead>
                <TableHead className="text-right">Corr. flow</TableHead>
                <TableHead className="text-right">PR</TableHead>
                <TableHead className="text-right">TR</TableHead>
                <TableHead className="text-right">η</TableHead>
                <TableHead className="text-right">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody className="tabular">
              {rows.map((p, i) => (
                <TableRow key={i}>
                  <TableCell>{p.speedFraction.toFixed(2)}</TableCell>
                  <TableCell>{p.flowPointIndex + 1}</TableCell>
                  <TableCell className="text-right">
                    {p.correctedMassFlow.toFixed(2)}
                  </TableCell>
                  <TableCell className="text-right">
                    {p.stalled ? "-" : p.overallPressureRatio.toFixed(3)}
                  </TableCell>
                  <TableCell className="text-right">
                    {p.stalled ? "-" : p.overallTemperatureRatio.toFixed(3)}
                  </TableCell>
                  <TableCell className="text-right">
                    {p.stalled
                      ? "-"
                      : `${(p.overallEfficiency * 100).toFixed(1)}%`}
                  </TableCell>
                  <TableCell className="text-right">
                    {p.stalled ? (
                      <Badge variant="destructive" className="gap-1">
                        <TriangleAlertIcon />
                        stall/choke
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground text-xs">
                        converged
                      </span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
