import math 
import logging
from typing import List
import numpy as np
from manager import AXC1DEventManager 

class AXC1DSolver:
    """
    Multistage compressor analysis and performance calculation solver.
    """
    def __init__(self, logger: logging.Logger, event_manager: AXC1DEventManager):
        """
        Initialize the AXC1DSolver instance.
        
        Args:
            logger: Logger instance for diagnostic and informational output.
        """
        self.logger = logger

        self.ru = None
        self.pi = None
        self.g  = None
        self.aj = None
        self.rad = None

        self.rg = None 
        self.dcp = None
        self.gj = None
        self.g2j = None 
        self.rpmrad = None

        self.ts = None
        self.gamma = None

        self.input_params = None
        self.deviation_factors = None
        self.specific_heat_coefficients = None
        self.stage_geometry = None
        self.stage_performance_characteristics = None
        self.efficiency_ratio_table = None
        self.bleed_table = None
        self.input_design_characteristics = None
        self.stage_reference_params = None
        self.dpsis_table = None
        self.computed_characteristics = None

        self.area2 = self.area3 = []
        self.rm2 = self.rm3 = []
        self.um2 = self.um3 = []
        self.bet2m = []
        self.rk2m = self.sk2m = self.cb2m = []
        self.cb2mr = self.cb3mr = []

    def cml(self, rotor_tip: float, rotor_hub: float):
        """
        Calculate the meanline radius
        """
        return math.sqrt((math.pow(rotor_tip, 2) + math.pow(rotor_hub, 2)) / 2)

    def cspref(self):
        """
        Calculate meanline velocity diagrams and design stage performance.
        
        At design speed and flow, computes velocity diagrams at meanline radii 
        for rotor inlet and outlet, and selected performance parameters for each 
        stage. Performs a one-dimensional, compressible, inviscid flow calculation 
        using iterative methods to obtain velocity diagrams for design conditions.
        Calculates design flow coefficient, blade angles, incidence angles, and 
        rotor diffusion factors.
        
        :param self: Description
        """
        pass

    def cpf(self, ts: float):
        """
        Calculate specific heat and gamma as functions of temperature.
        
        Computes Cp from a fifth-degree polynomial of static temperature, and 
        derives gamma from the relation gamma = Cp / (Cp - R). 
        Supplies properties for flow calculations in other subroutines.
        
        :param self: Description
        :param ts: Static Temperature
        :type ts: float
        """
        # C_p : C_1 + C_2 * t + C_3 * t^2 + C_4 ^ t^3 + C_5 * t^4 + C_6 * t^5
        self.ts = ts
        self.specific_heat = (
            (self.specific_heat_coefficients[0]) + 
            (self.specific_heat_coefficients[1] * self.ts) +
            (self.specific_heat_coefficients[2] * pow(self.ts, 2)) +
            (self.specific_heat_coefficients[3] * pow(self.ts, 3)) +
            (self.specific_heat_coefficients[4] * pow(self.ts, 4)) +
            (self.specific_heat_coefficients[5] * pow(self.ts, 5)) 
        )
        # γ = C_p ​/ (C_p​ - R​)
        self.gamma = self.specific_heat / (self.specific_heat - self.ru)
        pass

    def cseta(self):
        """
        Generate stage adiabatic efficiency curve vs. flow coefficient.
        
        Generates a curve for eta_ad(phi) composed of two parabolas: one from 
        stall to design flow, and another from design to choke flow. The peak 
        efficiency occurs at design conditions. Calculates efficiency values for 
        all input flow coefficients, repeated for each compressor stage.
        
        :param self: Description
        """
        pass

    def cspsi(self):
        """
        Generate stage pressure coefficient curve vs. flow coefficient.
        
        Obtains pressure coefficient values for each stage at various input flow 
        coefficients when stage characteristics are not provided. Uses design conditions 
        with iterative calculations to compute velocity components and pressure rise. 
        Applies optional rotor deviation angle corrections for off-design flow conditions.
        
        :param self: Description
        """
        pass

    def cspsd(self):
        """
        Adjust pressure coefficient for off-design rotative speeds.
        
        Calculates changes in pressure rise coefficient for off-design speeds. 
        Uses design values and applies iterative calculations with varying rotative 
        speed N. Computes velocity components, temperature rise, and pressure 
        coefficient adjustments. Supports optional rotor deviation angle corrections 
        for off-design speeds.
        
        :param self: Description
        """
        pass

    def csoupt(self):
        """
        Calculate and output stage and cumulative compressor performance.
        
        Computes individual stage and cumulative compressor performance parameters 
        for selected speeds and flow conditions. Outputs velocity diagrams, flow 
        coefficients, pressure rise, adiabatic efficiency, blade angles, and 
        diffusion factors. Results in SI or U.S. customary units. Detects and 
        reports stall or choke conditions for out-of-range flows.
        
        :param self: Description
        """
        pass

    def cspan(self):
        """
        Alter stage characteristics for blade setting angle changes.
        
        Checks and applies blade reset parameters (CB2M, CB2MR, CB3MR) to alter 
        stage design flow coefficient and pressure coefficient. Recalculates stage 
        velocity diagrams and performance parameters for each upstream stator reset 
        or blade angle change. Modifies stage characteristic curve accounting for 
        blade deviation angle adjustments.
        
        :param self: Description
        """
        pass

    def run(self, input_params: List[float], deviation_factors: List[float], specific_heat_coefficients: List[float], 
            stage_geometry: List[dict], bleed_table: List[List[float]], efficiency_ratio_table: List[List[float]]):
        """
        Execute the compressor analysis logic.
        
        :param file_path: path to the input deck file
        :type file_path: str
        """
        self.logger.info("A")
        # gas constant (ft·lbf/(lbmol·°R))
        self.ru = 1545.44 
        # pi constant 
        self.pi = 3.14159
        # gravitational acceleration (US customary units), not SI units!
        self.g  = 32.1740
        # mechanical equivalent of heat (ft·lbf/Btu)
        self.aj = 778.12 
        # radians to degrees conversion
        self.rad = 57.29578

        # SI INPUT PARAMETERS
        # [STAGES, SPEEDS, P_0 IN, T_0 IN, POINTS, MOLE WT DES, RPM DES, FLOW ]
        self.input_params = input_params

        # DEVIATION FACTORS
        # [SPDPSI, SPDPHI, DRDEVG, DRDEVN, DRDEVP, UNITS]
        self.deviation_factors = deviation_factors

        # SPECIFIC HEAT COEFFICIENTS
        # [CPCO(1), CPCO(2), CPCO(3), CPCO(4), CPCO(5), CPCO(6)]
        self.specific_heat_coefficients = specific_heat_coefficients

        # STAGE GEOMETRY 
        # [[STAGE, RT2, RH2, RT3, RH3, BET2M, CB2M, CB2MR, CB3MR, RK2M, RSOLM, SK2M],[...], ...N]
        # where N = number of stages
        self.stage_geometry = stage_geometry

        # BLEED TABLE (STAGE, PCT SPD)
        # [[PCT SPD, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [], ...N]
        # where N = 5
        self.bleed_table = bleed_table

        # EFFICIENCY RATIO TABLE (PCTSPD vs ETARAT)
        # [[PCTSPD, ETARAT], ...N]
        # where N = 5
        self.efficiency_ratio_table = efficiency_ratio_table

        self.rg = self.ru / self.input_params[5]
        self.dcp = self.rg / self.aj
        self.gj = self.g * self.aj
        self.g2j = self.gj * 2.0 
        self.rpmrad = self.pi / 360.0 

        # for each stage
        for i in range(int(self.input_params[0])):
            # calculate flow areas
            # inlet annulus area: (RT2(I) + RH2(I)) * (RT2(I) - RH2(I)) * PI / 144.0
            self.area2[i] = (self.stage_geometry[i][1] + self.stage_geometry[i][2]) * (self.stage_geometry[i][1] - self.stage_geometry[i][2]) * self.pi / 144.0
            # outlet annulus area: (RT3(I) + RH3(I)) * (RT3(I) - RH3(I)) * PI / 144.0
            self.area3[i] = (self.stage_geometry[i][3] + self.stage_geometry[i][4]) * (self.stage_geometry[i][3] - self.stage_geometry[i][4]) * self.pi / 144.0

            # calculate meanline radii
            # inlet meanline radius: SQRT(RT2(I) ** 2 - AREA2(I) * 72.0 / PI)
            self.rm2[i] = math.sqrt(math.pow(self.stage_geometry[i][1], 2) - self.area2[i] * 72.0 / self.pi)
            # outlet meanline radius: SQRT(RT3(I) ** 2 - AREA3(I) * 72.0 / PI)
            self.rm3[i] = math.sqrt(math.pow(self.stage_geometry[i][3], 2) - self.area3[i] * 72.0 / self.pi)

            # calculate blade speeds
            # blade speed at the inlet: RM2(I) * DESRPM * RPMRAD
            self.um2[i] = self.rm2[i] * self.input_params[7] * self.rpmrad
            # blade speed at the outlet: RM3(I) * DESRPM * RPMRAD
            self.um3[i] = self.rm3[i] * self.input_params[7] * self.rpmrad

            # convert degrees to radians: BET2M(I,1) = BET2M(I,1)/RAD
            self.stage_geometry[i][5] = self.stage_geometry[i][5] / self.rad      
            # adjust rotor blade angle: RK2M(I) + CB2MR(I + 1) 
            self.rk2m[i] = self.rk2m[i] + self.cb2mr[i + 1] 
            # adjust stator blade angle: SK2M(I) + CB2M(I + 1)
            self.sk2m[i] = self.sk2m[i] + self.cb2m[i + 1] 
            # convert correction to radians
            self.cb2m[i] = self.cb2m[i] / self.rad            
            self.cb2mr[i] = self.cb2mr[i] / self.rad
            self.cb3mr[i] = self.cb3mr[i] / self.rad

        # call csref method for reference calculations
        self.cspref()

        # if efficiency not provided, calculate it
        # IF(ETADES(I,1,1) .EQ. 0.0) CALL CSETA  
        # if (self.etades(i, 1, 1) == 0.0): self.cseta

        # if pressure coeff not provided, calculate it
        # IF(PSIDES(I,1,1).EQ.0.0) CALL CSPSI   
        # if (self.psides(i, 1, 1) == 0.0): self.cspsi
        
        # IF(SPDPSI.EQ.1.0) CALL CSPSD 
        # if (self.spdpsi(i, 1, 1) == 0.0): self.cspsd

        # call cspan method to calculate span-wise variations
        self.cspan()
        for i in range(int(self.input_params[0])):
            # Convert back to degrees for output
            self.stage_reference_params[i][7] = self.stage_geometry[i][7] * self.rad
            self.stage_reference_params[i][8] = self.stage_geometry[i][8] * self.rad
        
        # IF (UNITS.EQ.1.0) FLOCAL(I,1) = FLOCAL(I,1)/0.453592
        # TODO: if SI units, convert flow back from lb/sec to kg/sec for internal calculations

        # TODO: calculate off-design performance
        
        # TODO: option to alter flow coefficient 

        # write the results to the terminal
        self.logger.info(f"")

        

