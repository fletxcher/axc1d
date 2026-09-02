"use client"

import { useAnalysis } from "@/lib/analysis/store"
import type { DeviationFactors } from "@/lib/analysis/types"
import { StepShell } from "@/components/analysis/step-shell"
import { Card, CardContent } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"

interface FlagDef {
  key: keyof DeviationFactors
  title: string
  body: string
}

const CORRECTION_FLAGS: FlagDef[] = [
  {
    key: "speedPsi",
    title: "Off-design speed ψ correction",
    body: "Shift the pressure-coefficient characteristic for rotative speeds away from design.",
  },
  {
    key: "speedPhi",
    title: "Off-design speed φ correction",
    body: "Scale the flow-coefficient axis with speed fraction.",
  },
  {
    key: "deviationBladeReset",
    title: "Deviation angle · blade reset",
    body: "Adjust the rotor deviation angle when stagger is reset from design.",
  },
  {
    key: "deviationSpeed",
    title: "Deviation angle · off-design speed",
    body: "Adjust the rotor deviation angle for off-design rotative speed.",
  },
  {
    key: "deviationFlow",
    title: "Deviation angle · off-design φ",
    body: "Adjust the rotor deviation angle for off-design flow coefficient.",
  },
]

export default function DeviationStep() {
  const { config, updateConfig } = useAnalysis()
  const d = config.deviationFactors

  function set(key: keyof DeviationFactors, value: boolean) {
    updateConfig((c) => ({
      ...c,
      deviationFactors: { ...c.deviationFactors, [key]: value },
    }))
  }

  return (
    <StepShell slug="deviation">
      <div className="flex flex-col gap-5">
        <Card>
          <CardContent className="divide-y p-0">
            {CORRECTION_FLAGS.map((flag) => (
              <label
                key={flag.key}
                className="hover:bg-muted/40 flex cursor-pointer items-start justify-between gap-4 px-5 py-4 transition-colors"
              >
                <span className="min-w-0">
                  <span className="block text-sm font-medium">{flag.title}</span>
                  <span className="text-muted-foreground mt-0.5 block text-sm">
                    {flag.body}
                  </span>
                </span>
                <Switch
                  checked={d[flag.key]}
                  onCheckedChange={(v) => set(flag.key, Boolean(v))}
                />
              </label>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-0">
            <label className="hover:bg-muted/40 flex cursor-pointer items-start justify-between gap-4 px-5 py-4 transition-colors">
              <span className="min-w-0">
                <span className="block text-sm font-medium">SI units</span>
                <span className="text-muted-foreground mt-0.5 block text-sm">
                  On: kPa, K, cm, kg/s. Off: psia, °R, in, lbm/s.
                </span>
              </span>
              <Switch
                checked={d.siUnits}
                onCheckedChange={(v) => set("siUnits", Boolean(v))}
              />
            </label>
          </CardContent>
        </Card>

        <p className="text-muted-foreground text-xs">
          Leaving every flag on reproduces the reference deck.
        </p>
        <Separator className="opacity-0" />
      </div>
    </StepShell>
  )
}
