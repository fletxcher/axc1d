# AXC1D - 1D Meanline Axial Compressor Design Tool

## Overview

**AXC1D** is a C++ implementation of a 1D meanline stage-stacking code for multistage axial compressor analysis, based on NASA's STGSTK methodology (Technical Paper 2020, 1982). It enables rapid off-design performance prediction across operating speeds and flow ranges.

**Key Capabilities:**
- Simplifies 3D blade flow to single meanline representation at intermediate radius
- Replaces expensive 3D CFD with seconds-fast calculations (±3-5% accuracy)
- Incorporates empirical correlations from experimental test data
- Predicts off-design behavior at different speeds, flows, and blade settings

### Stage-Stacking Method

Each stage is analyzed sequentially: input characteristics define pressure rise ψ(φ) and efficiency η_ad(φ), velocity diagrams capture thermodynamic state at meanline, stages stack with each outlet feeding next inlet, mass flow iteration ensures continuity convergence.

```bash
MAIN_ROUTINE:
  // Initialization
  READ input_data via CSINPT()
  
  FOR each_stage:
    CALCULATE meanline_radii:
      RM = SQRT(RT² - annulus_area/(2π))
    CALCULATE wheel_speeds:
      U = RM × RPM × (2π/60)
  
  // Design Point Calculation
  CALL CSPREF():
    FOR each_stage:
      // Inlet velocity triangle
      GIVEN: inlet_total_pressure, inlet_total_temp, flow_angle_β2
      ITERATE to find axial_velocity_Vz2 satisfying:
        continuity: W = ρ × Area × Vz
        ideal_gas: with Cp, γ from CPF(static_temp)
      
      CALCULATE tangential_velocity: Vt2 = Vz2 × tan(β2)
      DEFINE flow_coefficient: φ = Vz2 / U2
      
      // Outlet velocity triangle
      IF stage_characteristics_input:
        INTERPOLATE η_adiabatic(φ), ψ(φ) from tables
      ELSE:
        USE input pressure_ratio, efficiency
      
      APPLY Euler_turbine_equation:
        Vt3 = [Cp×η×(T3-T2) + U2×Vt2] / U3
      
      ITERATE to find Vz3 satisfying:
        continuity at outlet
        thermodynamic_consistency
      
      STACK: outlet_state → becomes inlet_state for next_stage
  
  // Optional Corrections
  IF stage_chars_not_input:
    CALL CSETA():  // Generate η(φ) curves
      FIT two_parabolas:
        parabola1: φ_stall → φ_design (peak efficiency)
        parabola2: φ_design → φ_choke
      ENFORCE constraints:
        η = η_design at φ_design
        η = 0.9×η_design at φ_stall
        η = 0.8×η_design at φ_choke
    
    CALL CSPSI():  // Generate ψ(φ) curves
      FOR each φ_value:
        CALCULATE Vz2 from φ
        RECOMPUTE velocity_triangles
        EXTRACT ψ = work_coefficient
  
  IF off_design_speed:
    CALL CSPSD():  // Part-speed corrections
      ADJUST pressure_coefficient:
        Δψ_N based on Mach_number_effects
      EXPAND flow_range:
        Δφ_N based on choking_physics
      
      IF rotor_deviation_option:
        MODIFY β3_relative based on speed_correlation
  
  IF blade_reset:
    CALL CSPAN():  // Variable geometry
      UPDATE flow_angles: β = β_design + Δβ_reset
      RECALCULATE velocity_triangles
      EXTRACT new ψ(φ), η(φ) curves
      
      IF rotor_deviation_option:
        ADJUST β3 = β3_design + Δβ_stagger
  
  // Performance Map Generation
  CALL CSOUPT():
    FOR each speed_line:
      FOR flow from W_min to W_max:
        FOR each_stage:
          COMPUTE inlet_velocity_diagram
          DETERMINE φ_actual
          
          IF φ_actual outside [φ_stall, φ_choke]:
            FLAG "STALL or CHOKE"
            BREAK
          
          INTERPOLATE η(φ), ψ(φ) from stage_characteristics
          COMPUTE outlet_conditions
          ACCUMULATE compressor_totals:
            PR_total = Π(PR_stage)
            η_total via mass-averaged enthalpy rise
        
        OUTPUT stage_and_compressor_performance

SUBROUTINE CPF(temperature):
  // Specific heat polynomial
  Cp = C1 + C2×T + C3×T² + C4×T³ + C5×T⁴ + C6×T⁵
  γ = Cp / (Cp - R)
  RETURN Cp, γ

PHYSICS_MODELS:
  Rotor_deviation_correlation(Δφ, ΔN, Δγ):
    // Empirical from NASA test data
    Δβ3 = -10 × (V3'/V2')_off / (V3'/V2')_design - 1
  
  LOSS_CORRELATIONS:
    Diffusion_factor = 1 - V3/V2 + (Δ(rVθ))/(2σV2_inlet)
    Efficiency_decrement from boundary_layer_models
```

## Usage

```bash
git clone git@https://github.com/fletxcher/axc1d
cd /home/axc1d/src && rm -rf build && mkdir build && cd build
cmake .. && ninja && ./axc1d
```
**Prerequisites:** Qt 5.15+/6.0+, CMake 3.16+, C++17 compiler

## Methodology

Based on **NASA Technical Paper 2020 (1982)** - STGSTK by Lona Urasek. Advantages: simple 1D model, fast (seconds vs hours), empirically grounded, clear physical insight, handles 1-20+ stages. Limitations: assumes radial equilibrium, valid for conventional subsonic blades, most accurate for similar compressors in correlation database.