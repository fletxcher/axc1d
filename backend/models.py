"""
Pydantic request/response schemas for the AXC1D API.

Field names are camelCase so the JSON contract matches the Next.js frontend
(`web/frontend/lib/analysis/types.ts`) one-to-one.
"""

from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field

class OperatingParameters(BaseModel):
    stages: int = Field(ge=1, le=24)
    speeds: int = Field(ge=1, le=24)
    inletPressure: float = Field(gt=0, description="P0 (kPa if SI, psia otherwise)")
    inletTemperature: float = Field(gt=0, description="T0 (K if SI, degR otherwise)")
    pointsPerCurve: int = Field(ge=2, le=64)
    molecularWeight: float = Field(gt=0)
    rpm: float = Field(gt=0)
    massFlow: float = Field(gt=0, description="Design mass flow (kg/s if SI, lbm/s otherwise)")


class DeviationFactors(BaseModel):
    speedPsi: bool = True
    speedPhi: bool = True
    deviationBladeReset: bool = True
    deviationSpeed: bool = True
    deviationFlow: bool = True
    siUnits: bool = True


class StageGeometry(BaseModel):
    rotorInletTip: float
    rotorInletHub: float
    rotorOutletTip: float
    rotorOutletHub: float
    inletFlowAngle: float
    bladeResetAbs: float
    bladeResetRel: float
    bladeResetOutlet: float
    rotorMetalAngle: float
    rotorSolidity: float
    statorMetalAngle: float


class EfficiencyRatioRow(BaseModel):
    speedFraction: float
    efficiencyRatio: float


class BleedRow(BaseModel):
    speedFraction: float
    stageBleed: List[float]


class CharacteristicPoint(BaseModel):
    phi: float
    psi: float = 0.0
    eta: float = 0.0


class StageCharacteristic(BaseModel):
    points: List[CharacteristicPoint]


class AnalysisConfig(BaseModel):
    parameters: OperatingParameters
    deviationFactors: DeviationFactors
    gasCoefficients: List[float] = Field(min_length=6, max_length=6)
    stageGeometry: List[StageGeometry]
    efficiencyRatioTable: List[EfficiencyRatioRow]
    bleedTable: List[BleedRow]
    characteristics: List[StageCharacteristic]


# === SOLVER OUTPUT === #


class StageResult(BaseModel):
    stage: int
    massFlow: float
    phi: float
    psi: float
    eta: float
    pressureRatio: float
    temperatureRatio: float
    inletTotalTemperature: float
    outletTotalTemperature: float
    inletTotalPressure: float
    outletTotalPressure: float
    axialVelocityInlet: float
    axialVelocityOutlet: float
    bladeSpeedInlet: float
    bladeSpeedOutlet: float
    swirlVelocityInlet: float
    swirlVelocityOutlet: float
    incidence: float
    diffusionFactor: float


class OperatingPoint(BaseModel):
    speedFraction: float
    efficiencyRatio: float
    flowPointIndex: int
    correctedMassFlow: float
    stages: List[StageResult]
    overallPressureRatio: float
    overallTemperatureRatio: float
    overallEfficiency: float
    stalled: bool


class DesignSummary(BaseModel):
    pressureRatio: float
    efficiency: float
    massFlow: float
    stages: int
    surgeMarginPct: float


class AnalysisResults(BaseModel):
    stub: bool = False
    generatedAt: str
    runtimeMs: int
    units: Literal["SI", "US"]
    speeds: List[float]
    operatingPoints: List[OperatingPoint]
    design: DesignSummary


# === STANDALONE CALCULATION ENDPOINTS === #


class MeanlineRadiusRequest(BaseModel):
    tipRadius: float = Field(gt=0)
    hubRadius: float = Field(ge=0)


class MeanlineRadiusResponse(BaseModel):
    meanlineRadius: float
    annulusArea: float | None = None


class SpecificHeatRequest(BaseModel):
    temperature: float = Field(gt=0, description="Static temperature")
    coefficients: List[float] = Field(min_length=6, max_length=6)
    molecularWeight: float = Field(default=28.97, gt=0)
    si: bool = Field(default=False, description="temperature is in K (converted to degR)")


class SpecificHeatResponse(BaseModel):
    temperature: float
    specificHeat: float
    gamma: float
    gammaMinusOne: float
    cpOverR: float


class DesignPointStage(BaseModel):
    stage: int
    phiRef: float
    psiRef: float
    etaRef: float
    diffusionFactor: float
    rotorIncidence: float
    statorIncidence: float
    velocityRatioV3V2: float
    meanlineRadiusInlet: float
    meanlineRadiusOutlet: float
    bladeSpeedInlet: float
    bladeSpeedOutlet: float


class DesignPointResponse(BaseModel):
    units: Literal["SI", "US"]
    stages: List[DesignPointStage]


class ValidationIssue(BaseModel):
    section: str
    message: str


class ValidationResponse(BaseModel):
    valid: bool
    issues: List[ValidationIssue]


class RunSummary(BaseModel):
    id: str
    createdAt: str
    stages: int
    speeds: int
    pointsPerCurve: int
    designPressureRatio: float
    designEfficiency: float


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
