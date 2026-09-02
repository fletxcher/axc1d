import {
  ClipboardCheck,
  FlaskConical,
  Layers3,
  Sigma,
  SlidersHorizontal,
  Spline,
  Table2,
  type LucideIcon,
} from "lucide-react"

import type { AnalysisConfig } from "./types"

export interface StepDef {
  id: string
  /** Route segment under /analysis. */
  slug: string
  title: string
  /** One-line summary shown in the stepper and step header. */
  summary: string
  icon: LucideIcon
  /** Returns null when valid, or a short reason why the step is incomplete. */
  validate: (config: AnalysisConfig) => string | null
}

const finite = (n: number) => Number.isFinite(n)

export const STEPS: StepDef[] = [
  {
    id: "parameters",
    slug: "parameters",
    title: "Operating Parameters",
    summary: "Stage count, speed lines, inlet conditions and design point.",
    icon: SlidersHorizontal,
    validate: (c) => {
      const p = c.parameters
      if (p.stages < 1) return "At least one stage is required."
      if (p.speeds < 1) return "At least one speed line is required."
      if (!finite(p.inletPressure) || p.inletPressure <= 0)
        return "Inlet pressure must be positive."
      if (!finite(p.inletTemperature) || p.inletTemperature <= 0)
        return "Inlet temperature must be positive."
      if (!finite(p.rpm) || p.rpm <= 0) return "Design speed must be positive."
      if (!finite(p.massFlow) || p.massFlow <= 0)
        return "Design mass flow must be positive."
      return null
    },
  },
  {
    id: "deviation",
    slug: "deviation",
    title: "Deviation Factors",
    summary: "Off-design correction flags and the unit system.",
    icon: Sigma,
    validate: () => null,
  },
  {
    id: "gas",
    slug: "gas",
    title: "Gas Properties",
    summary: "Specific-heat polynomial coefficients.",
    icon: FlaskConical,
    validate: (c) =>
      c.gasCoefficients.every(finite)
        ? null
        : "Every Cp coefficient must be a number.",
  },
  {
    id: "geometry",
    slug: "geometry",
    title: "Stage Geometry",
    summary: "Meanline radii, blade angles and solidity for each stage.",
    icon: Layers3,
    validate: (c) => {
      for (const [i, g] of c.stageGeometry.entries()) {
        if (g.rotorInletTip <= g.rotorInletHub)
          return `Stage ${i + 1}: inlet tip radius must exceed hub radius.`
        if (g.rotorOutletTip <= g.rotorOutletHub)
          return `Stage ${i + 1}: outlet tip radius must exceed hub radius.`
        if (g.rotorSolidity <= 0)
          return `Stage ${i + 1}: solidity must be positive.`
      }
      return null
    },
  },
  {
    id: "tables",
    slug: "tables",
    title: "Speed Tables",
    summary: "Efficiency ratio and inter-stage bleed against speed.",
    icon: Table2,
    validate: (c) =>
      c.efficiencyRatioTable.every(
        (r) => finite(r.speedFraction) && finite(r.efficiencyRatio)
      )
        ? null
        : "Efficiency ratio table has an empty cell.",
  },
  {
    id: "characteristics",
    slug: "characteristics",
    title: "Design Characteristics",
    summary: "φ, ψ and η points defining each stage curve at design speed.",
    icon: Spline,
    validate: (c) => {
      for (const [i, curve] of c.characteristics.entries()) {
        if (curve.points.some((pt) => !finite(pt.phi)))
          return `Stage ${i + 1}: every φ value must be a number.`
        const phis = curve.points.map((pt) => pt.phi)
        if (phis.some((v, k) => k > 0 && v <= phis[k - 1]))
          return `Stage ${i + 1}: φ values must strictly increase.`
      }
      return null
    },
  },
  {
    id: "review",
    slug: "review",
    title: "Review & Run",
    summary: "Confirm the deck and launch the stage-stacking sweep.",
    icon: ClipboardCheck,
    validate: () => null,
  },
]

export const FIRST_STEP_SLUG = STEPS[0].slug
export const RESULTS_SLUG = "results"

export function stepIndex(slug: string): number {
  return STEPS.findIndex((s) => s.slug === slug)
}

export function stepBySlug(slug: string): StepDef | undefined {
  return STEPS.find((s) => s.slug === slug)
}
