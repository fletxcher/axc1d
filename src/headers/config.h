#ifndef CONFIG_H
#define CONFIG_H

#include <QString>

/**
 * Constant configuration parameters for AXC1D analysis
 */
struct ConstantConfig {
    QString analysis_type;
    float n_stages;
    QString units;
    float verbosity;
};

/**
 * Inlet flow conditions
 */
struct InletConfig {
    float inlet_pressure;
    float inlet_temperature;
    float mass_flow;
    float swirl_angle;
    float mach_number;
};

/**
 * Gas thermodynamic properties
 */
struct GasPropertiesConfig {
    float gamma;
    float r;
};

/**
 * Rotor rotation configuration
 */
struct RotationConfig {
    float rpm;
    QString direction;
};

/**
 * Stage characteristics including curves and coefficients
 */
struct StageCharacteristicsConfig {
    float stage_pressure_coefficient_curve;
    float stage_efficiency_curve;
    float flow_coefficient_range;
    float blade_deviation_adjustment;
    float inlet_guide_vane_angle;
};

/**
 * Solver numerical configuration
 */
struct SolverConfig {
    float max_iters;
    float convergence_tolerance;
    float numerical_damping;
};

/**
 * Output configuration for results
 */
struct OutputConfig {
    float efficiency;
    float format;
};

/**
 * Main configuration class for AXC1D application
 */
class AXC1DConfig {
public:
    AXC1DConfig();
    ~AXC1DConfig();

    bool read(const QString& filename);
    bool save(const QString& filename);

    ConstantConfig constant;
    InletConfig inlet;
    GasPropertiesConfig gas_properties;
    RotationConfig rotation;
    StageCharacteristicsConfig stage_characteristics;
    SolverConfig solver;
    OutputConfig output;

private:
    QString configTemplate() const;
};

#endif // CONFIG_H
