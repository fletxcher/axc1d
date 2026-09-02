import { cn } from "@/lib/utils"

/** Stylised axial-compressor rotor: three swept blades around a hub. */
export function BrandMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
      className={cn("size-6", className)}
    >
      <rect
        width="32"
        height="32"
        rx="8"
        className="fill-primary"
      />
      <g className="stroke-primary-foreground" strokeWidth="2" strokeLinecap="round">
        <path d="M16 16 L16 6 A10 10 0 0 1 24.66 11" fill="none" />
        <path d="M16 16 L24.66 21 A10 10 0 0 1 16 26" fill="none" />
        <path d="M16 16 L7.34 21 A10 10 0 0 1 7.34 11" fill="none" />
      </g>
      <circle cx="16" cy="16" r="2.5" className="fill-primary-foreground" />
    </svg>
  )
}
