# AXC1D - 1D Meanline Axial Compressor Design Tool

## Overview

**AXC1D** is a Python application that makes use of a custom 1D meanline stage-stacking code for multistage axial compressor analysis, based on NASA's STGSTK methodology (Technical Paper 2020, 1982). It enables rapid off-design performance prediction across operating speeds and flow ranges.

**Key Capabilities:**
- Simplifies 3D blade flow to single meanline representation at intermediate radius
- Replaces expensive 3D CFD with seconds-fast calculations (±3-5% accuracy)
- Incorporates empirical correlations from experimental test data
- Predicts off-design behavior at different speeds, flows, and blade settings

### Stage-Stacking Method

Each stage is analyzed sequentially: input characteristics define pressure rise ψ(φ) and efficiency η_ad(φ), velocity diagrams capture thermodynamic state at meanline, stages stack with each outlet feeding next inlet, mass flow iteration ensures continuity convergence.

### Psuedo-Code
```bash
BEGIN
│
├── CSINPT reads all geometry, blade angles, design points, speed lines, and option flags
│
├── CPF computes Cp and gamma at inlet temperature
│
├── CSPREF computes design-point velocity triangles and reference phi, psi, eta for every stage
│
├── for each stage:
│   ├── CSETA builds the eta(phi) characteristic curve
│   ├── CSPSI builds the psi(phi) characteristic curve (applies off-design flow deviation correction if flagged)
│   ├── CSPAN applies blade reset correction to psi(phi) if flagged
│   └── CSPSD applies off-design speed correction to psi(phi) if flagged
│
└── for each speed line:
    └── for each flow point:
        │
        ├── MAIN applies phi correction for off-design speed if flagged
        │
        ├── [INNER STAGE-STACKING LOOP]:
        │   for each stage:
        │   - look up eta and psi from corrected characteristics
        │   - compute velocity triangles (rotor inlet and exit)
        │   - compute T0_exit and P0_exit
        │   - enforce continuity → find Va at exit
        │   - update state vector → feed to next stage
        │
        └── CSOUPT writes converged performance for this point
                                                             └── END
        
```
## Project Structure
```bash
.
├── NASA STGSTK Paper.pdf   # original NASA research paper
├── README.md               
├── requirements.txt        # all neccessary libraries for the project
├── src
│   ├── __init__.py
│   ├── __pycache__
│   └── python
│       ├── __init__.py
│       ├── __pycache__
│       ├── application.py  # main application 
│       ├── editor.py       # configuration menu for all of the inputs to the solver
│       ├── plotter.py      # pyqt widget that holds all of the plots and displays the output of the program 
│       └── solver.py       # python implementation of the multi-stage axial compressor stage stacking program
└── tests                   # unit tests for each seperate component of the solver program
    ├── __init__.py         
    ├── __pycache__         
    ├── cml.py              # unit tests for the computation of the meanline
    ├── cpf.py              # unit tests for the computation of the specific heat and specific heat ratio
    ├── cseta.py            # unit tests for the computation of the stage adiabatic efficiency vs. flow coefficient curve
    ├── csoupt.py           # unit tests for the computation of the output stage and cumulative compressor performance
    ├── cspan.py            # unit tests for the computation of the alteration of stage characteristics for blade setting angle changes
    ├── cspref.py           # unit tests for the computation of the meanline velocity diagrams and design stage performance
    ├── cspsd.py            # unit tests for the computation of the adjusted pressure coefficient for off-design rotative speeds.
    ├── cspsi.py            # unit tests for the computation of stage pressure coefficient vs. flow coefficient curve
    └── pytest.ini          # pytest configuration
```

## Installation
```bash
git clone git@https://github.com/fletxcher/axc1d 
cd axc1d/
python3 -m venv venv
source venv/bin/activate
pip install -r requirments.txt
```

## Usage
```bash
cd axc1d/src/python/
python application.py
```

## Methodology
Based on **NASA Technical Paper 2020 (1982)** - STGSTK by Ronald J. Steinke