import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { analyze, exportAnalysis, getHealth, teachBack } from './api'
import type { Analysis } from './api'
import { comparison, response, rulesResponse, source } from './test-fixtures'

vi.mock('./api', async importOriginal => ({ ...await importOriginal<typeof import('./api')>(), analyze: vi.fn(), exportAnalysis: vi.fn(), getHealth: vi.fn(), teachBack: vi.fn() }))
beforeEach(() => {
  vi.mocked(getHealth).mockResolvedValue({ status: 'ok', provider: 'mock', model: null })
  vi.mocked(analyze).mockResolvedValue(response)
  vi.mocked(teachBack).mockResolvedValue(comparison)
  vi.mocked(exportAnalysis).mockReset()
})
const consent = { name: /This is practice text/ }
const planButton = { name: /Show me my steps/ }
const compareButton = { name: /Check what I said/ }
async function createPlan(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole('checkbox', consent))
  await user.click(screen.getByRole('button', planButton))
  await screen.findByText(/Written by a prepared demo example/)
}
async function reviewScreen(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole('button', { name: /^Check it and save$/ }))
  expect(screen.getByRole('heading', { level: 1 })).toHaveFocus()
}
async function acceptAll(user: ReturnType<typeof userEvent.setup>) {
  for (const button of screen.getAllByRole('button', { name: /^Accept / })) await user.click(button)
}
describe('Editorial patient journey', () => {
  it('starts with a labeled fictional record and requires consent again after editing', async () => {
    const user = userEvent.setup(); render(<App />)
    expect(screen.getByRole('heading', { name: 'Amira Patel' })).toBeInTheDocument()
    const submit = screen.getByRole('button', planButton)
    expect(submit).toBeDisabled()
    await user.click(screen.getByRole('checkbox', consent))
    expect(submit).toBeEnabled()
    await user.click(screen.getByRole('button', { name: 'Edit the note' }))
    await user.type(screen.getByLabelText('Your discharge instructions'), ' changed')
    expect(submit).toBeDisabled()
    expect(screen.queryByRole('heading', { name: 'Amira Patel' })).not.toBeInTheDocument()
  })
  it('creates cited steps, compares an explanation and requires a decision for every suggestion before export', async () => {
    const user = userEvent.setup(); render(<App />); await createPlan(user)
    expect(analyze).toHaveBeenCalledWith(source)
    expect(screen.getByRole('link', { name: /Source S4 · Original wording/ })).toHaveAttribute('href', '#source-s4')
    await user.click(screen.getByRole('button', { name: 'Example that misses something' }))
    await user.click(screen.getByRole('button', compareButton))
    expect(await screen.findByText('One part needs a closer look')).toBeInTheDocument()
    await reviewScreen(user)
    const download = screen.getByRole('button', { name: /Download my copy/ })
    const confirmation = screen.getByRole('checkbox', { name: /I have read the note/ })
    expect(download).toBeDisabled(); expect(confirmation).toBeDisabled()
    await acceptAll(user)
    await user.selectOptions(screen.getByLabelText('Your review of step 1'), 'ask_care_team')
    await user.click(confirmation); await user.click(download)
    expect(exportAnalysis).toHaveBeenCalledWith(source, response, expect.objectContaining({ response: comparison }), { 'step-1': 'ask_care_team' }, expect.objectContaining({ 'step:step-1': { decision: 'accepted', note: '' }, feedback: { decision: 'accepted', note: '' } }))
    expect(screen.getByText(/Download started/)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Back to my steps' }))
    await user.type(screen.getByLabelText('In your own words'), ' changed')
    expect(screen.queryByText('One part needs a closer look')).not.toBeInTheDocument()
    await reviewScreen(user)
    expect(screen.getByRole('button', { name: /Download my copy/ })).toBeDisabled()
  })
  it('allows human edits and overrides without changing AI evidence and exports separate decisions', async () => {
    const user = userEvent.setup(); render(<App />); await createPlan(user); await reviewScreen(user)
    await user.click(screen.getByRole('button', { name: 'Edit step 1' }))
    const editor = screen.getByLabelText('Your wording · step 1')
    await user.clear(editor); await user.type(editor, 'My own reminder to discuss at the visit.')
    await user.click(screen.getByRole('button', { name: 'Save your wording' }))
    expect(screen.getByText('My own reminder to discuss at the visit.')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: response.result.items[0].instruction })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Override limitation 1' }))
    await user.type(screen.getByLabelText('Why you are setting this aside · limitation 1'), 'I will confirm this separately.')
    await user.click(screen.getByRole('button', { name: 'Save your reason' }))
    await user.click(screen.getByRole('button', { name: 'Accept question 1' }))
    await user.click(screen.getByRole('checkbox', { name: /I have read the note/ }))
    await user.click(screen.getByRole('button', { name: /Download my copy/ }))
    expect(exportAnalysis).toHaveBeenCalledWith(source, response, null, {}, expect.objectContaining({ 'step:step-1': { decision: 'edited', note: 'My own reminder to discuss at the visit.' }, 'clarification:0': { decision: 'overridden', note: 'I will confirm this separately.' } }))
    await user.click(screen.getByRole('button', { name: 'Reset review of step 1' }))
    expect(screen.getByRole('button', { name: /Download my copy/ })).toBeDisabled()
    expect(screen.getByRole('checkbox', { name: /I have read the note/ })).toBeDisabled()
  })
  it('invalidates confirmation when local review states change', async () => {
    const user = userEvent.setup(); render(<App />); await createPlan(user); await reviewScreen(user); await acceptAll(user)
    await user.click(screen.getByRole('checkbox', { name: /I have read the note/ }))
    await user.selectOptions(screen.getByLabelText('Your review of step 1'), 'read')
    expect(screen.getByRole('button', { name: /Download my copy/ })).toBeDisabled()
  })
  it('uses a skeleton and disables source actions while a plan is pending', async () => {
    let resolve!: (value: Analysis) => void
    vi.mocked(analyze).mockReturnValue(new Promise(done => { resolve = done }))
    const user = userEvent.setup(); render(<App />)
    await user.click(screen.getByRole('checkbox', consent))
    await user.click(screen.getByRole('button', planButton))
    expect(screen.getByText('Reading your note')).toBeInTheDocument()
    expect(document.querySelector('.skeleton')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Edit the note' })).toBeDisabled()
    expect(screen.queryByRole('button', planButton)).not.toBeInTheDocument()
    await act(async () => { resolve(response) })
    expect(await screen.findByText(/Written by a prepared demo example/)).toBeInTheDocument()
  })
  it('shows error with original unchanged, permits retry and displays comparison failure', async () => {
    vi.mocked(analyze).mockRejectedValueOnce(new Error('Provider timed out.'))
    const user = userEvent.setup(); render(<App />)
    await user.click(screen.getByRole('checkbox', consent))
    await user.click(screen.getByRole('button', planButton))
    expect(await screen.findByRole('alert')).toHaveTextContent('Provider timed out.')
    expect(screen.getByText(/Your text has not changed/)).toBeInTheDocument()
    await user.click(screen.getByRole('button', planButton))
    await screen.findByText(/Written by a prepared demo example/)
    vi.mocked(teachBack).mockRejectedValueOnce(new Error('Comparison failed.'))
    await user.type(screen.getByLabelText('In your own words'), 'my explanation')
    await user.click(screen.getByRole('button', compareButton))
    expect(await screen.findByRole('alert')).toHaveTextContent('Comparison failed.')
  })
  it('makes uncertain assessments explicit without fabricated confidence or evidence', async () => {
    vi.mocked(teachBack).mockResolvedValue({ ...comparison, result: { ...comparison.result, status: 'unable_to_assess', evidence: [], feedback: 'No supported assessment.' } })
    const user = userEvent.setup(); render(<App />); await createPlan(user)
    await user.type(screen.getByLabelText('In your own words'), 'I am not sure.')
    await user.click(screen.getByRole('button', compareButton))
    expect(await screen.findByText('I could not check this one')).toBeInTheDocument()
    expect(screen.getByText(/We could not back this up with a line from the note/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Override comparison' })).toBeInTheDocument()
  })
  it('handles no steps and an empty source without fabricating a patient or assessment', async () => {
    vi.mocked(analyze).mockResolvedValue({ ...response, result: { ...response.result, items: [] } })
    const user = userEvent.setup(); render(<App />); await createPlan(user)
    expect(screen.getByText('We could not find any clear steps in this text.')).toBeInTheDocument()
    expect(screen.queryByLabelText('In your own words')).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Read the note again' }))
    await user.clear(screen.getByLabelText('Your discharge instructions'))
    expect(screen.getByText('Let’s read your note with you.')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Amira Patel' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', planButton)).toBeDisabled()
  })
  it('shows offline state without claiming readiness', async () => {
    vi.mocked(getHealth).mockRejectedValueOnce(new Error('offline')); render(<App />)
    expect(await screen.findByText(/Cannot reach the service/)).toBeInTheDocument()
  })
})

describe('Free-text journey through the local rule engine', () => {
  const freeText = 'Call the ward on 555 0100 if you have a fever above 38 C.\nBook the follow-up review within seven days, even if you feel better.'
  beforeEach(() => {
    vi.mocked(analyze).mockResolvedValue({ ...rulesResponse, result: { ...rulesResponse.result, source_segments: freeText.split('\n').map((text, index) => ({ id: `s${index + 1}`, text })) } })
    vi.mocked(teachBack).mockResolvedValue({ ...comparison, origin: 'local_rules', result: { ...comparison.result, evidence: rulesResponse.result.items[0].evidence } })
  })
  it('says in plain words that deterministic rules, not an AI, produced the steps', async () => {
    const user = userEvent.setup(); render(<App />)
    await user.click(screen.getByRole('button', { name: 'Edit the note' }))
    await user.clear(screen.getByLabelText('Your discharge instructions'))
    await user.type(screen.getByLabelText('Your discharge instructions'), freeText)
    await user.click(screen.getByRole('checkbox', consent))
    await user.click(screen.getByRole('button', planButton))
    expect(await screen.findByText(/Written by simple rules that copy words from your own text\. No AI model was used\./)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Source S1 · Original wording/ })).toHaveAttribute('href', '#source-s1')
  })
  it('offers no AI presets for text the engine, not the fixture, produced', async () => {
    const user = userEvent.setup(); render(<App />)
    await user.click(screen.getByRole('button', { name: 'Edit the note' }))
    await user.clear(screen.getByLabelText('Your discharge instructions'))
    await user.type(screen.getByLabelText('Your discharge instructions'), freeText)
    await user.click(screen.getByRole('checkbox', consent))
    await user.click(screen.getByRole('button', planButton))
    await screen.findByText(/No AI model was used/)
    expect(screen.queryByRole('button', { name: 'Example that misses something' })).not.toBeInTheDocument()
    await user.type(screen.getByLabelText('In your own words'), 'I will call the ward on Friday if I feel unwell.')
    await user.click(screen.getByRole('button', compareButton))
    expect(await screen.findByText(/Simple rules compared the words, not an AI model\./)).toBeInTheDocument()
  })
})
