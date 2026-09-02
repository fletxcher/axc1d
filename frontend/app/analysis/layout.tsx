import { AppHeader } from "@/components/app-header"
import { Stepper, StepperMobile } from "@/components/analysis/stepper"
import { StepProgress } from "@/components/analysis/step-progress"

export default function AnalysisLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-full flex-col">
      <AppHeader center={<StepProgress />} />

      <div className="mx-auto flex w-full max-w-7xl flex-1 gap-8 px-4 py-6 sm:px-6 lg:py-10">
        <aside className="hidden w-60 shrink-0 lg:block">
          <div className="sticky top-20">
            <Stepper />
          </div>
        </aside>

        <main className="min-w-0 flex-1">
          <div className="mx-auto max-w-3xl lg:hidden">
            <StepperMobile />
          </div>
          <div className="mt-5 lg:mt-0">{children}</div>
        </main>
      </div>
    </div>
  )
}
