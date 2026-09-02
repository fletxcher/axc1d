// Domain model for an AXC1D analysis run.
// Mirrors the input sections of the desktop tool (src/python/editor.py) and the
// solver contract (src/python/solver.py).

export interface OperatingParameters {
  /** Number of compressor stages (NSTA). */
  stages: number
  /** Number of speed lines (NSPE). */
  speeds: number
  /** Inlet total pressure P0 (kPa in SI mode, psia otherwise). */
  inletPressure: number
  /** Inlet total temperature T0 (K in SI mode, °R otherwise). */
  inletTemperature: number
  /** Points per characteristic curve (NPTS). */
  pointsPerCurve: number
  /** Working-fluid molecular weight (g/mol). */
  molecularWeight: number
  /** Design rotational speed (rev/min). */
  rpm: number
  /** Design mass flow rate (kg/s in SI mode, lbm/s otherwise). */
  massFlow: number
}

export interface DeviationFactors {
  /** SPDPSI: adjust ψ for off-design rotative speed. */
  speedPsi: boolean
  /** SPDPHI: adjust φ for off-design rotative speed. */
  speedPhi: boolean
  /** DRDEVG: adjust rotor deviation angle for blade reset. */
  deviationBladeReset: boolean
  /** DRDEVN: adjust rotor deviation angle for off-design speed. */
  deviationSpeed: boolean
  /** DRDEVP: adjust rotor deviation angle for off-design φ. */
  deviationFlow: boolean
  /** UNITS: interpret inputs as SI. */
  siUnits: boolean
}

/** Fifth-degree polynomial coefficients for Cp(T), CPCO(1..6). */
export type GasCoefficients = [number, number, number, number, number, number]

export interface StageGeometry {
  /** Rotor inlet tip radius (RT2). */
  rotorInletTip: number
  /** Rotor inlet hub radius (RH2). */
  rotorInletHub: number
  /** Rotor outlet tip radius (RT3). */
  rotorOutletTip: number
  /** Rotor outlet hub radius (RH3). */
  rotorOutletHub: number
  /** Rotor inlet absolute flow angle at design, deg (BET2M). */
  inletFlowAngle: number
  /** Change in rotor inlet absolute flow angle, deg (CB2M). */
  bladeResetAbs: number
  /** Change in rotor inlet relative flow angle, deg (CB2MR). */
  bladeResetRel: number
  /** Change in rotor outlet relative flow angle, deg (CB3MR). */
  bladeResetOutlet: number
  /** Rotor inlet blade metal angle, deg (RK2M). */
  rotorMetalAngle: number
  /** Rotor blade row solidity at meanline (RSOLM). */
  rotorSolidity: number
  /** Stator inlet blade metal angle, deg (SK2M). */
  statorMetalAngle: number
}

export interface EfficiencyRatioRow {
  /** Fraction of design speed (PCTSPD). */
  speedFraction: number
  /** Efficiency ratio applied at that speed (ETARAT). */
  efficiencyRatio: number
}

export interface BleedRow {
  /** Fraction of design speed (PCTSPD). */
  speedFraction: number
  /** Bleed flow extracted after each stage; length === stages. */
  stageBleed: number[]
}

export interface CharacteristicPoint {
  /** Flow coefficient φ (PHIDES). */
  phi: number
  /** Work / pressure coefficient ψ (PSIDES). 0 ⇒ solver generates it. */
  psi: number
  /** Adiabatic efficiency η (ETADES). 0 ⇒ solver generates it. */
  eta: number
}

export interface StageCharacteristic {
  /** Design-speed characteristic points; length === pointsPerCurve. */
  points: CharacteristicPoint[]
}

export interface AnalysisConfig {
  parameters: OperatingParameters
  deviationFactors: DeviationFactors
  gasCoefficients: GasCoefficients
  stageGeometry: StageGeometry[]
  efficiencyRatioTable: EfficiencyRatioRow[]
  bleedTable: BleedRow[]
  characteristics: StageCharacteristic[]
}

// ---------------------------------------------------------------------------
// Solver output contract  (matches web/backend/models.py)
// ---------------------------------------------------------------------------

export interface StageResult {
  stage: number
  massFlow: number
  phi: number
  psi: number
  eta: number
  pressureRatio: number
  temperatureRatio: number
  inletTotalTemperature: number
  outletTotalTemperature: number
  inletTotalPressure: number
  outletTotalPressure: number
  axialVelocityInlet: number
  axialVelocityOutlet: number
  bladeSpeedInlet: number
  bladeSpeedOutlet: number
  swirlVelocityInlet: number
  swirlVelocityOutlet: number
  incidence: number
  diffusionFactor: number
}

export interface OperatingPoint {
  speedFraction: number
  efficiencyRatio: number
  flowPointIndex: number
  /** Corrected inlet mass flow: headline x-axis for the compressor map. */
  correctedMassFlow: number
  stages: StageResult[]
  overallPressureRatio: number
  overallTemperatureRatio: number
  overallEfficiency: number
  /** True when at least one stage fell outside its stall/choke window. */
  stalled: boolean
}

export interface AnalysisResults {
  /** True only for client-side placeholder data; the API always returns false. */
  stub: boolean
  generatedAt: string
  runtimeMs: number
  /** Unit system the numbers are reported in. */
  units?: "SI" | "US"
  speeds: number[]
  operatingPoints: OperatingPoint[]
  design: {
    pressureRatio: number
    efficiency: number
    massFlow: number
    stages: number
    surgeMarginPct: number
  }
}
