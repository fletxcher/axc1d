import * as React from "react"
import Link from "next/link"

import { SITE } from "@/lib/site"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { BrandMark } from "@/components/brand-mark"
import { GitHubIcon } from "@/components/icons"
import { ThemeToggle } from "@/components/theme-toggle"
import { SettingsDialog } from "@/components/settings-dialog"

export function AppHeader({
  center,
  className,
}: {
  center?: React.ReactNode
  className?: string
}) {
  return (
    <header
      className={cn(
        "bg-background/80 sticky top-0 z-40 border-b backdrop-blur-sm",
        className
      )}
    >
      <div className="mx-auto flex h-14 w-full max-w-7xl items-center gap-4 px-4 sm:px-6">
        <Link
          href="/"
          className="flex shrink-0 items-center gap-2 font-medium tracking-tight"
        >
          <BrandMark />
          <span className="text-sm">{SITE.name}</span>
        </Link>

        {center ? (
          <div className="hidden flex-1 justify-center md:flex">{center}</div>
        ) : (
          <div className="flex-1" />
        )}

        <div className="flex shrink-0 items-center gap-0.5">
          <Button
            variant="ghost"
            size="icon"
            aria-label="GitHub account"
            render={
              <a href={SITE.githubUrl} target="_blank" rel="noreferrer" />
            }
          >
            <GitHubIcon className="size-4" />
          </Button>
          <ThemeToggle />
          <SettingsDialog />
        </div>
      </div>
      {center ? (
        <div className="border-t px-4 py-2 md:hidden">{center}</div>
      ) : null}
    </header>
  )
}
