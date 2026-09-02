"use client"

import * as React from "react"

import { defaultConfig, normalizeConfig } from "./defaults"
import { runAnalysis } from "./solver"
import { STEPS } from "./steps"
import type { AnalysisConfig, AnalysisResults } from "./types"

const CONFIG_KEY = "axc1d.config.v1"
const RESULTS_KEY = "axc1d.results.v1"

type RunStatus = "idle" | "running" | "done" | "error"

interface AnalysisContextValue {
  config: AnalysisConfig
  /** Replace the config through an updater; array sections are re-shaped automatically. */
  updateConfig: (recipe: (draft: AnalysisConfig) => AnalysisConfig) => void
  resetConfig: () => void
  hydrated: boolean

  results: AnalysisResults | null
  runStatus: RunStatus
  runError: string | null
  run: () => Promise<void>
  clearResults: () => void

  /** slug → null when the step validates, else a short reason. */
  stepIssues: Record<string, string | null>
  firstInvalidSlug: string | null
}

const AnalysisContext = React.createContext<AnalysisContextValue | null>(null)

export function AnalysisProvider({ children }: { children: React.ReactNode }) {
  const [config, setConfig] = React.useState<AnalysisConfig>(() =>
    normalizeConfig(defaultConfig())
  )
  const [results, setResults] = React.useState<AnalysisResults | null>(null)
  const [runStatus, setRunStatus] = React.useState<RunStatus>("idle")
  const [runError, setRunError] = React.useState<string | null>(null)
  const [hydrated, setHydrated] = React.useState(false)

  // Hydrate from localStorage after mount to avoid SSR mismatch.
  React.useEffect(() => {
    try {
      const rawConfig = window.localStorage.getItem(CONFIG_KEY)
      if (rawConfig) {
        setConfig(normalizeConfig(JSON.parse(rawConfig) as AnalysisConfig))
      }
      const rawResults = window.localStorage.getItem(RESULTS_KEY)
      if (rawResults) {
        setResults(JSON.parse(rawResults) as AnalysisResults)
        setRunStatus("done")
      }
    } catch {
      // ignore malformed storage
    }
    setHydrated(true)
  }, [])

  React.useEffect(() => {
    if (!hydrated) return
    try {
      window.localStorage.setItem(CONFIG_KEY, JSON.stringify(config))
    } catch {
      /* quota / private mode */
    }
  }, [config, hydrated])

  React.useEffect(() => {
    if (!hydrated) return
    try {
      if (results) window.localStorage.setItem(RESULTS_KEY, JSON.stringify(results))
      else window.localStorage.removeItem(RESULTS_KEY)
    } catch {
      /* quota / private mode */
    }
  }, [results, hydrated])

  const updateConfig = React.useCallback(
    (recipe: (draft: AnalysisConfig) => AnalysisConfig) => {
      setConfig((prev) => normalizeConfig(recipe(prev)))
    },
    []
  )

  const resetConfig = React.useCallback(() => {
    setConfig(normalizeConfig(defaultConfig()))
    setResults(null)
    setRunStatus("idle")
    setRunError(null)
  }, [])

  const clearResults = React.useCallback(() => {
    setResults(null)
    setRunStatus("idle")
    setRunError(null)
  }, [])

  const run = React.useCallback(async () => {
    setRunStatus("running")
    setRunError(null)
    try {
      const next = await runAnalysis(config)
      setResults(next)
      setRunStatus("done")
    } catch (err) {
      const message = err instanceof Error ? err.message : "Solver failed."
      setRunError(message)
      setRunStatus("error")
      throw err // let callers (toast.promise, navigation) see the failure
    }
  }, [config])

  const stepIssues = React.useMemo(() => {
    const map: Record<string, string | null> = {}
    for (const step of STEPS) map[step.slug] = step.validate(config)
    return map
  }, [config])

  const firstInvalidSlug = React.useMemo(
    () => STEPS.find((s) => stepIssues[s.slug])?.slug ?? null,
    [stepIssues]
  )

  const value: AnalysisContextValue = {
    config,
    updateConfig,
    resetConfig,
    hydrated,
    results,
    runStatus,
    runError,
    run,
    clearResults,
    stepIssues,
    firstInvalidSlug,
  }

  return (
    <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>
  )
}

export function useAnalysis(): AnalysisContextValue {
  const ctx = React.useContext(AnalysisContext)
  if (!ctx) throw new Error("useAnalysis must be used within <AnalysisProvider>")
  return ctx
}
