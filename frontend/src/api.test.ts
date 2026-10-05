import { describe, expect, it, vi } from 'vitest'
import { analyze, buildExport, exportAnalysis, getHealth, isAnalysis, normalizeSource, teachBack, textLength } from './api'
import { comparison, response, source } from './test-fixtures'

const fetched = (data: unknown) => vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(data))))
describe('Healthcare API client', () => {
  it('validates metadata and grounded plan, rejecting invalid evidence', () => {
    expect(isAnalysis(response)).toBe(true)
    expect(isAnalysis({ ...response, is_mock: false })).toBe(false)
    expect(isAnalysis({ ...response, schema_version: 'old' })).toBe(false)
    expect(isAnalysis({ ...response, request_id: 'not-a-uuid' })).toBe(false)
    expect(isAnalysis({ ...response, result: { ...response.result, items: [{ ...response.result.items[0], evidence: [{ segment_id: 's1', quote: 'invented' }] }] } })).toBe(false)
    expect(isAnalysis({})).toBe(false)
  })
  it('normalizes CRLF and counts code points like the backend', () => {
    expect(normalizeSource('  hello\r\nworld\r ')).toBe('hello\nworld')
    expect(textLength('📄')).toBe(1)
  })
  it('posts consent and checks source correspondence', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(response)))
    vi.stubGlobal('fetch', fetchMock)
    expect(await analyze(`  ${source.replace(/\n/g, '\r\n')}  `)).toEqual(response)
    expect(fetchMock.mock.calls[0][0]).toBe('/api/analyze')
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ text: source, synthetic_data_confirmed: true })
    fetched(response)
    await expect(analyze('Different synthetic instructions.')).rejects.toThrow('does not match')
  })
  it('sends source and focus, not generated instruction as truth', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(comparison)))
    vi.stubGlobal('fetch', fetchMock)
    expect(await teachBack(source, response, response.result.items[0], ' my answer ')).toEqual(comparison)
    const body = JSON.parse(fetchMock.mock.calls[0][1].body)
    expect(body).toEqual({ text: source, synthetic_data_confirmed: true, focus: { id: 'step-1', evidence: response.result.items[0].evidence }, answer: 'my answer' })
    expect(body.focus.instruction).toBeUndefined()
  })
  it('rejects invalid or unrelated teach-back output', async () => {
    fetched({ ...comparison, result: { ...comparison.result, focus_id: 'forged' } })
    await expect(teachBack(source, response, response.result.items[0], 'answer')).rejects.toThrow('Invalid source-grounded feedback')
    fetched({ ...comparison, result: { ...comparison.result, evidence: [] } })
    await expect(teachBack(source, response, response.result.items[0], 'answer')).rejects.toThrow('Invalid source-grounded feedback')
  })
  it('rejects malformed successful JSON and backend errors', async () => {
    fetched({})
    await expect(analyze(source)).rejects.toThrow('Invalid API result')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: { code: 'provider_timeout', message: 'The provider did not respond in time.' } }), { status: 504 })))
    await expect(analyze(source)).rejects.toThrow('did not respond in time')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: [] }), { status: 422 })))
    await expect(analyze('short')).rejects.toThrow('Check the text length')
  })
  it('handles network failure, timeout and invalid health', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    await expect(getHealth()).rejects.toThrow('Cannot reach the backend')
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new DOMException('timeout', 'TimeoutError')))
    await expect(getHealth()).rejects.toThrow('timed out')
    fetched({ status: 'ok', provider: 'unknown', model: null })
    await expect(getHealth()).rejects.toThrow('Invalid health')
  })
  it('builds an export preserving source, feedback and human review', () => {
    const file = buildExport(source, response, { answer: 'my answer', response: comparison }, { 'step-1': 'ask_care_team', forged: 'read' }, '2026-10-04T12:00:00.000Z')
    expect(file.schema_version).toBe('care-export-v1')
    expect(file.source_text).toBe(source)
    expect(file.plan.is_mock).toBe(true)
    expect(file.teach_back?.answer).toBe('my answer')
    expect(file.review).toEqual({ confirmed: true, reviewed_at: '2026-10-04T12:00:00.000Z', item_states: [{ id: 'step-1', state: 'ask_care_team' }] })
    expect(file.limitations.join(' ')).toContain('not medical advice')
  })
  it('preserves human overrides separately and removes stale or unknown decisions', () => {
    const file = buildExport(source, response, null, {}, '2026-10-04T12:00:00Z', {
      'step:step-1': { decision: 'edited', note: 'My wording' },
      'clarification:0': { decision: 'overridden', note: 'Ask separately' },
      feedback: { decision: 'accepted', note: '' },
      forged: { decision: 'accepted', note: '' },
    })
    expect(file.human_review).toEqual({ 'step:step-1': { decision: 'edited', note: 'My wording' }, 'clarification:0': { decision: 'overridden', note: 'Ask separately' } })
    expect(file.plan.result.items[0].instruction).toBe(response.result.items[0].instruction)
    expect(file.plan.result.items[0].evidence).toEqual(response.result.items[0].evidence)
  })
  it('downloads the exact JSON blob and intended filename', async () => {
    let blob: Blob | undefined
    const createObjectURL = vi.fn((value: Blob) => { blob = value; return 'blob:fixture' })
    vi.stubGlobal('URL', { createObjectURL, revokeObjectURL: vi.fn() })
    let filename = ''
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (this: HTMLAnchorElement) { filename = this.download })
    exportAnalysis(source, response, null, { 'step-1': 'read' })
    expect(filename).toBe(`asclepius-${response.request_id}.json`)
    expect(blob?.type).toBe('application/json')
    const content = await new Promise<string>((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(String(reader.result)); reader.onerror = reject; reader.readAsText(blob!); })
    expect(JSON.parse(content).plan.result.items[0].evidence).toEqual(response.result.items[0].evidence)
    expect(JSON.parse(content).source_text).toBe(source)
    expect(document.querySelector('a[download]')).toBeNull()
  })
})
