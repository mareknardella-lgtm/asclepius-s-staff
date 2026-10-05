export interface Health { status: 'ok'; provider: 'mock' | 'openai'; model: string | null }
export interface Evidence { segment_id: string; quote: string }
export interface CareItem { id: string; instruction: string; evidence: Evidence[] }
export interface CarePlan {
  source_segments: { id: string; text: string }[]
  summary: string
  items: CareItem[]
  clarifications: { description: string; evidence: Evidence[] }[]
  questions_for_care_team: string[]
}
export type Origin = 'scripted_fixture' | 'local_rules' | 'model'
export interface Metadata {
  schema_version: 'care-v1'
  prompt_version: string
  request_id: string
  provider: 'mock' | 'openai'
  model: string | null
  is_mock: boolean
  origin: Origin
  elapsed_ms: number
}
export interface Analysis extends Metadata { result: CarePlan }
export interface TeachBack extends Metadata {
  result: { focus_id: string; status: 'matched' | 'needs_clarification' | 'unable_to_assess'; feedback: string; evidence: Evidence[] }
}
export type ItemState = 'read' | 'ask_care_team'
export interface TeachBackRecord { answer: string; response: TeachBack }
export interface HumanDecision { decision: 'accepted' | 'edited' | 'overridden'; note: string }
export type HumanReview = Record<string, HumanDecision>

