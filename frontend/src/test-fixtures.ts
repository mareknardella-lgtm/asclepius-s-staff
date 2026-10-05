import type { Analysis, TeachBack } from './api'
import { editorialSource } from './demo-data'
export const source = editorialSource
export const response: Analysis = {
  schema_version: 'care-v1', prompt_version: 'care-plan-v1', request_id: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', provider: 'mock', model: null, is_mock: true, origin: 'scripted_fixture', elapsed_ms: 4,
  result: {
    source_segments: source.split('\n').map((text, index) => ({ id: `s${index + 1}`, text })),
    summary: 'Scripted synthetic fixture, not real AI.',
    items: [{ id: 'step-1', instruction: 'Arrange follow-up within seven days, even if you feel better.', evidence: [{ segment_id: 's4', quote: 'Arrange a follow-up within seven days, even if you feel better.' }] }],
    clarifications: [{ description: 'No exact appointment date is provided.', evidence: [] }], questions_for_care_team: ['How can I confirm the appointment?'],
  },
}
export const comparison: TeachBack = {
  ...response, prompt_version: 'care-teach-back-v1',
  result: { focus_id: 'step-1', status: 'needs_clarification', feedback: 'Scripted feedback: the source says even if you feel better.', evidence: response.result.items[0].evidence },
}
// Free text is handled by the deterministic engine, which must be labelled as such.
export const rulesResponse: Analysis = {
  ...response, origin: 'local_rules', elapsed_ms: 2,
  result: {
    ...response.result,
    summary: '2 steps taken directly from this document. Produced by local rules, not by an AI model.',
    items: [
      { id: 'step-1', instruction: 'Call the ward on 555 0100 if you have a fever above 38 C.', evidence: [{ segment_id: 's1', quote: 'Call the ward on 555 0100 if you have a fever above 38 C.' }] },
      { id: 'step-2', instruction: 'Book the follow-up review within seven days, even if you feel better.', evidence: [{ segment_id: 's2', quote: 'Book the follow-up review within seven days, even if you feel better.' }] },
    ],
  },
}
