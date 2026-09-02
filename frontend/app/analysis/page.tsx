import { redirect } from "next/navigation"

import { FIRST_STEP_SLUG } from "@/lib/analysis/steps"

export default function AnalysisIndex() {
  redirect(`/analysis/${FIRST_STEP_SLUG}`)
}
