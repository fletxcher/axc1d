"use client"

import * as React from "react"
import { CheckIcon, CopyIcon, DownloadIcon } from "lucide-react"
import { toast } from "sonner"

import type { AnalysisResults } from "@/lib/analysis/types"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

type Format = "json" | "csv" | "txt"

const FORMATS: { id: Format; label: string; ext: string; mime: string }[] = [
  { id: "json", label: "JSON", ext: "json", mime: "application/json" },
  { id: "csv", label: "CSV", ext: "csv", mime: "text/csv" },
  { id: "txt", label: "Text", ext: "txt", mime: "text/plain" },
]

const PREVIEW_LIMIT = 20_000

export function ResultsExportDialog({ results }: { results: AnalysisResults }) {
  const [open, setOpen] = React.useState(false)
  const [format, setFormat] = React.useState<Format>("json")
  const [copied, setCopied] = React.useState(false)

  const content = React.useMemo(
    () => serialize(results, format),
    [results, format]
  )
  const truncated = content.length > PREVIEW_LIMIT
  const preview = truncated
    ? `${content.slice(0, PREVIEW_LIMIT)}\n\n… preview truncated — the download contains the full data.`
    : content

  const meta = FORMATS.find((f) => f.id === format)!

  function handleDownload() {
    const blob = new Blob([content], { type: `${meta.mime};charset=utf-8` })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `axc1d-results.${meta.ext}`
    a.click()
    URL.revokeObjectURL(url)
    toast.success(`Downloaded axc1d-results.${meta.ext}`)
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      toast.error("Clipboard unavailable")
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={<Button variant="outline" size="sm" />}
      >
        <DownloadIcon />
        Export
      </DialogTrigger>
      <DialogContent className="sm:max-w-[56rem]!">
        <DialogHeader>
          <DialogTitle>Export results</DialogTitle>
          <DialogDescription>
            Preview the sweep in each format, then download the file.
          </DialogDescription>
        </DialogHeader>

        <Tabs
          value={format}
          onValueChange={(v) => setFormat(v as Format)}
          className="gap-3"
        >
          <TabsList variant="line" className="w-full justify-start">
            {FORMATS.map((f) => (
              <TabsTrigger key={f.id} value={f.id}>
                {f.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>

        <pre className="bg-muted/40 tabular max-h-[38vh] overflow-auto rounded-lg border p-3 font-mono text-xs leading-relaxed whitespace-pre">
          {preview}
        </pre>

        <DialogFooter>
          <Button variant="outline" onClick={handleCopy}>
            {copied ? <CheckIcon /> : <CopyIcon />}
            {copied ? "Copied" : "Copy"}
          </Button>
          <Button onClick={handleDownload}>
            <DownloadIcon />
            Download
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function serialize(results: AnalysisResults, format: Format): string {
  if (format === "json") return JSON.stringify(results, null, 2)
  if (format === "csv") return toCsv(results)
  return toText(results)
}

function toCsv(results: AnalysisResults): string {
  const header = [
    "speed_fraction",
    "flow_point",
    "corrected_mass_flow",
    "overall_pressure_ratio",
    "overall_temperature_ratio",
    "overall_efficiency",
    "stalled",
  ]
  const rows = results.operatingPoints.map((p) =>
    [
      p.speedFraction,
      p.flowPointIndex + 1,
      p.correctedMassFlow,
      p.stalled ? "" : p.overallPressureRatio,
      p.stalled ? "" : p.overallTemperatureRatio,
      p.stalled ? "" : p.overallEfficiency,
      p.stalled ? 1 : 0,
    ].join(",")
  )
  return [header.join(","), ...rows].join("\n")
}

function toText(results: AnalysisResults): string {
  const d = results.design
  const pad = (s: string | number, n: number) => String(s).padStart(n)

  const lines: string[] = [
    "AXC1D results",
    `Generated : ${new Date(results.generatedAt).toLocaleString()}`,
    `Solver    : ${results.stub ? "placeholder (stub)" : "STGSTK"}`,
    `Runtime   : ${results.runtimeMs} ms`,
    "",
    "Design summary",
    `  Peak pressure ratio : ${d.pressureRatio.toFixed(3)}`,
    `  Peak efficiency     : ${(d.efficiency * 100).toFixed(1)} %`,
    `  Surge margin        : ${d.surgeMarginPct.toFixed(0)} %`,
    `  Stages              : ${d.stages}`,
    `  Speed lines         : ${results.speeds.length}`,
    "",
    "Operating points",
    [
      pad("N/N0", 6),
      pad("Pt", 4),
      pad("Corr.flow", 12),
      pad("PR", 9),
      pad("TR", 9),
      pad("eta", 8),
      "  Status",
    ].join(""),
  ]

  for (const p of results.operatingPoints) {
    lines.push(
      [
        pad(p.speedFraction.toFixed(2), 6),
        pad(p.flowPointIndex + 1, 4),
        pad(p.correctedMassFlow.toFixed(2), 12),
        pad(p.stalled ? "-" : p.overallPressureRatio.toFixed(3), 9),
        pad(p.stalled ? "-" : p.overallTemperatureRatio.toFixed(3), 9),
        pad(p.stalled ? "-" : (p.overallEfficiency * 100).toFixed(1), 8),
        p.stalled ? "  stall/choke" : "  converged",
      ].join("")
    )
  }

  return lines.join("\n")
}
