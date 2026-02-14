#ifndef SOLVER_H
#define SOLVER_H

#include <QString>

/**
 * AXC1D Multistage compressor analysis and performance calculation solver
 */
class AXC1DSolver {
public:
    explicit AXC1DSolver();
    ~AXC1DSolver();

    /**
     * Read and process input data for compressor analysis
     */
    void csinpt();

    /**
     * Calculate compressor meanline flow parameters
     */
    void cml();

    /**
     * Calculate meanline velocity diagrams and design stage performance
     */
    void csref();

    /**
     * Calculate specific heat and gamma as functions of temperature
     */
    void cpf();

    /**
     * Generate stage adiabatic efficiency curve vs. flow coefficient
     */
    void cseta();

    /**
     * Generate stage pressure coefficient curve vs. flow coefficient
     */
    void cspsi();

    /**
     * Adjust pressure coefficient for off-design rotative speeds
     */
    void cspsd();

    /**
     * Calculate and output stage and cumulative compressor performance
     */
    void csoupt();

    /**
     * Alter stage characteristics for blade setting angle changes
     */
    void cspan();

    /**
     * Execute the compressor analysis logic
     */
    void run();
};

#endif // SOLVER_H
