"use client"

import * as React from "react"
import Link from "next/link"
import { ArrowLeftIcon, ArrowRightIcon } from "lucide-react"

import { STEPS, stepIndex } from "@/lib/analysis/steps"
import { Button } from "@/components/ui/button"

export function StepShell({
  slug,
  children,
  footer,
}: {
  slug: string
  children: React.ReactNode
  /** Replace the default Previous / Next footer. */
  footer?: React.ReactNode
}) {
  const index = stepIndex(slug)
  const step = STEPS[index]
  const prev = index > 0 ? STEPS[index - 1] : null
  const next = index < STEPS.length - 1 ? STEPS[index + 1] : null
  const Icon = step.icon

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
      <div className="flex items-start gap-3">
        <span className="border-primary/25 bg-primary/10 text-primary mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg border">
          <Icon className="size-[18px]" />
        </span>
        <div className="min-w-0">
          <h1 className="font-heading text-xl font-semibold tracking-tight">
            {step.title}
          </h1>
          <p className="text-muted-foreground mt-0.5 text-sm">{step.summary}</p>
        </div>
      </div>

      <div>{children}</div>

      {footer ?? (
        <div className="flex items-center justify-between gap-3 border-t pt-4">
          {prev ? (
            <Button
              variant="ghost"
              size="sm"
              render={<Link href={`/analysis/${prev.slug}`} />}
            >
              <ArrowLeftIcon />
              {prev.title}
            </Button>
          ) : (
            <Button variant="ghost" size="sm" render={<Link href="/" />}>
              <ArrowLeftIcon />
              Overview
            </Button>
          )}

          {next && (
            <Button
              variant="ghost"
              size="sm"
              render={<Link href={`/analysis/${next.slug}`} />}
            >
              {next.title}
              <ArrowRightIcon />
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
