"use client"

import * as React from "react"

import { useAnalysis } from "@/lib/analysis/store"
import type { StageGeometry } from "@/lib/analysis/types"
import { StepShell } from "@/components/analysis/step-shell"
import { FieldBlock, FieldGrid, NumberInput } from "@/components/analysis/fields"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

const FIELDS: {
  key: keyof StageGeometry
  label: string
  suffix?: string
  group: "radii" | "angles" | "solidity"
}[] = [
  { key: "rotorInletTip", label: "Rotor inlet tip radius", group: "radii" },
  { key: "rotorInletHub", label: "Rotor inlet hub radius", group: "radii" },
  { key: "rotorOutletTip", label: "Rotor outlet tip radius", group: "radii" },
  { key: "rotorOutletHub", label: "Rotor outlet hub radius", group: "radii" },
  { key: "inletFlowAngle", label: "Inlet absolute flow angle", suffix: "deg", group: "angles" },
  { key: "bladeResetAbs", label: "Δ inlet absolute angle", suffix: "deg", group: "angles" },
  { key: "bladeResetRel", label: "Δ inlet relative angle", suffix: "deg", group: "angles" },
  { key: "bladeResetOutlet", label: "Δ outlet relative angle", suffix: "deg", group: "angles" },
  { key: "rotorMetalAngle", label: "Rotor inlet metal angle", suffix: "deg", group: "angles" },
  { key: "statorMetalAngle", label: "Stator inlet metal angle", suffix: "deg", group: "angles" },
  { key: "rotorSolidity", label: "Rotor solidity at meanline", group: "solidity" },
]

export default function GeometryStep() {
  const { config, updateConfig } = useAnalysis()
  const stages = config.stageGeometry

  function set(stageIndex: number, key: keyof StageGeometry, value: number) {
    updateConfig((c) => ({
      ...c,
      stageGeometry: c.stageGeometry.map((g, i) =>
        i === stageIndex ? { ...g, [key]: value } : g
      ),
    }))
  }

  const lengthUnit = config.deviationFactors.siUnits ? "cm" : "in"

  return (
    <StepShell slug="geometry">
      <Accordion
        multiple
        defaultValue={[0]}
        keepMounted
        className="overflow-hidden rounded-xl border"
      >
        {stages.map((stage, index) => {
          return (
            <AccordionItem
              key={index}
              value={index}
              className="not-last:border-b px-4"
            >
              <AccordionTrigger className="py-3.5">
                <span className="font-medium">Stage {index + 1}</span>
              </AccordionTrigger>
              <AccordionContent className="pb-4">
                <div className="flex flex-col gap-5">
                  <Group title="Annulus radii" unit={lengthUnit}>
                    <FieldGrid className="lg:grid-cols-4">
                      {FIELDS.filter((f) => f.group === "radii").map((f) => (
                        <FieldBlock key={f.key} label={f.label}>
                          <NumberInput
                            value={stage[f.key]}
                            suffix={lengthUnit}
                            onCommit={(v) => set(index, f.key, v)}
                          />
                        </FieldBlock>
                      ))}
                    </FieldGrid>
                  </Group>

                  <Group title="Blade angles">
                    <FieldGrid>
                      {FIELDS.filter((f) => f.group === "angles").map((f) => (
                        <FieldBlock key={f.key} label={f.label}>
                          <NumberInput
                            value={stage[f.key]}
                            suffix={f.suffix}
                            onCommit={(v) => set(index, f.key, v)}
                          />
                        </FieldBlock>
                      ))}
                    </FieldGrid>
                  </Group>

                  <Group title="Solidity">
                    <FieldGrid>
                      {FIELDS.filter((f) => f.group === "solidity").map((f) => (
                        <FieldBlock key={f.key} label={f.label}>
                          <NumberInput
                            value={stage[f.key]}
                            onCommit={(v) => set(index, f.key, v)}
                          />
                        </FieldBlock>
                      ))}
                    </FieldGrid>
                  </Group>
                </div>
              </AccordionContent>
            </AccordionItem>
          )
        })}
      </Accordion>
    </StepShell>
  )
}

function Group({
  title,
  unit,
  children,
}: {
  title: string
  unit?: string
  children: React.ReactNode
}) {
  return (
    <div>
      <p className="text-muted-foreground mb-3 text-xs font-medium tracking-wide uppercase">
        {title}
        {unit ? ` · ${unit}` : ""}
      </p>
      {children}
    </div>
  )
}
