"use client"

import { InfoIcon } from "lucide-react"

import { useAnalysis } from "@/lib/analysis/store"
import { StepShell } from "@/components/analysis/step-shell"
import { NumberInput } from "@/components/analysis/fields"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const ROWS = [
  { key: "phi", label: "φ" },
  { key: "psi", label: "ψ" },
  { key: "eta", label: "η" },
] as const

export default function CharacteristicsStep() {
  const { config, updateConfig } = useAnalysis()
  const curves = config.characteristics

  function set(
    stage: number,
    point: number,
    key: "phi" | "psi" | "eta",
    value: number
  ) {
    updateConfig((c) => ({
      ...c,
      characteristics: c.characteristics.map((curve, si) =>
        si === stage
          ? {
              points: curve.points.map((pt, pi) =>
                pi === point ? { ...pt, [key]: value } : pt
              ),
            }
          : curve
      ),
    }))
  }

  return (
    <StepShell slug="characteristics">
      <div className="flex flex-col gap-4">
        <Tabs defaultValue="0">
          <TabsList variant="line" className="w-full justify-start">
            {curves.map((_, i) => (
              <TabsTrigger key={i} value={String(i)}>
                Stage {i + 1}
              </TabsTrigger>
            ))}
          </TabsList>

          {curves.map((curve, stageIndex) => (
            <TabsContent key={stageIndex} value={String(stageIndex)}>
              <Card>
                <CardContent className="p-0">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="bg-muted/40 w-24">Point</TableHead>
                        {curve.points.map((_, k) => (
                          <TableHead key={k} className="w-24 text-center tabular">
                            {k + 1}
                          </TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {ROWS.map((r) => (
                        <TableRow key={r.key}>
                          <TableCell className="bg-muted/40 align-middle font-medium">
                            {r.label}
                          </TableCell>
                          {curve.points.map((pt, k) => (
                            <TableCell key={k} className="p-1.5">
                              <NumberInput
                                className="h-7 px-1.5 text-center"
                                value={pt[r.key]}
                                onCommit={(v) => set(stageIndex, k, r.key, v)}
                              />
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>
          ))}
        </Tabs>

        <p className="text-muted-foreground flex items-start gap-2 text-xs">
          <InfoIcon className="mt-px size-3.5 shrink-0" />
          These points define the design-speed characteristic for each stage. φ
          must strictly increase left to right. Leave ψ and η at 0 to have the
          solver build them from a two-parabola fit around the design point.
        </p>
      </div>
    </StepShell>
  )
}
