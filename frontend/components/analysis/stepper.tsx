"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { CheckIcon, ChartLineIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { STEPS } from "@/lib/analysis/steps"
import { useAnalysis } from "@/lib/analysis/store"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

function useNavState() {
  const pathname = usePathname()
  const { stepIssues, results } = useAnalysis()
  const currentSlug =
    STEPS.find((s) => pathname.startsWith(`/analysis/${s.slug}`))?.slug ??
    (pathname.startsWith("/analysis/results") ? "results" : STEPS[0].slug)
  return { stepIssues, results, currentSlug }
}

/** Persistent left-hand section menu. Every step is reachable at any time. */
export function Stepper() {
  const { stepIssues, results, currentSlug } = useNavState()

  return (
    <nav aria-label="Configuration sections" className="flex flex-col gap-0.5">
      <p className="text-muted-foreground mb-1 px-2.5 text-xs font-medium tracking-wide uppercase">
        Configuration
      </p>

      {STEPS.map((step) => {
        const active = step.slug === currentSlug
        const issue = stepIssues[step.slug]
        const Icon = step.icon

        return (
          <Link
            key={step.id}
            href={`/analysis/${step.slug}`}
            aria-current={active ? "page" : undefined}
            className={cn(
              "group relative flex items-center gap-2.5 rounded-md py-2 pr-2 pl-3.5 text-sm transition-colors",
              active
                ? "bg-accent text-foreground font-medium"
                : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
            )}
          >
            {active && (
              <span className="bg-primary absolute inset-y-1.5 left-0 w-0.5 rounded-full" />
            )}
            <Icon className="size-4 shrink-0" />
            <span className="flex-1 truncate">{step.title}</span>
            <StatusDot issue={issue} />
          </Link>
        )
      })}

      <SelectSeparatorLine />

      <Link
        href="/analysis/results"
        aria-disabled={!results}
        className={cn(
          "relative flex items-center gap-2.5 rounded-md py-2 pr-2 pl-3.5 text-sm transition-colors",
          currentSlug === "results"
            ? "bg-accent text-foreground font-medium"
            : results
              ? "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
              : "text-muted-foreground/40 pointer-events-none"
        )}
      >
        {currentSlug === "results" && (
          <span className="bg-primary absolute inset-y-1.5 left-0 w-0.5 rounded-full" />
        )}
        <ChartLineIcon className="size-4 shrink-0" />
        <span className="flex-1 truncate">Results</span>
      </Link>
    </nav>
  )
}

/** Compact section switcher for narrow screens. */
export function StepperMobile() {
  const router = useRouter()
  const { results, currentSlug } = useNavState()

  return (
    <Select
      value={currentSlug}
      onValueChange={(v) => router.push(`/analysis/${v}`)}
    >
      <SelectTrigger className="w-full">
        <SelectValue>
          {(v) =>
            v === "results"
              ? "Results"
              : (STEPS.find((s) => s.slug === v)?.title ?? "Jump to section")
          }
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {STEPS.map((step) => (
          <SelectItem key={step.id} value={step.slug}>
            {step.title}
          </SelectItem>
        ))}
        <SelectSeparator />
        <SelectItem value="results" disabled={!results}>
          Results
        </SelectItem>
      </SelectContent>
    </Select>
  )
}

function StatusDot({ issue }: { issue: string | null }) {
  if (issue) {
    return (
      <span
        title={issue}
        aria-label="Needs attention"
        className="bg-destructive/70 size-1.5 shrink-0 rounded-full"
      />
    )
  }
  return (
    <CheckIcon
      aria-label="Complete"
      className="text-muted-foreground/50 size-3.5 shrink-0"
    />
  )
}

function SelectSeparatorLine() {
  return <div className="bg-border mx-2.5 my-1.5 h-px" />
}
