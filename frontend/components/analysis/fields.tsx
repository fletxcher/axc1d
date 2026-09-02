"use client"

import * as React from "react"

import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

/** Controlled numeric input that lets the user type freely and commits a number. */
export function NumberInput({
  value,
  onCommit,
  className,
  suffix,
  ...props
}: Omit<
  React.ComponentProps<"input">,
  "value" | "onChange" | "type"
> & {
  value: number
  onCommit: (next: number) => void
  suffix?: string
}) {
  const [draft, setDraft] = React.useState(() => formatNumber(value))
  const [focused, setFocused] = React.useState(false)

  React.useEffect(() => {
    if (!focused) setDraft(formatNumber(value))
  }, [value, focused])

  return (
    <div className="relative">
      <Input
        {...props}
        type="text"
        inputMode="decimal"
        value={draft}
        className={cn(suffix && "pr-10", "tabular", className)}
        onFocus={(e) => {
          setFocused(true)
          props.onFocus?.(e)
        }}
        onChange={(e) => {
          const raw = e.target.value
          setDraft(raw)
          const parsed = Number(raw)
          if (raw.trim() !== "" && Number.isFinite(parsed)) onCommit(parsed)
        }}
        onBlur={(e) => {
          setFocused(false)
          const parsed = Number(draft)
          if (draft.trim() === "" || !Number.isFinite(parsed)) {
            setDraft(formatNumber(value))
          } else {
            onCommit(parsed)
            setDraft(formatNumber(parsed))
          }
          props.onBlur?.(e)
        }}
      />
      {suffix && (
        <span className="text-muted-foreground pointer-events-none absolute inset-y-0 right-2.5 flex items-center text-xs">
          {suffix}
        </span>
      )}
    </div>
  )
}

/** Label + control + optional hint, stacked. */
export function FieldBlock({
  label,
  htmlFor,
  hint,
  className,
  children,
}: {
  label: string
  htmlFor?: string
  hint?: string
  className?: string
  children: React.ReactNode
}) {
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
      {hint && <p className="text-muted-foreground text-xs">{hint}</p>}
    </div>
  )
}

export function FieldGrid({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        "grid gap-x-5 gap-y-4 sm:grid-cols-2 lg:grid-cols-3",
        className
      )}
    >
      {children}
    </div>
  )
}

function formatNumber(n: number): string {
  if (!Number.isFinite(n)) return ""
  // keep it compact but preserve small coefficients in exponent form
  if (n !== 0 && (Math.abs(n) < 1e-4 || Math.abs(n) >= 1e7)) {
    return n.toExponential(5)
  }
  return String(n)
}
