"use client"

import type { ReactNode } from "react"
import { usePathname } from "next/navigation"

import { STEPS } from "@/lib/analysis/steps"

/** Current section label shown in the app header. */
export function StepProgress() {
  const pathname = usePathname()

  if (pathname.startsWith("/analysis/results")) {
    return <HeaderLabel text="Results" />
  }

  const step = STEPS.find((s) => pathname.startsWith(`/analysis/${s.slug}`))
  if (!step) return null

  const Icon = step.icon
  return (
    <HeaderLabel text={step.title}>
      <Icon className="size-3.5" />
    </HeaderLabel>
  )
}

function HeaderLabel({
  text,
  children,
}: {
  text: string
  children?: ReactNode
}) {
  return (
    <div className="text-muted-foreground flex items-center gap-1.5 text-xs font-medium">
      {children}
      {text}
    </div>
  )
}
