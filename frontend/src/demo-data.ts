export const editorialSource = `SYNTHETIC DEMO — fictional person and record; not medical advice.
Patient: Amira Patel, age 62 years. Document: discharge instructions.
Issued: 04 October 2026 at 09:20 UTC. Service: Northfield Day Unit (fictional).
Arrange a follow-up within seven days, even if you feel better.
Bring your discharge instructions to that visit.
The follow-up service will confirm the appointment date.
Medication listed in this fictional record: atorvastatin 20 mg. No dosing schedule is provided.
Haemoglobin: 13.2 g/dL; reference interval in this fictional record: 12.0–16.0 g/dL.
Sodium: 139 mmol/L; reference interval in this fictional record: 135–145 mmol/L.`
export const legacySource = 'SYNTHETIC DEMO — not medical advice.\nArrange a follow-up within seven days, even if you feel better.\nBring your discharge instructions to that visit.\nThe follow-up service will confirm the appointment date.'
export const secondSource = 'SYNTHETIC DEMO — not medical advice.\nCall the clinic on Monday to confirm the appointment time.\nBring your appointment letter to the visit.'
export const correctAnswer = 'I will arrange the follow-up within seven days even if I feel better.'
export const incorrectAnswer = 'I only need to arrange the follow-up if I still feel unwell.'
export const fictionalPatient = {
  name: 'Amira Patel', age: '62 years', service: 'Northfield Day Unit',
  issued: '04 Oct 2026 · 09:20 UTC', datetime: '2026-10-04T09:20:00Z',
  medication: 'Atorvastatin', recordedStrength: '20 mg',
  labs: [
    { name: 'Haemoglobin', value: '13.2', unit: 'g/dL', range: '12.0–16.0 g/dL', source: 's8' },
    { name: 'Sodium', value: '139', unit: 'mmol/L', range: '135–145 mmol/L', source: 's9' },
  ],
}
