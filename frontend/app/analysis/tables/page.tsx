"use client"

import { useAnalysis } from "@/lib/analysis/store"
import { StepShell } from "@/components/analysis/step-shell"
import { NumberInput } from "@/components/analysis/fields"
import { Card, CardContent } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export default function TablesStep() {
  const { config, updateConfig } = useAnalysis()
  const { efficiencyRatioTable, bleedTable, parameters } = config
  const flowUnit = config.deviationFactors.siUnits ? "kg/s" : "lbm/s"

  function setEff(row: number, key: "speedFraction" | "efficiencyRatio", v: number) {
    updateConfig((c) => ({
      ...c,
      efficiencyRatioTable: c.efficiencyRatioTable.map((r, i) =>
        i === row ? { ...r, [key]: v } : r
      ),
    }))
  }

  function setBleedSpeed(row: number, v: number) {
    updateConfig((c) => ({
      ...c,
      bleedTable: c.bleedTable.map((r, i) =>
        i === row ? { ...r, speedFraction: v } : r
      ),
    }))
  }

  function setBleedCell(row: number, stage: number, v: number) {
    updateConfig((c) => ({
      ...c,
      bleedTable: c.bleedTable.map((r, i) =>
        i === row
          ? {
              ...r,
              stageBleed: r.stageBleed.map((b, s) => (s === stage ? v : b)),
            }
          : r
      ),
    }))
  }

  return (
    <StepShell slug="tables">
      <div className="flex flex-col gap-6">
        <section>
          <p className="text-sm font-medium">Efficiency ratio table</p>
          <p className="text-muted-foreground mb-3 text-sm">
            Multiplier applied to stage efficiency at each speed line (ETARAT).
          </p>
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-40">Speed fraction</TableHead>
                    <TableHead className="w-40">Efficiency ratio</TableHead>
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {efficiencyRatioTable.map((row, i) => (
                    <TableRow key={i}>
                      <TableCell>
                        <NumberInput
                          className="h-7"
                          value={row.speedFraction}
                          onCommit={(v) => setEff(i, "speedFraction", v)}
                        />
                      </TableCell>
                      <TableCell>
                        <NumberInput
                          className="h-7"
                          value={row.efficiencyRatio}
                          onCommit={(v) => setEff(i, "efficiencyRatio", v)}
                        />
                      </TableCell>
                      <TableCell className="text-muted-foreground text-xs">
                        {i === 0 ? "design" : `${Math.round(row.speedFraction * 100)}% N`}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </section>

        <section>
          <p className="text-sm font-medium">Inter-stage bleed</p>
          <p className="text-muted-foreground mb-3 text-sm">
            Flow extracted downstream of each stage ({flowUnit}), per speed line.
          </p>
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-32">Speed</TableHead>
                    {Array.from({ length: parameters.stages }, (_, s) => (
                      <TableHead key={s} className="w-28">
                        Stage {s + 1}
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {bleedTable.map((row, i) => (
                    <TableRow key={i}>
                      <TableCell>
                        <NumberInput
                          className="h-7"
                          value={row.speedFraction}
                          onCommit={(v) => setBleedSpeed(i, v)}
                        />
                      </TableCell>
                      {row.stageBleed.map((b, s) => (
                        <TableCell key={s}>
                          <NumberInput
                            className="h-7"
                            value={b}
                            onCommit={(v) => setBleedCell(i, s, v)}
                          />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </section>

        <p className="text-muted-foreground text-xs">
          Row counts follow the speed-line count from Operating Parameters.
        </p>
      </div>
    </StepShell>
  )
}
