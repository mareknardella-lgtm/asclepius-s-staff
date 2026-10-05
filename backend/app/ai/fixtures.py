DEMO_SOURCE = """SYNTHETIC DEMO — not medical advice.
Arrange a follow-up within seven days, even if you feel better.
Bring your discharge instructions to that visit.
The follow-up service will confirm the appointment date."""
SECOND_SOURCE = """SYNTHETIC DEMO — not medical advice.
Call the clinic on Monday to confirm the appointment time.
Bring your appointment letter to the visit."""
EDITORIAL_SOURCE = """SYNTHETIC DEMO — fictional person and record; not medical advice.
Patient: Amira Patel, age 62 years. Document: discharge instructions.
Issued: 04 October 2026 at 09:20 UTC. Service: Northfield Day Unit (fictional).
Arrange a follow-up within seven days, even if you feel better.
Bring your discharge instructions to that visit.
The follow-up service will confirm the appointment date.
Medication listed in this fictional record: atorvastatin 20 mg. No dosing schedule is provided.
Haemoglobin: 13.2 g/dL; reference interval in this fictional record: 12.0–16.0 g/dL.
Sodium: 139 mmol/L; reference interval in this fictional record: 135–145 mmol/L."""
CORRECT_ANSWER = "I will arrange the follow-up within seven days even if I feel better."
INCORRECT_ANSWER = "I only need to arrange the follow-up if I still feel unwell."
