"use client"

import { InfoIcon } from "lucide-react"

import { useAnalysis } from "@/lib/analysis/store"
import type { OperatingParameters } from "@/lib/analysis/types"
import { StepShell } from "@/components/analysis/step-shell"
import { FieldBlock, FieldGrid, NumberInput } from "@/components/analysis/fields"
import { Card, CardContent } from "@/components/ui/card"

export default function ParametersStep() {
  const { config, updateConfig } = useAnalysis()
  const p = config.parameters
  const si = config.deviationFactors.siUnits

  function set<K extends keyof OperatingParameters>(
    key: K,
    value: OperatingParameters[K]
  ) {
    updateConfig((c) => ({
      ...c,
      parameters: { ...c.parameters, [key]: value },
    }))
  }

  return (
    <StepShell slug="parameters">
      <div className="flex flex-col gap-5">
        <Card>
          <CardContent className="p-5">
            <p className="mb-4 text-sm font-medium">Model size</p>
            <FieldGrid>
              <FieldBlock label="Stages" hint="1 to 12 stages.">
                <NumberInput value={p.stages} step={1} onCommit={(v) => set("stages", v)} />
              </FieldBlock>
              <FieldBlock label="Cases" hint="Number of cases">
                <NumberInput value={p.speeds} step={1} onCommit={(v) => set("speeds", v)} />
              </FieldBlock>
              <FieldBlock
                label="Points per curve"
                hint="Samples along each characteristic."
              >
                <NumberInput
                  value={p.pointsPerCurve}
                  step={1}
                  onCommit={(v) => set("pointsPerCurve", v)}
                />
              </FieldBlock>
            </FieldGrid>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <p className="mb-4 text-sm font-medium">Inlet conditions &amp; design point</p>
            <FieldGrid>
              <FieldBlock label="Inlet total pressure">
                <NumberInput
                  value={p.inletPressure}
                  suffix={si ? "kPa" : "psia"}
                  onCommit={(v) => set("inletPressure", v)}
                />
              </FieldBlock>
              <FieldBlock label="Inlet total temperature">
                <NumberInput
                  value={p.inletTemperature}
                  suffix={si ? "K" : "°R"}
                  onCommit={(v) => set("inletTemperature", v)}
                />
              </FieldBlock>
              <FieldBlock label="Molecular weight">
                <NumberInput
                  value={p.molecularWeight}
                  suffix="g/mol"
                  onCommit={(v) => set("molecularWeight", v)}
                />
              </FieldBlock>
              <FieldBlock label="Design speed">
                <NumberInput
                  value={p.rpm}
                  suffix="rev/min"
                  onCommit={(v) => set("rpm", v)}
                />
              </FieldBlock>
              <FieldBlock label="Design mass flow">
                <NumberInput
                  value={p.massFlow}
                  suffix={si ? "kg/s" : "lbm/s"}
                  onCommit={(v) => set("massFlow", v)}
                />
              </FieldBlock>
            </FieldGrid>
          </CardContent>
        </Card>

        <p className="text-muted-foreground flex items-start gap-2 text-xs">
          <InfoIcon className="mt-px size-3.5 shrink-0" />
          Changing stage or speed counts re-shapes the geometry, table and
          characteristic sections. Existing rows are kept; new ones use the
          reference deck defaults. The unit system is set on the next step.
        </p>
      </div>
    </StepShell>
  )
}
