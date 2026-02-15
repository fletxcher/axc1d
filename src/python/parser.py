import io
import logging
import numpy as np
from typing import List

class AXC1DParser:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.n_stages = 0

    def input_params(self, lines: List[str]):
        idx = lines.index("SI INPUT PARAMETERS")
        # skip the first n_skip_lines
        n_skip_lines = 2 
        n_params = 8
        values = [line.split(':') for line in lines[idx + n_skip_lines : idx + n_params + n_skip_lines]]
        result = np.array(values)[:, 1].astype(float)
        self.n_stages = int(result[0])
        self.logger.info(f"SI Input Params: {result.tolist()}")
        return result

    def deviation_factors(self, lines: List[str]):
        idx = lines.index("DEVIATION FACTORS")
        # skip the first n_skip_lines
        n_skip_lines = 2 
        n_params = 6
        values = [line.split(':') for line in lines[idx + n_skip_lines : idx + n_params + n_skip_lines]]
        result = np.array(values)[:, 1].astype(float)
        self.logger.info(f"Deviation Factors: {result.tolist()}")
        return result

    def specific_heat_coefficients(self, lines: List[str]):
        idx = lines.index("SPECIFIC HEAT COEFFICIENTS")
        # skip the first n_skip_lines
        n_skip_lines = 2 
        n_params = 6
        values = [line.split(':') for line in lines[idx + n_skip_lines : idx + n_params + n_skip_lines]]
        result = np.array(values)[:, 1].astype(float)
        self.logger.info(f"Specific Heat Coefficients: {result.tolist()}")
        return result

    def stage_geometry(self, lines: List[str]):
        idx = lines.index("STAGE GEOMETRY")
        # skip the first n_skip_lines
        n_skip_lines = 5
        n_params = 2
        result = np.genfromtxt(io.StringIO("\n".join(lines[idx + n_skip_lines : idx + n_params + n_skip_lines])))
        self.logger.info(f"Stage Geometry: {result.tolist()}")
        return result
    
    def stage_performance_characteristics(self, lines: List[str]):
        idx = lines.index("STAGE PERFORMANCE CHARACTERISTICS")
        # skip the first n_skip_lines
        n_skip_lines = 4
        n_params = 2
        result = np.genfromtxt(io.StringIO("\n".join(lines[idx + n_skip_lines : idx + n_params + n_skip_lines])))
        self.logger.info(f"Stage Performance Characteristics: {result.tolist()}")
        return result
        
    def efficiency_ratio_table(self, lines: List[str]):
        idx = lines.index("EFFICIENCY RATIO TABLE (PCTSPD vs ETARAT)")
        # skip the first n_skip_lines
        n_skip_lines = 4
        n_params = 5
        result = np.genfromtxt(io.StringIO("\n".join(lines[idx + n_skip_lines : idx + n_params + n_skip_lines])))
        self.logger.info(f"Efficiency Ratio Table: {result.tolist()}")
        return result
        
    def bleed_table(self, lines: List[str]):
        idx = lines.index("BLEED TABLE (STAGE, PCT SPD)")
        # skip the first n_skip_lines
        n_skip_lines = 4
        n_params = 5
        result = np.genfromtxt(io.StringIO("\n".join(lines[idx + n_skip_lines : idx + n_params + n_skip_lines])))
        self.logger.info(f"Bleed Table: {result.tolist()}")
        return result
        
    def input_design_characteristics(self, lines: List[str]):
        values = []
        for i in range(self.n_stages):
            idx = lines.index(f"INPUT DESIGN CHARACTERISTICS - STAGE {i + 1}")
            # skip the first n_skip_lines
            n_skip_lines = 4
            n_params = 3
            # result = np.genfromtxt(io.StringIO("\n".join(lines[idx + n_skip_lines : idx + n_params + n_skip_lines])))
            pct_spd100 = np.array([])
            pct_spd90 = np.array([])
            pct_spd80 = np.array([])
            pct_spd70 = np.array([])
            pct_spd50 = np.array([])
            pct_spd0 = np.array([])
            values.append([pct_spd100, pct_spd90, pct_spd80, pct_spd70, pct_spd50, pct_spd0])
        result = np.array(values)
        self.logger.info(f"Input Design Characteristics: {result.tolist()}")
        return result
    
    def stage_reference_params(self, lines: List[str]):
        idx = lines.index("STAGE REFERENCE PARAMETERS")
        # skip the first n_skip_lines
        n_skip_lines = 5
        n_params = 2
        result = np.genfromtxt(io.StringIO("\n".join(lines[idx + n_skip_lines : idx + n_params + n_skip_lines])))
        self.logger.info(f"Stage Reference Parameters: {result.tolist()}")
        return result
    
    def dpsis_table(self, lines: List[str]):
        idx = lines.index("DPSIS TABLE (STAGE, PCT SPD)")
        # skip the first n_skip_lines
        n_skip_lines = 5
        n_params = 2
        result = np.genfromtxt(io.StringIO("\n".join(lines[idx + n_skip_lines : idx + n_params + n_skip_lines])))
        self.logger.info(f"DPSIS Table: {result.tolist()}")
        return result
    
    def computed_characteristics(self, lines: List[str]):
        values = []
        for i in range(self.n_stages):
            idx = lines.index(f"COMPUTED CHARACTERISTICS - STAGE {i + 1}")
            # skip the first n_skip_lines
            n_skip_lines = 4
            n_params = 3
            # result = np.genfromtxt(io.StringIO("\n".join(lines[idx + n_skip_lines : idx + n_params + n_skip_lines])))
            pct_spd100 = np.array([])
            pct_spd90 = np.array([])
            pct_spd80 = np.array([])
            pct_spd70 = np.array([])
            pct_spd50 = np.array([])
            pct_spd0 = np.array([])
            values.append([pct_spd100, pct_spd90, pct_spd80, pct_spd70, pct_spd50, pct_spd0])
        result = np.array(values)
        self.logger.info(f"Computed Characteristics: {result.tolist()}")
        return result