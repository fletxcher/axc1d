import type {
  AnalysisConfig,
  BleedRow,
  CharacteristicPoint,
  EfficiencyRatioRow,
  StageCharacteristic,
  StageGeometry,
} from "./types"

/** Speed lines used by the desktop tool's default deck. */
export const DEFAULT_SPEED_FRACTIONS = [1.0, 0.9, 0.8, 0.7, 0.5]

const DEFAULT_EFFICIENCY_RATIOS = [1.0, 1.017, 1.029, 1.017, 1.023]

const STAGE_GEOMETRY_DEFAULTS: StageGeometry[] = [
  {
    rotorInletTip: 25.42,
    rotorInletHub: 9.891,
    rotorOutletTip: 24.628,
    rotorOutletHub: 12.088,
    inletFlowAngle: 0,
    bladeResetAbs: 0,
    bladeResetRel: 0,
    bladeResetOutlet: 0,
    rotorMetalAngle: 56.15,
    rotorSolidity: 1.68,
    statorMetalAngle: 36.1,
  },
  {
    rotorInletTip: 23.96,
    rotorInletHub: 13.604,
    rotorOutletTip: 23.566,
    rotorOutletHub: 14.696,
    inletFlowAngle: 0,
    bladeResetAbs: 0,
    bladeResetRel: 0,
    bladeResetOutlet: 0,
    rotorMetalAngle: 55.46,
    rotorSolidity: 1.57,
    statorMetalAngle: 36.15,
  },
]

const STAGE_PHI_DEFAULTS: number[][] = [
  [0.31, 0.35, 0.38, 0.42, 0.43, 0.44, 0.45, 0.46],
  [0.4, 0.42, 0.44, 0.45, 0.46, 0.48, 0.51, 0.53],
]

export function makeGeometry(index: number): StageGeometry {
  return (
    STAGE_GEOMETRY_DEFAULTS[index] ?? {
      ...STAGE_GEOMETRY_DEFAULTS[STAGE_GEOMETRY_DEFAULTS.length - 1],
    }
  )
}

export function makeCharacteristic(
  stageIndex: number,
  pointsPerCurve: number
): StageCharacteristic {
  const phiRow =
    STAGE_PHI_DEFAULTS[stageIndex] ??
    STAGE_PHI_DEFAULTS[STAGE_PHI_DEFAULTS.length - 1]
  const points: CharacteristicPoint[] = []
  for (let k = 0; k < pointsPerCurve; k += 1) {
    const phi =
      phiRow[k] ??
      // extrapolate linearly past the tabulated points
      +(phiRow[phiRow.length - 1] + 0.02 * (k - phiRow.length + 1)).toFixed(4)
    points.push({ phi, psi: 0, eta: 0 })
  }
  return { points }
}

export function makeEfficiencyRow(index: number): EfficiencyRatioRow {
  return {
    speedFraction: DEFAULT_SPEED_FRACTIONS[index] ?? 0.4,
    efficiencyRatio: DEFAULT_EFFICIENCY_RATIOS[index] ?? 1.02,
  }
}

export function makeBleedRow(index: number, stages: number): BleedRow {
  return {
    speedFraction: DEFAULT_SPEED_FRACTIONS[index] ?? 0.4,
    stageBleed: Array.from({ length: stages }, () => 0),
  }
}

export function defaultConfig(): AnalysisConfig {
  const stages = 2
  const speeds = 5
  const pointsPerCurve = 8
  return {
    parameters: {
      stages,
      speeds,
      inletPressure: 10.135,
      inletTemperature: 288.17,
      pointsPerCurve,
      molecularWeight: 28.97,
      rpm: 16042.797,
      massFlow: 33.248,
    },
    deviationFactors: {
      speedPsi: true,
      speedPhi: true,
      deviationBladeReset: true,
      deviationSpeed: true,
      deviationFlow: true,
      siUnits: true,
    },
    gasCoefficients: [
      0.23747, 0.21962e-4, -0.87791e-7, 0.13991e-9, -0.78056e-13, 0.15043e-16,
    ],
    stageGeometry: Array.from({ length: stages }, (_, i) => makeGeometry(i)),
    efficiencyRatioTable: Array.from({ length: speeds }, (_, i) =>
      makeEfficiencyRow(i)
    ),
    bleedTable: Array.from({ length: speeds }, (_, i) => makeBleedRow(i, stages)),
    characteristics: Array.from({ length: stages }, (_, i) =>
      makeCharacteristic(i, pointsPerCurve)
    ),
  }
}

/**
 * Re-shapes array-valued sections so their lengths match
 * `parameters.{stages,speeds,pointsPerCurve}`. Existing rows are preserved;
 * new rows fall back to sensible defaults.
 */
export function normalizeConfig(config: AnalysisConfig): AnalysisConfig {
  const stages = clampInt(config.parameters.stages, 1, 12)
  const speeds = clampInt(config.parameters.speeds, 1, 12)
  const pointsPerCurve = clampInt(config.parameters.pointsPerCurve, 2, 24)

  const stageGeometry = resize(config.stageGeometry, stages, (i) =>
    makeGeometry(i)
  )

  const efficiencyRatioTable = resize(
    config.efficiencyRatioTable,
    speeds,
    (i) => makeEfficiencyRow(i)
  )

  const bleedTable = resize(config.bleedTable, speeds, (i) =>
    makeBleedRow(i, stages)
  ).map((row) => ({
    ...row,
    stageBleed: resize(row.stageBleed, stages, () => 0),
  }))

  const characteristics = resize(config.characteristics, stages, (i) =>
    makeCharacteristic(i, pointsPerCurve)
  ).map((curve, stageIndex) => ({
    points: resize(
      curve.points,
      pointsPerCurve,
      (k) => makeCharacteristic(stageIndex, pointsPerCurve).points[k]
    ),
  }))

  return {
    ...config,
    parameters: { ...config.parameters, stages, speeds, pointsPerCurve },
    stageGeometry,
    efficiencyRatioTable,
    bleedTable,
    characteristics,
  }
}

function resize<T>(arr: T[], length: number, fill: (index: number) => T): T[] {
  const next = arr.slice(0, length)
  for (let i = next.length; i < length; i += 1) next.push(fill(i))
  return next
}

function clampInt(value: number, min: number, max: number): number {
  if (!Number.isFinite(value)) return min
  return Math.min(max, Math.max(min, Math.round(value)))
}
