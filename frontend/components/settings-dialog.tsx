"use client"

import * as React from "react"
import { Settings2Icon } from "lucide-react"

import { SITE } from "@/lib/site"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Separator } from "@/components/ui/separator"
import { ThemeSegmented } from "@/components/theme-toggle"

export function SettingsDialog() {
  const [open, setOpen] = React.useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={<Button variant="ghost" size="icon" aria-label="Settings" />}
      >
        <Settings2Icon />
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
          <DialogDescription>
            Preferences and workspace actions for this browser.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-5 py-1">
          <Row label="Appearance" hint="Theme for this device.">
            <ThemeSegmented />
          </Row>

          <Separator />

          <div className="text-muted-foreground space-y-1 text-xs">
            <p className="text-foreground font-medium">About {SITE.name}</p>
            <p>{SITE.description}</p>
            <p>Methodology: {SITE.paperTitle}</p>
            <p>
              <a
                href={SITE.repoUrl}
                target="_blank"
                rel="noreferrer"
                className="underline underline-offset-3 hover:text-foreground"
              >
                Source repository
              </a>
            </p>
          </div>
        </div>

        <DialogClose render={<Button variant="outline" size="sm" />}>
          Done
        </DialogClose>
      </DialogContent>
    </Dialog>
  )
}

function Row({
  label,
  hint,
  children,
}: {
  label: string
  hint: string
  children: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-2">
      <div>
        <p className="text-sm font-medium">{label}</p>
        <p className="text-muted-foreground text-xs">{hint}</p>
      </div>
      {children}
    </div>
  )
}
