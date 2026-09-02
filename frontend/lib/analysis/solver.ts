import { apiFetch } from "@/lib/api"

import type { AnalysisConfig, AnalysisResults } from "./types"

/**
 * Runs the full 1D meanline stage-stacking sweep on the AXC1D backend
 * (`POST /api/solve`). The Python solver in `web/backend/services.py` - a port
 * of `desktop/src/python/solver.py` - is the source of truth.
 *
 * Request body is the `AnalysisConfig`; the response is `AnalysisResults`.
 */
export async function runAnalysis(
  config: AnalysisConfig
): Promise<AnalysisResults> {
  return apiFetch<AnalysisResults>("/api/solve", {
    method: "POST",
    body: JSON.stringify(config),
  })
}
