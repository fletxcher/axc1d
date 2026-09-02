"""
AXC1D HTTP API.

Run locally:
    cd web/backend
    fastapi dev routes.py           # http://127.0.0.1:8000  (docs at /docs)

Endpoints
    GET    /api/health
    GET    /api/config/default          reference input deck
    POST   /api/config/validate         structural pre-flight checks
    POST   /api/solve                   full stage-stacking sweep  (?persist=true to keep)
    GET    /api/runs                     list persisted sweeps      (in-memory for now)
    GET    /api/runs/{run_id}            retrieve a persisted sweep
    DELETE /api/runs/{run_id}            drop a persisted sweep
    POST   /api/calc/meanline-radius     cml()
    POST   /api/calc/specific-heat       cpf()
    POST   /api/calc/design-point        cspref() reference performance

Data retrieval is served from an in-process dict (`_RUNS`). It is intentionally
the only storage layer today; swapping it for a database means replacing the
handful of `_RUNS` accesses in this file - the request/response contracts do
not change.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
import services
from models import (
    AnalysisConfig,
    AnalysisResults,
    DesignPointResponse,
    HealthResponse,
    MeanlineRadiusRequest,
    MeanlineRadiusResponse,
    RunSummary,
    SpecificHeatRequest,
    SpecificHeatResponse,
    ValidationResponse,
)

API_VERSION = "0.1.0"

app = FastAPI(
    title="AXC1D",
    version=API_VERSION,
    description="1D meanline axial-compressor stage-stacking analysis.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === IN-MEMORY RUN STORE === #

# run_id -> (created_at_iso, config, results)
_RUNS: Dict[str, Tuple[str, AnalysisConfig, AnalysisResults]] = {}
_MAX_RUNS = 50


def _persist_run(cfg: AnalysisConfig, results: AnalysisResults) -> str:
    run_id = uuid.uuid4().hex[:12]
    _RUNS[run_id] = (datetime.now(timezone.utc).isoformat(), cfg, results)
    # keep the store bounded, oldest-out
    if len(_RUNS) > _MAX_RUNS:
        oldest = min(_RUNS, key=lambda k: _RUNS[k][0])
        _RUNS.pop(oldest, None)
    return run_id


def _summary(run_id: str) -> RunSummary:
    created, cfg, results = _RUNS[run_id]
    return RunSummary(
        id=run_id,
        createdAt=created,
        stages=cfg.parameters.stages,
        speeds=cfg.parameters.speeds,
        pointsPerCurve=cfg.parameters.pointsPerCurve,
        designPressureRatio=results.design.pressureRatio,
        designEfficiency=results.design.efficiency,
    )

# === META / RETRIEVAL === #

@app.get("/api/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="axc1d-api", version=API_VERSION)

@app.get("/api/config/default", response_model=AnalysisConfig, tags=["config"])
def get_default_config() -> AnalysisConfig:
    """The reference deck (matches the desktop tool's origin.axc1d)."""
    return services.default_config()

@app.post("/api/config/validate", response_model=ValidationResponse, tags=["config"])
def validate(config: AnalysisConfig) -> ValidationResponse:
    issues = services.validate_config(config)
    return ValidationResponse(valid=not issues, issues=issues)

# === CALCULATIONS === #

@app.post("/api/solve", response_model=AnalysisResults, tags=["solve"])
def solve(
    config: AnalysisConfig,
    response: Response,
    persist: bool = Query(False, description="keep the result in the run store"),
) -> AnalysisResults:
    try:
        results = services.run_analysis(config)
    except (ValueError, ZeroDivisionError, OverflowError, KeyError, IndexError) as exc:
        raise HTTPException(status_code=422, detail=f"solver error: {exc}") from exc

    if persist:
        # the run id rides on a header so the body stays the pure contract
        response.headers["X-Run-Id"] = _persist_run(config, results)
    return results

@app.post("/api/calc/meanline-radius", response_model=MeanlineRadiusResponse, tags=["calc"])
def meanline_radius(body: MeanlineRadiusRequest) -> MeanlineRadiusResponse:
    if body.tipRadius <= body.hubRadius:
        raise HTTPException(422, "tip radius must exceed hub radius")
    return services.compute_meanline_radius(body.tipRadius, body.hubRadius)

@app.post("/api/calc/specific-heat", response_model=SpecificHeatResponse, tags=["calc"])
def specific_heat(body: SpecificHeatRequest) -> SpecificHeatResponse:
    return services.compute_specific_heat(
        body.temperature, body.coefficients, body.molecularWeight, body.si
    )

@app.post("/api/calc/design-point", response_model=DesignPointResponse, tags=["calc"])
def design_point(config: AnalysisConfig) -> DesignPointResponse:
    try:
        return services.compute_design_point(config)
    except (ValueError, ZeroDivisionError, OverflowError, KeyError, IndexError) as exc:
        raise HTTPException(status_code=422, detail=f"solver error: {exc}") from exc

# === PERSISTED RUNS === #

@app.get("/api/runs", response_model=List[RunSummary], tags=["runs"])
def list_runs() -> List[RunSummary]:
    return [_summary(rid) for rid in sorted(_RUNS, key=lambda k: _RUNS[k][0], reverse=True)]

@app.get("/api/runs/{run_id}", response_model=AnalysisResults, tags=["runs"])
def get_run(run_id: str) -> AnalysisResults:
    entry = _RUNS.get(run_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="run not found")
    return entry[2]

@app.delete("/api/runs/{run_id}", status_code=204, tags=["runs"])
def delete_run(run_id: str) -> Response:
    if _RUNS.pop(run_id, None) is None:
        raise HTTPException(status_code=404, detail="run not found")
    return Response(status_code=204)
