#include "../headers/config.h"
#include <QFile>
#include <QTextStream>

AXC1DConfig::AXC1DConfig() {
    // Initialize with default values
    constant.analysis_type = "compressor";
    constant.n_stages = 1.0f;
    constant.units = "SI";
    constant.verbosity = 1.0f;

    inlet.inlet_pressure = 101325.0f;
    inlet.inlet_temperature = 288.15f;
    inlet.mass_flow = 100.0f;
    inlet.swirl_angle = 0.0f;
    inlet.mach_number = 0.5f;

    gas_properties.gamma = 1.4f;
    gas_properties.r = 287.0f;

    rotation.rpm = 10000.0f;
    rotation.direction = "CW";

    stage_characteristics.stage_pressure_coefficient_curve = 0.5f;
    stage_characteristics.stage_efficiency_curve = 0.85f;
    stage_characteristics.flow_coefficient_range = 0.05f;
    stage_characteristics.blade_deviation_adjustment = 2.0f;
    stage_characteristics.inlet_guide_vane_angle = 0.0f;

    solver.max_iters = 100.0f;
    solver.convergence_tolerance = 1e-5f;
    solver.numerical_damping = 0.5f;

    output.efficiency = 0.85f;
    output.format = 0.0f;
}

AXC1DConfig::~AXC1DConfig() {
}

QString AXC1DConfig::configTemplate() const {
    return QString(
        "=============== AXC1D MULTISTAGE ANALYSIS TOOL ===============\n"
        "[CONSTANT]\n"
        "- analysis_type: \n"
        "- n_stages: \n"
        "- units: \n"
        "- verbosity: \n"
        "\n"
        "[INLET]\n"
        "- total_pressure: \n"
        "- total_temperature: \n"
        "- mass_flow: \n"
        "- swirl_angle: \n"
        "- mach_number: \n"
        "\n"
        "[GAS PROPERTIES]\n"
        "- gamma: \n"
        "- r: \n"
        "\n"
        "[ROTATION]\n"
        "- rpm: \n"
        "- direction: \n"
        "\n"
        "[STAGE CHARACTERISTICS]\n"
        "- stage_pressure_coefficient_curve: \n"
        "- stage_efficiency_curve: \n"
        "- flow_coefficient_range: \n"
        "- blade_deviation_adjustment: \n"
        "- inlet_guide_vane_angle: \n"
        "\n"
        "[SOLVER]\n"
        "- max_iters: \n"
        "- convergence_tolerance: \n"
        "- numerical_damping: \n"
        "\n"
        "[OUTPUT]\n"
        "- efficiency: \n"
        "- format: \n"
    );
}

bool AXC1DConfig::read(const QString& filename) {
    QFile file(filename);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return false;
    }

    QTextStream in(&file);
    while (!in.atEnd()) {
        QString line = in.readLine();
        // Parse configuration file
        // This is a simplified parser; a full implementation would
        // properly parse INI-like format
    }

    file.close();
    return true;
}

bool AXC1DConfig::save(const QString& filename) {
    QFile file(filename);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        return false;
    }

    QTextStream out(&file);
    out << configTemplate();
    file.close();
    return true;
}
