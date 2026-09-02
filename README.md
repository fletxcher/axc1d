# AXC1D - 1D Meanline Axial Compressor Design Tool

## Overview

**AXC1D** predicts the off-design performance of multistage axial compressors
with a custom 1D meanline stage-stacking code, based on NASA's **STGSTK**
methodology (Technical Paper 2020, 1982). It trades the cost of 3D CFD for
seconds-fast estimates (±3-5% against test data) across operating speeds and
flow ranges.

It runs as two pieces: a FastAPI service that holds the solver, and a Next.js
workspace for building an input deck and reading off the compressor map.

**Key capabilities**

- Simplifies 3D blade flow to a single meanline representation at the RMS radius
- Replaces expensive 3D CFD with seconds-fast calculations (±3-5% accuracy)
- Incorporates empirical correlations from experimental test data
- Predicts off-design behaviour at different speeds, flows, and blade settings

## Stage-stacking method

Each stage is analysed sequentially: input characteristics define the pressure
rise ψ(φ) and efficiency η_ad(φ), velocity diagrams capture the thermodynamic
state at the meanline, stages stack with each outlet feeding the next inlet, and
a mass-flow iteration enforces continuity.

```
BEGIN
│
├── CSINPT   read geometry, blade angles, design points, cases, option flags
│
├── CPF      compute Cp and gamma at inlet temperature
│
├── CSPREF   design-point velocity triangles and reference phi, psi, eta per stage
│
├── for each stage:
│   ├── CSETA   build the eta(phi) characteristic curve
│   ├── CSPSI   build the psi(phi) characteristic curve (+ off-design flow deviation if flagged)
│   ├── CSPAN   apply blade-reset correction to psi(phi) if flagged
│   └── CSPSD   apply off-design speed correction to psi(phi) if flagged
│
└── for each case:
    └── for each flow point:
        │
        ├── phi correction for off-design speed if flagged
        │
        ├── [INNER STAGE-STACKING LOOP] for each stage:
        │     look up eta and psi from the corrected characteristics
        │     compute rotor inlet / exit velocity triangles
        │     compute T0_exit and P0_exit
        │     carry continuity to the next stage
        │
        └── CSOUPT  write converged stage and cumulative performance
                                                              └── END
```

These routines are the methods of `Solver` in `backend/services.py`: `cml`,
`cpf`, `cspref`, `cseta`, `cspsi`, `cspsd`, `cspan`, `csoupt`, and `run`.

## Architecture

| Path | Stack | Role |
|------|-------|------|
| `backend/`  | FastAPI + Pydantic (Python 3.12) | The solver over HTTP - `/api/solve` and the individual calculations |
| `frontend/` | Next.js 16 (App Router), React 19, Tailwind v4, shadcn/ui | Guided input workflow and the results workspace |

The frontend posts an `AnalysisConfig` to `POST /api/solve` and renders the
`AnalysisResults` it gets back. Both shapes are defined once per side -
`frontend/lib/analysis/types.ts` and `backend/models.py` - and kept in sync.

## Project structure

```
.
├── NASA STGSTK Paper.pdf        original NASA research paper
├── README.md
│
├── backend/
│   ├── routes.py               FastAPI app, endpoints, in-memory run store
│   ├── services.py             Solver, schema adapters, reference deck
│   ├── models.py               Pydantic request / response schemas
│   └── pyproject.toml
│
└── frontend/
    ├── app/
    │   ├── page.tsx             landing / overview
    │   └── analysis/
    │       ├── layout.tsx       header + sidebar section menu
    │       ├── parameters/      step 1 - stage & case counts, inlet, design point
    │       ├── deviation/       step 2 - off-design correction flags, unit system
    │       ├── gas/             step 3 - specific-heat polynomial coefficients
    │       ├── geometry/        step 4 - per-stage annulus radii, blade angles, solidity
    │       ├── tables/          step 5 - efficiency-ratio and inter-stage bleed tables
    │       ├── characteristics/ step 6 - phi / psi / eta design-speed curve points
    │       ├── review/          step 7 - deck summary, readiness checks, run
    │       └── results/         compressor & efficiency maps, stage explorer, tables
    ├── components/analysis/     stepper, form fields, results/* (charts, export, tables)
    └── lib/
        ├── api.ts              backend client (base URL, error handling)
        └── analysis/           types, default deck, localStorage store, solve call
```

## Running it

### Backend

```bash
cd backend
uv sync                
uv run fastapi dev routes.py
# -> http://127.0.0.1:8000 
```

If a stale `VIRTUAL_ENV` from an earlier layout is exported in your shell, `uv`
warns and ignores it - run `unset VIRTUAL_ENV` or open a fresh terminal.

### Frontend

```bash
cd frontend
npm install
npm run dev
# -> http://localhost:3000
```

The API base URL is `NEXT_PUBLIC_API_URL` (see `frontend/.env.example`); it
defaults to `http://localhost:8000`, and the backend's CORS allow-list already
includes `localhost:3000`. A failed run surfaces the API error, including how to
start the backend when it is unreachable.

## Workflow

`/` is the overview. `/analysis/<step>` gives one page per input section; the
left sidebar is the primary navigation, so steps can be revisited in any order.
The input deck and the last results set persist to `localStorage`
(`axc1d.config.v1`, `axc1d.results.v1`). Theme (light / dark / system) is in the
header alongside a settings dialog and a GitHub link.

`/analysis/results` shows the compressor and efficiency maps (one line per case),
a per-stage explorer of outlet total pressure and temperature, the full
operating-point table, and JSON / CSV / text export.

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET  | `/api/health` | liveness |
| GET  | `/api/config/default` | the reference input deck |
| POST | `/api/config/validate` | structural pre-flight checks |
| POST | `/api/solve` | full stage-stacking sweep (`?persist=true` keeps it) |
| GET  | `/api/runs`, `/api/runs/{id}` | list / retrieve persisted sweeps |
| DELETE | `/api/runs/{id}` | drop a persisted sweep |
| POST | `/api/calc/meanline-radius` | `cml()` |
| POST | `/api/calc/specific-heat` | `cpf()` - Cp and gamma vs temperature |
| POST | `/api/calc/design-point` | `cspref()` - design-speed reference performance |

Persisted runs live in an in-process dict (`_RUNS` in `routes.py`) - the one
seam a database would replace. Nothing else changes when it does.

## Methodology

Based on **NASA Technical Paper 2020 (1982)** - STGSTK, by Ronald J. Steinke.
Not a substitute for 3D CFD.
