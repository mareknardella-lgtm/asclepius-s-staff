import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { analyze, exportAnalysis, getHealth, normalizeSource, teachBack, textLength } from './api'
import type { Analysis, Health, HumanDecision, HumanReview, ItemState, TeachBackRecord } from './api'
import { EvidenceList, HumanControl, Icon, Skeleton } from './components'
import { correctAnswer, editorialSource, fictionalPatient, incorrectAnswer, legacySource, secondSource } from './demo-data'

const statusLabels = { matched: 'That matches the note', needs_clarification: 'One part needs a closer look', unable_to_assess: 'I could not check this one' }
// Plain-language names for the engine, for people who are not technical.
// The exact origin code stays in the audit record and in the exported file.
const originPlain = {
  scripted_fixture: 'a prepared demo example. No AI looked at this note.',
  local_rules: 'simple rules that copy words from your own text. No AI model was used.',
  model: 'an AI model, then checked against the original wording.',
} as const
const originLabels = {
  scripted_fixture: 'DEMO FIXTURE · SCRIPTED EXAMPLE, NOT AI',
  local_rules: 'LOCAL RULES ON YOUR TEXT · NOT AI',
  model: 'MODEL OUTPUT · AI ASSISTED',
} as const
export default function App() {
  const [text, setText] = useState(editorialSource)
  const [confirmed, setConfirmed] = useState(false)
  const [health, setHealth] = useState<Health | null>(null)
  const [healthError, setHealthError] = useState(false)
  const [busy, setBusy] = useState<'plan' | 'teach' | null>(null)
  const [error, setError] = useState('')
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [focusId, setFocusId] = useState('')
  const [answer, setAnswer] = useState('')
  const [record, setRecord] = useState<TeachBackRecord | null>(null)
  const [states, setStates] = useState<Record<string, ItemState>>({})
  const [decisions, setDecisions] = useState<HumanReview>({})
  const [reviewed, setReviewed] = useState(false)
  const [exported, setExported] = useState(false)
  const [screen, setScreen] = useState<'understand' | 'review'>('understand')
  const [sourceEditing, setSourceEditing] = useState(false)
  const headingRef = useRef<HTMLHeadingElement>(null)
  const resultRef = useRef<HTMLElement>(null)
  const source = normalizeSource(text)
  const seeded = source === editorialSource
  const length = textLength(source)
  const valid = confirmed && length >= 20 && length <= 4000 && source.split('\n').filter(line => line.trim()).length <= 80
  const focus = analysis?.result.items.find(item => item.id === focusId)
  const reviewKeys = analysis ? [
    ...analysis.result.items.map(item => `step:${item.id}`),
    ...analysis.result.clarifications.map((_, index) => `clarification:${index}`),
    ...analysis.result.questions_for_care_team.map((_, index) => `question:${index}`),
    ...(record ? ['feedback'] : []),
  ] : []
  const remaining = reviewKeys.filter(key => !decisions[key]).length
  const canDownload = reviewed && remaining === 0 && !!analysis && !busy

  useEffect(() => {
    let active = true
    getHealth().then(data => { if (active) setHealth(data) }).catch(() => { if (active) setHealthError(true) })
    return () => { active = false }
  }, [])
  useEffect(() => { if (screen === 'review') headingRef.current?.focus() }, [screen])
  function resetReview() { setReviewed(false); setExported(false) }
  function invalidate() { setAnalysis(null); setRecord(null); setAnswer(''); setFocusId(''); setStates({}); setDecisions({}); setScreen('understand'); resetReview(); setError('') }
  function changeAnswer(value: string) { setAnswer(value); setRecord(null); setDecisions(previous => { const next = { ...previous }; delete next.feedback; return next }); resetReview(); setError('') }
  function decision(key: string, value: HumanDecision | undefined) {
    setDecisions(previous => { const next = { ...previous }; if (value) next[key] = value; else delete next[key]; return next }); resetReview()
  }
  function control(key: string, label: string, content: string) { return <HumanControl key={key} id={label} text={content} value={decisions[key]} disabled={!!busy} onChange={value => decision(key, value)} /> }
  function load(value: string) { invalidate(); setText(value); setConfirmed(false); setSourceEditing(false) }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!valid || busy) return
    invalidate(); setSourceEditing(false); setBusy('plan')
    try {
      const data = await analyze(source)
      setAnalysis(data); setFocusId(data.result.items[0]?.id ?? '')
      setHealth({ status: 'ok', provider: data.provider, model: data.model }); setHealthError(false)
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'The plan could not be prepared. Please try again.') }
    finally { setBusy(null) }
  }
  async function compare(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!analysis || !focus || busy || !answer.trim() || textLength(answer.trim()) > 1000) return
    changeAnswer(answer); setBusy('teach')
    try { setRecord({ answer: answer.trim(), response: await teachBack(source, analysis, focus, answer) }) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'The explanation could not be compared.') }
    finally { setBusy(null) }
  }
  function download() {
    if (!analysis || !canDownload) return
    try { exportAnalysis(source, analysis, record, states, decisions); setExported(true) }
    catch { setError('The file could not be downloaded. Check your browser settings and try again.') }
  }
  const sourceLines = analysis?.result.source_segments ?? source.split('\n').filter(line => line.trim()).map((line, index) => ({ id: `s${index + 1}`, text: line }))
  return <div className="app-shell">
    <a className="skip-link" href="#main">Skip to the instructions</a>
    <header className="site-header"><a className="brand" href="#main" aria-label="Asclepius home"><span className="brand-mark" aria-hidden="true">a.</span><span>Asclepius<small>THE CARE INSTRUCTIONS DESK</small></span></a><div className="header-context"><span>Patient & caregiver edition</span><span className="privacy-cue"><Icon name="lock" /> Nothing is saved on a server</span></div></header>
    <main id="main">
      <div className="page-heading"><div><h1 ref={headingRef} tabIndex={-1}>{screen === 'review' ? 'Your plan, ready to take with you.' : 'What should I do at home?'}</h1><p className="heading-description">{screen === 'review' ? 'Keep your own wording, your questions and the original note together.' : 'Read the steps from your discharge note, then say one back in your own words.'}</p></div><p className="edition-stamp"><strong>Practice example</strong><span>{seeded ? 'Discharge note · 4 October 2026' : 'Your own text'}</span><span>Not a real patient record</span></p></div>
      <nav className="journey-nav" aria-label="Care instructions journey"><button aria-current={screen === 'understand' ? 'step' : undefined} disabled={!!busy} onClick={() => setScreen('understand')}><span className="numeric">1</span> Understand your instructions</button><button aria-current={screen === 'review' ? 'step' : undefined} disabled={!analysis || !!busy} onClick={() => setScreen('review')}><span className="numeric">2</span> Check it and save{analysis && <span className="nav-count">{remaining} left</span>}</button></nav>
      {error && <section className="error-note" role="alert"><strong>We could not finish that.</strong><p>{error}</p><button className="button button-quiet" onClick={() => setError('')}>Close this message</button><p className="caption">Your text has not changed. Try again whenever you are ready.</p></section>}
      <div className="workspace">
        <aside className="source-column" aria-labelledby="source-heading">
          {seeded && <section className="patient-context"><div className="context-top"><span className="caption">Practice patient</span><span className="numeric">Case 4</span></div><h2>{fictionalPatient.name}</h2><p>{fictionalPatient.age} <span aria-hidden="true">/</span> {fictionalPatient.service}</p><dl><div><dt>Document</dt><dd>Discharge instructions</dd></div><div><dt>Issued</dt><dd><time dateTime={fictionalPatient.datetime}>{fictionalPatient.issued}</time></dd></div></dl></section>}
          <section className="document-panel"><div className="section-heading"><div><p className="caption">The original note</p><h2 id="source-heading">Discharge note</h2></div><Icon name="file" /></div>
            <div className="source-toolbar"><button className="text-button" disabled={!!busy} onClick={() => { setSourceEditing(value => !value); setScreen('understand') }}>{sourceEditing ? 'Close editor' : 'Edit the note'}</button><details><summary>Other examples</summary><div className="example-menu"><button disabled={!!busy} onClick={() => load(editorialSource)}>Load practice example</button><button disabled={!!busy} onClick={() => load(legacySource)}>Short follow-up note</button><button disabled={!!busy} onClick={() => load(secondSource)}>Try another example</button><button disabled={!!busy} onClick={() => { load(''); setSourceEditing(true) }}>Start with an empty note</button></div></details></div>
            {sourceEditing && <div className="source-editor"><label htmlFor="input">Your discharge instructions</label><textarea id="input" value={text} rows={9} disabled={!!busy} onChange={event => { invalidate(); setText(event.target.value); setConfirmed(false) }} aria-describedby="input-hint" /><p id="input-hint" className="caption">{length.toLocaleString('en-GB')} of 4,000 characters, up to 80 lines. Please use practice text only.</p></div>}
            <div className="source-view">{sourceLines.length ? sourceLines.map(segment => <p id={`source-${segment.id}`} tabIndex={-1} key={segment.id}><span className="source-number">{segment.id.toUpperCase()}</span>{segment.text}</p>) : <p className="source-empty">No note yet. Add practice instructions in the editor, or choose an example.</p>}</div>
            {seeded && <details className="record-context"><summary>The medicine and test results written in the note <span>As written only</span></summary><div className="record-detail"><p className="caption">Copied from this practice record. Asclepius does not interpret them.</p><dl className="medication-context"><div><dt>{fictionalPatient.medication}</dt><dd className="numeric">{fictionalPatient.recordedStrength}</dd></div></dl><p className="caption">The strength as written, not a dose to take. <a href="#source-s7">See line S7</a></p><table><caption>Test values as written · no medical assessment</caption><thead><tr><th scope="col">Test</th><th scope="col">Value</th><th scope="col">Range in the record</th></tr></thead><tbody>{fictionalPatient.labs.map(lab => <tr key={lab.name}><th scope="row"><a href={`#source-${lab.source}`}>{lab.name}</a></th><td className="numeric">{lab.value} {lab.unit}</td><td className="numeric">{lab.range}</td></tr>)}</tbody></table></div></details>}
            <p className="document-footer">Every step below points back to the line it came from. That shows where a word came from, not that the advice is right for you.</p>
          </section>
          <div className="connection-note" role="status">{health ? health.provider === 'mock' ? 'Working offline · no AI is called' : `Service configured · ${health.model} (availability not verified)` : healthError ? 'Cannot reach the service · start it and try again' : 'Checking the connection…'}</div>
        </aside>
        <section className="working-column" ref={resultRef} aria-label={screen === 'review' ? 'Check your plan' : 'Understand your instructions'} aria-busy={!!busy}>
          {screen === 'understand' ? <>
            {!analysis && busy !== 'plan' && <section className="start-panel"><h2>Let’s read your note with you.</h2><p>You will get the steps one by one, with the original wording next to each one. Nothing is done or sent anywhere.</p><p className="caption">Read the steps · say one back in your own words · keep a copy for the care team.</p><form onSubmit={submit}><label className="review-check"><input type="checkbox" checked={confirmed} onChange={event => { invalidate(); setConfirmed(event.target.checked) }} />This is practice text with no real patient details. I agree to send it to the connected service.</label><button className="button button-primary" disabled={!valid} type="submit">Show me my steps<Icon name="arrow" /></button></form><p className="decision-support">This helps you read your discharge note. It is not medical advice, and it does not check that the advice is correct. Review it with your care team.</p></section>}
            {busy === 'plan' && <Skeleton />}
            {analysis && <div className="result-content">
              <p className="engine-note">Written by {originPlain[analysis.origin]} Each step is the wording from your note, copied over. Nothing here has been checked for medical correctness.</p>
              {analysis.result.items.length === 0 ? <section className="attention-panel"><h2>We could not find any clear steps in this text.</h2><p>Nothing has been filled in for you. Look at the questions below, or ask someone on the care team to read the note with you.</p><button className="button button-secondary" onClick={() => { invalidate(); setSourceEditing(true) }}>Read the note again</button></section> : <>
                <section className="priority-step"><div className="step-heading"><div className="step-tag-group"><span className="step-num-badge priority">Step 1</span><p className="caption">Start here</p></div><span className="state-label">Please check this</span></div><h2>{analysis.result.items[0].instruction}</h2><EvidenceList evidence={analysis.result.items[0].evidence} /><p className="caption">Taken from your note. We have not checked that it is right for you.</p></section>
                {analysis.result.items.slice(1).length > 0 && <section className="secondary-step"><p className="caption step-section-title">Then, one at a time</p>{analysis.result.items.slice(1).map((item, index) => <div className="secondary-step-item" key={item.id}><div className="step-heading"><span className="step-num-badge">Step {index + 2}</span></div><h3>{item.instruction}</h3><EvidenceList evidence={item.evidence} /></div>)}</section>}
              </>}
              {analysis.result.clarifications.length > 0 && <section className="uncertainty-panel"><div className="panel-badge-row"><span className="warning-badge">Things to ask your doctor</span></div><h3>Some parts still need a person to explain them.</h3>{analysis.result.clarifications.map((item, index) => <div className="clarification" key={index}><p>{item.description}</p><EvidenceList evidence={item.evidence} empty="No line in the note backs this up. It is a gap to ask about, not a finding about your health." /></div>)}</section>}
              {analysis.result.items.length > 0 && <section className="teach-back" aria-labelledby="teach-heading"><div className="teach-badge-row"><span className="teach-method-badge">AHRQ Teach-Back Method</span></div><h2 id="teach-heading">Now say one back in your own words.</h2><p className="teach-intro">Research shows explaining instructions back in your own words helps catch misunderstandings before leaving hospital. You can look at the note while you do this — we check the wording, not your memory.</p><form onSubmit={compare}>
                <fieldset className="step-choices" disabled={!!busy}><legend>Which step do you want to say back?</legend>{analysis.result.items.map((item, index) => <label key={item.id}><input type="radio" name="focus-step" value={item.id} checked={focusId === item.id} onChange={() => { setFocusId(item.id); changeAnswer('') }} /><span><strong>Step {index + 1}.</strong> {item.instruction}</span></label>)}</fieldset>
                <label htmlFor="answer">In your own words</label><textarea id="answer" rows={3} value={answer} disabled={!!busy} onChange={event => changeAnswer(event.target.value)} placeholder="How would you explain this step to someone at home?" aria-describedby="answer-hint" /><p id="answer-hint" className="caption">{textLength(answer.trim())} of 1,000 characters · checked against the line you picked</p>{[editorialSource, legacySource].includes(source) && focusId === 'step-1' && <div className="preset-row"><span className="caption">Prepared examples:</span><button className="text-button" type="button" disabled={!!busy} onClick={() => changeAnswer(incorrectAnswer)}>Example that misses something</button><button className="text-button" type="button" disabled={!!busy} onClick={() => changeAnswer(correctAnswer)}>Example that matches</button></div>}<button className="button button-secondary" type="submit" disabled={!!busy || !answer.trim() || textLength(answer.trim()) > 1000}>{busy === 'teach' ? 'Checking against the note…' : 'Check what I said'}<Icon name="arrow" /></button></form>
                {busy === 'teach' && <Skeleton label="Checking against the original wording" />}
                {record && <section className={`feedback ${record.response.result.status}`} role="status"><div className="feedback-status-pill"><span className={`pill ${record.response.result.status}`}>{record.response.result.status === 'matched' ? '✓ Matches note' : record.response.result.status === 'needs_clarification' ? '⚠️ Check difference' : 'ℹ️ Incomplete'}</span></div><h3>{statusLabels[record.response.result.status]}</h3><p>{record.response.result.feedback}</p><EvidenceList evidence={record.response.result.evidence} empty="We could not back this up with a line from the note. Ask someone on the care team rather than relying on this." /><p className="caption">{record.response.origin === 'local_rules' ? 'Simple rules compared the words, not an AI model. ' : ''}Matching the wording is not the same as understanding the advice or being safe.</p>{control('feedback', 'comparison', record.response.result.feedback)}</section>}
              </section>}
              <section className="continue-panel"><div><h3>When you are happy with it, take a copy with you.</h3><p className="caption">{remaining ? `${remaining} suggestions can be checked or edited.` : 'All decisions recorded.'}</p></div><button className="button button-primary" disabled={!!busy} onClick={() => setScreen('review')}>Check it and save<Icon name="arrow" /></button></section>
            </div>}
          </> : analysis && <div className="review-screen result-content"><div className="review-summary"><h2>{remaining ? `${remaining} ${remaining === 1 ? 'decision' : 'decisions'} still yours to make.` : 'Your decisions are recorded.'}</h2><p>Accept, change or set aside each suggestion. Your own words never replace the original note, and nothing here says the advice is medically correct.</p></div>
            {remaining > 0 && <div className="quick-accept-row"><button type="button" className="button button-secondary" disabled={!!busy} onClick={() => { setDecisions(prev => { const next = { ...prev }; reviewKeys.forEach(k => { if (!next[k]) next[k] = { decision: 'accepted', note: '' } }); return next }); resetReview() }}><Icon name="check" />Quick-accept all suggestions</button><span className="caption">or review each suggestion below individually</span></div>}
            {analysis.result.items.map((item, index) => <section className="review-item" key={item.id}><p className="caption">Step {index + 1}</p><h3>{item.instruction}</h3><EvidenceList evidence={item.evidence} />{control(`step:${item.id}`, `step ${index + 1}`, item.instruction)}<label htmlFor={`state-${item.id}`}>Your review of step {index + 1}</label><select id={`state-${item.id}`} value={states[item.id] ?? ''} disabled={!!busy} onChange={event => { const value = event.target.value as ItemState | ''; setStates(previous => { const next = { ...previous }; if (value) next[item.id] = value; else delete next[item.id]; return next }); resetReview() }}><option value="">I have not done this yet</option><option value="read">I have read it</option><option value="ask_care_team">I will ask the care team</option></select></section>)}
            {analysis.result.clarifications.length > 0 && <section className="review-item"><p className="caption">Still to ask about</p>{analysis.result.clarifications.map((item, index) => <div className="clarification" key={index}><p>{item.description}</p><EvidenceList evidence={item.evidence} />{control(`clarification:${index}`, `limitation ${index + 1}`, item.description)}</div>)}</section>}
            {analysis.result.questions_for_care_team.map((question, index) => <section className="review-item" key={index}><p className="caption">A question to ask · not a medical claim</p><h3>{question}</h3><EvidenceList evidence={[]} empty="Suggested from this note. No line backs it up, so it is a topic for you to raise, not a finding." />{control(`question:${index}`, `question ${index + 1}`, question)}</section>)}
            {record && <section className="review-item"><p className="caption">What you said back</p><p><strong>Your words:</strong> {record.answer}</p><p>{record.response.result.feedback}</p><EvidenceList evidence={record.response.result.evidence} />{control('feedback', 'comparison', record.response.result.feedback)}</section>}
            <section className="export-panel"><h3>Take your copy with you.</h3><label className="review-check"><input type="checkbox" checked={reviewed} disabled={remaining > 0 || !!busy} onChange={event => { setReviewed(event.target.checked); setExported(false) }} />I have read the note, the steps and the open questions. This does not mean the advice is medically correct.</label>{remaining > 0 && <p className="caption">Make your {remaining} remaining {remaining === 1 ? 'decision' : 'decisions'} above first.</p>}<button className="button button-primary" disabled={!canDownload} onClick={download}>Download my copy (JSON)<Icon name="download" /></button><p className="caption">The file holds your note, where each step came from and your own decisions. Nothing is sent to a doctor or a clinic.</p>{exported && <p className="export-note" role="status"><Icon name="check" />Download started. Your copy is ready to show the care team.</p>}<button className="text-button" onClick={() => setScreen('understand')}>Back to my steps</button></section>
          </div>}
          {analysis && <details className="audit-trail"><summary>How this was made <span>For anyone who wants the detail</span></summary><dl><div><dt>Made by</dt><dd>{originLabels[analysis.origin]}</dd></div><div><dt>Plan time</dt><dd className="numeric">{analysis.elapsed_ms} ms ({analysis.origin === 'model' ? 'backend elapsed' : analysis.origin === 'local_rules' ? 'local rules, not inference' : 'scripted example, not inference'})</dd></div><div><dt>Prompt</dt><dd>{analysis.prompt_version}</dd></div><div><dt>Request</dt><dd className="numeric">{analysis.request_id}</dd></div>{record && <div><dt>Comparison</dt><dd className="numeric">{record.response.elapsed_ms} ms</dd></div>}</dl><p className="caption">No source or answer is saved on the server. A configured model provider may retain requests under its own policy.</p></details>}
        </section>
      </div>
    </main><footer><span>Asclepius / Care transitions</span><span>Practice data only · helps you read your note · not medical advice.</span><span className="privacy-cue"><Icon name="lock" /> Downloads stay with you</span></footer>
  </div>
}