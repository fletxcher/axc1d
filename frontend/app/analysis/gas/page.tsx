"use client"

import { useAnalysis } from "@/lib/analysis/store"
import type { GasCoefficients } from "@/lib/analysis/types"
import { StepShell } from "@/components/analysis/step-shell"
import { FieldBlock, FieldGrid, NumberInput } from "@/components/analysis/fields"
import { Card, CardContent } from "@/components/ui/card"

export default function GasStep() {
  const { config, updateConfig } = useAnalysis()
  const coeffs = config.gasCoefficients

  function setCoefficient(index: number, value: number) {
    updateConfig((c) => {
      const next = [...c.gasCoefficients] as GasCoefficients
      next[index] = value
      return { ...c, gasCoefficients: next }
    })
  }

  return (
    <StepShell slug="gas">
      <Card>
        <CardContent className="p-5">
          <p className="mb-1 text-sm font-medium">Specific-heat polynomial</p>
          <p className="text-muted-foreground mb-4 text-sm">
            Coefficients for specific heat as a function of temperature. The
            reference deck uses air.
          </p>
          <FieldGrid>
            {coeffs.map((value, i) => (
              <FieldBlock key={i} label={`Coefficient ${i + 1}`}>
                <NumberInput
                  value={value}
                  onCommit={(v) => setCoefficient(i, v)}
                />
              </FieldBlock>
            ))}
          </FieldGrid>
        </CardContent>
      </Card>
    </StepShell>
  )
}