export const normalizeSource = (text: string) => text.replace(/\r\n?/g, '\n').trim()
// Python counts Unicode code points, unlike JavaScript's UTF-16 string.length.
export const textLength = (text: string) => Array.from(text).length
function object(value: unknown): value is Record<string, unknown> { return typeof value === 'object' && value !== null && !Array.isArray(value) }
function string(value: unknown, max: number): value is string { return typeof value === 'string' && value.trim().length > 0 && textLength(value) <= max }
function list(value: unknown, max: number): value is unknown[] { return Array.isArray(value) && value.length <= max }
function metadata(value: Record<string, unknown>): boolean {
  return value.schema_version === 'care-v1' && string(value.prompt_version, 100) &&
    typeof value.request_id === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value.request_id) &&
    (value.provider === 'mock' || value.provider === 'openai') &&
    (value.model === null || string(value.model, 200)) && value.is_mock === (value.provider === 'mock') &&
    (value.origin === 'scripted_fixture' || value.origin === 'local_rules' || value.origin === 'model') &&
    (value.origin !== 'model') === value.is_mock &&
    typeof value.elapsed_ms === 'number' && Number.isInteger(value.elapsed_ms) && value.elapsed_ms >= 0
}
function evidence(value: unknown, segments: CarePlan['source_segments'], required: boolean): value is Evidence[] {
  return list(value, 3) && (!required || value.length > 0) && value.every(ref => object(ref) &&
    string(ref.segment_id, 40) && string(ref.quote, 4000) && segments.some(segment => segment.id === ref.segment_id && segment.text.includes(ref.quote as string)))
}
export function isAnalysis(value: unknown): value is Analysis {
  if (!object(value) || !metadata(value) || !object(value.result)) return false
  const result = value.result
  if (!list(result.source_segments, 80) || result.source_segments.length === 0 ||
      !result.source_segments.every((segment, index) => object(segment) && segment.id === `s${index + 1}` && string(segment.text, 4000))) return false
  const segments = result.source_segments as CarePlan['source_segments']
  return string(result.summary, 1200) && list(result.items, 6) &&
    result.items.every(item => object(item) && string(item.id, 40) && string(item.instruction, 600) && evidence(item.evidence, segments, true)) &&
    new Set(result.items.map(item => (item as CareItem).id)).size === result.items.length &&
    list(result.clarifications, 6) && result.clarifications.every(item => object(item) && string(item.description, 600) && evidence(item.evidence, segments, false)) &&
    list(result.questions_for_care_team, 3) && result.questions_for_care_team.every(question => string(question, 300))
}
function isTeachBack(value: unknown, plan: Analysis, focus: CareItem): value is TeachBack {
  if (!object(value) || !metadata(value) || !object(value.result)) return false
  const result = value.result
  return result.focus_id === focus.id && ['matched', 'needs_clarification', 'unable_to_assess'].includes(String(result.status)) &&
    string(result.feedback, 1000) && evidence(result.evidence, plan.result.source_segments, result.status !== 'unable_to_assess') &&
    result.evidence.every(ref => focus.evidence.some(selected => selected.segment_id === ref.segment_id && selected.quote.includes(ref.quote)))
}
async function request(path: string, init: RequestInit, timeoutMs: number): Promise<unknown> {
  try {
    const response = await fetch(`/api${path}`, { ...init, signal: AbortSignal.timeout(timeoutMs) })
    const body: unknown = await response.json().catch(() => null)
    if (!response.ok) {
      let message = response.status === 422 ? 'Check the text length, synthetic-data confirmation and selected source.' : `Request failed (HTTP ${response.status}).`
      if (object(body) && object(body.detail) && string(body.detail.message, 2000)) message = body.detail.message
      throw new Error(message)
    }
    return body
  } catch (error) {
    if (error instanceof DOMException && ['TimeoutError', 'AbortError'].includes(error.name)) throw new Error('The request timed out. Check the backend and try again.')
    if (error instanceof TypeError) throw new Error('Cannot reach the backend. Make sure it is running.')
    throw error
  }
}
export async function getHealth(): Promise<Health> {
  const data = await request('/health', {}, 5000)
  if (!object(data) || data.status !== 'ok' || !['mock', 'openai'].includes(String(data.provider)) || !(data.model === null || string(data.model, 200))) throw new Error('Invalid health response.')
  return data as unknown as Health
}
const post = (body: unknown): RequestInit => ({ method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
export async function analyze(text: string): Promise<Analysis> {
  const source = normalizeSource(text)
  const data = await request('/analyze', post({ text: source, synthetic_data_confirmed: true }), 135_000)
  if (!isAnalysis(data)) throw new Error('Invalid API result. No plan was accepted.')
  const lines = source.split('\n').filter(line => line.trim())
  if (lines.length !== data.result.source_segments.length || lines.some((line, index) => line !== data.result.source_segments[index].text)) throw new Error('The returned source does not match your instructions.')
  return data
}
export async function teachBack(text: string, plan: Analysis, focus: CareItem, answer: string): Promise<TeachBack> {
  const data = await request('/teach-back', post({ text: normalizeSource(text), synthetic_data_confirmed: true, focus: { id: focus.id, evidence: focus.evidence }, answer: answer.trim() }), 135_000)
  if (!isTeachBack(data, plan, focus)) throw new Error('Invalid source-grounded feedback. No assessment was accepted.')
  return data
}
export function buildExport(text: string, plan: Analysis, record: TeachBackRecord | null, itemStates: Record<string, ItemState>, reviewedAt = new Date().toISOString(), humanReview: HumanReview = {}) {
  return {
    schema_version: 'care-export-v1', source_text: normalizeSource(text), synthetic_data_confirmed: true,
    plan, teach_back: record,
    review: { confirmed: true, reviewed_at: reviewedAt, item_states: plan.result.items.filter(item => itemStates[item.id]).map(item => ({ id: item.id, state: itemStates[item.id] })) },
    human_review: Object.fromEntries(Object.entries(humanReview).filter(([key]) =>
      plan.result.items.some(item => key === `step:${item.id}`) ||
      plan.result.clarifications.some((_, index) => key === `clarification:${index}`) ||
      plan.result.questions_for_care_team.some((_, index) => key === `question:${index}`) ||
      (key === 'feedback' && record !== null))),
    limitations: ['Synthetic demonstration only; not medical advice or clinically validated.', 'Source citations establish text provenance, not medical truth.', 'Teach-back estimates text correspondence, not comprehension or safety.', 'Mock results are scripted fixtures, not real AI assessments.', 'No appointment, treatment or external action was performed.'],
  }
}
export function exportAnalysis(text: string, plan: Analysis, record: TeachBackRecord | null, itemStates: Record<string, ItemState>, humanReview: HumanReview = {}): void {
  const blob = new Blob([JSON.stringify(buildExport(text, plan, record, itemStates, new Date().toISOString(), humanReview), null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `asclepius-${plan.request_id}.json`
  document.body.appendChild(link)
  try { link.click() } finally { link.remove(); window.setTimeout(() => URL.revokeObjectURL(url), 1000) }
}
