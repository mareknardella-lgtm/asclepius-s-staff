import { useState } from 'react'
import type { Evidence, HumanDecision } from './api'

export function Icon({ name }: { name: 'arrow' | 'file' | 'check' | 'lock' | 'download' }) {
  const paths = {
    arrow: 'M4 12h16m-6-6 6 6-6 6', file: 'M14 3H6v18h12V7l-4-4Zm0 0v5h5M9 12h6m-6 4h6',
    check: 'm5 12 4 4L19 6', lock: 'M7 10V7a5 5 0 0 1 10 0v3M5 10h14v11H5V10Zm7 4v3',
    download: 'M12 3v12m-4-4 4 4 4-4M5 17v4h14v-4',
  }
  return <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name]} /></svg>
}
export function EvidenceList({ evidence, label = 'Source', empty = 'No supporting passage was supplied. Treat this as a limitation, not a medical finding.' }: { evidence: Evidence[]; label?: string; empty?: string }) {
  return <div className="evidence-list">{evidence.length === 0 ? <p className="evidence-empty">{empty}</p> : evidence.map((ref, index) => <blockquote key={`${ref.segment_id}-${index}`}><a href={`#source-${ref.segment_id}`}><Icon name="file" />{label} {ref.segment_id.toUpperCase()} · Original wording</a><p>“{ref.quote}”</p></blockquote>)}</div>
}
export function Skeleton({ label = 'Reading your note' }: { label?: string }) {
  return <div className="loading-state" role="status"><p className="caption">{label}</p><div aria-hidden="true" className="skeleton-layout"><span className="skeleton skeleton-title" /><span className="skeleton" /><span className="skeleton" /><span className="skeleton skeleton-short" /><div className="skeleton-rule" /><span className="skeleton skeleton-title" /><span className="skeleton" /></div><p className="caption">One moment. Nothing is decided or sent anywhere.</p></div>
}
export function HumanControl({ id, text, value, disabled, onChange }: { id: string; text: string; value?: HumanDecision; disabled: boolean; onChange: (value: HumanDecision | undefined) => void }) {
  const [mode, setMode] = useState<'edited' | 'overridden' | null>(null)
  const [draft, setDraft] = useState('')
  const label = value?.decision === 'accepted' ? 'Accepted by you' : value?.decision === 'edited' ? 'Your edited wording' : value?.decision === 'overridden' ? 'Set aside by you' : 'Awaiting your review'
  function open(next: 'edited' | 'overridden') { setMode(next); setDraft(value?.note || (next === 'edited' ? text : '')) }
  return <div className="human-control">
    <div className="human-control-top"><span className="decision-label">{label}</span><div className="decision-actions"><button type="button" disabled={disabled} aria-label={`Accept ${id}`} aria-pressed={value?.decision === 'accepted'} onClick={() => { onChange({ decision: 'accepted', note: '' }); setMode(null) }}>Accept</button><button type="button" disabled={disabled} aria-label={`Edit ${id}`} onClick={() => open('edited')}>Edit</button><button type="button" disabled={disabled} aria-label={`Override ${id}`} onClick={() => open('overridden')}>Set aside</button>{value && <button type="button" disabled={disabled} aria-label={`Reset review of ${id}`} onClick={() => { onChange(undefined); setMode(null) }}>Reset</button>}</div></div>
    {value?.note && <p className="human-note"><strong>Your note, not AI:</strong> {value.note}</p>}
    {mode && <div className="edit-area"><label htmlFor={`edit-${id}`}>{mode === 'edited' ? 'Your wording' : 'Why you are setting this aside'} · {id}</label><textarea id={`edit-${id}`} rows={3} maxLength={600} disabled={disabled} value={draft} onChange={event => setDraft(event.target.value)} /><p className="caption">The original suggestion and its source will stay unchanged in the audit record.</p><div className="button-row"><button className="button button-secondary" type="button" disabled={disabled || !draft.trim()} onClick={() => { onChange({ decision: mode, note: draft.trim() }); setMode(null) }}>Save your {mode === 'edited' ? 'wording' : 'reason'}</button><button className="button button-quiet" type="button" disabled={disabled} onClick={() => setMode(null)}>Cancel</button></div></div>}
  </div>
}
