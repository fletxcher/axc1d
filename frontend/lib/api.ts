/**
 * Thin client for the AXC1D FastAPI backend (`web/backend`).
 *
 * Base URL comes from `NEXT_PUBLIC_API_URL` (see `.env.example`); it falls back
 * to the FastAPI dev-server default so the app works with zero configuration
 * once `fastapi dev routes.py` is running.
 */

export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
).replace(/\/+$/, "")

export class ApiError extends Error {
  readonly status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
    })
  } catch {
    throw new ApiError(
      `Cannot reach the AXC1D API at ${API_BASE_URL}. ` +
        "Start it with:  cd web/backend && fastapi dev routes.py",
      0
    )
  }

  if (!res.ok) {
    throw new ApiError(await readErrorDetail(res), res.status)
  }
  return (await res.json()) as T
}

async function readErrorDetail(res: Response): Promise<string> {
  try {
    const body = await res.json()
    const detail = body?.detail
    if (typeof detail === "string") return detail
    if (Array.isArray(detail)) {
      // FastAPI 422 validation errors
      return detail
        .map((e) => {
          const loc = Array.isArray(e?.loc) ? e.loc.slice(1).join(".") : ""
          return loc ? `${loc}: ${e.msg}` : e.msg
        })
        .join("; ")
    }
  } catch {
    /* non-JSON body */
  }
  return `API error ${res.status}`
}

/** Resolves true when the backend answers `GET /api/health`. */
export function checkApiHealth(): Promise<boolean> {
  return apiFetch<{ status: string }>("/api/health")
    .then((r) => r.status === "ok")
    .catch(() => false)
}
