Add-Type -AssemblyName System.Speech

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voices = $synth.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name }
if ($voices -contains "Microsoft David Desktop") {
    $synth.SelectVoice("Microsoft David Desktop")
} elseif ($voices -contains "Microsoft Zira Desktop") {
    $synth.SelectVoice("Microsoft Zira Desktop")
}

$synth.Rate = 2  # Crisp, professional presenter tempo (approx 170-175s)

$outDir = "public/video"
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

$outFile = Join-Path $outDir "voiceover.wav"
$synth.SetOutputToWaveFile($outFile)

Write-Host "🎙️ Synthesizing synchronized English voiceover for Asclepius (target: ~170s)..."

# Segment 1: Problem & Mission (0:00 - 0:25)
$s1 = @"
When patients leave hospital, discharge paperwork is packed with dense medical jargon and conditional warnings. Standard AI summarizers often look convincing, but can silently drop critical conditions—turning 'follow up in seven days even if you feel better' into 'only if you feel unwell'. In healthcare, dropping a condition leads directly to preventable complications and hospital readmissions. We built Asclepius to make instructions clear, accessible, and testable.
"@
$synth.Speak($s1)
Start-Sleep -Milliseconds 600

# Segment 2: Clinical Note & Lab Metadata (0:25 - 0:50)
$s2 = @"
Asclepius places the original discharge note side-by-side with every extracted action. Every sentence is given a permanent, numbered source line from S1 to S9. Here is a realistic synthetic note for Amira Patel, age 62. When we expand the metadata card, notice Asclepius displays laboratory values and medications exactly as written. Crucially, it never invents a dosing regimen or prescribes medication. Instead, it quarantines medication records as questions to discuss with the doctor.
"@
$synth.Speak($s2)
Start-Sleep -Milliseconds 600

# Segment 3: Grounded Step Extraction & Citations (0:50 - 1:20)
$s3 = @"
We confirm this is synthetic practice text and click 'Show me my steps'. Asclepius immediately parses the note into bite-sized actions. At the top, the engine provenance is transparent: 'Written by a prepared demo example. No AI looked at this note'. Step 1 highlights the immediate priority: arranging a follow-up within seven days. Notice the citation badge 'Source S4'. Clicking it immediately jumps to and highlights the exact sentence in the clinical note. Nothing is displayed without its source provenance.
"@
$synth.Speak($s3)
Start-Sleep -Milliseconds 600

# Segment 4: AHRQ Teach-Back in Action (1:20 - 1:55)
$s4 = @"
This leads to our core clinical innovation: the AHRQ Teach-Back check. Simply reading an instruction does not prove comprehension. Here, the patient explains Step 1 in their own words. First, we simulate what happens when someone misunderstands: we select the example that misses a condition, saying 'I only need to arrange the follow-up if I still feel unwell'. Asclepius checks this against the source line and provides empathetic, non-blaming guidance: the note specifies within seven days, even if you feel better. Next, we test a matching explanation: the engine confirms comprehension with a reassuring green badge.
"@
$synth.Speak($s4)
Start-Sleep -Milliseconds 600

# Segment 5: Human-in-the-Loop Governance & Audit Dossier (1:55 - 2:25)
$s5 = @"
Once the patient understands the instructions, we transition to Screen 2: 'Check it and save'. Asclepius enforces a strict human-in-the-loop governance desk. Every recommendation must receive an explicit human decision: accept, edit, or set aside with a reason. For quick review, we click 'Quick-accept all suggestions'. Once confirmed, the download button unlocks. Asclepius exports a tamper-evident JSON audit dossier bundling original text, machine reasoning, and human decisions, ready to share with the care team.
"@
$synth.Speak($s5)
Start-Sleep -Milliseconds 600

# Segment 6: Dynamic Offline Rule Engine on Free Text (2:25 - 2:45)
$s6 = @"
Asclepius is not a hardcoded demo. We return to Screen 1, open 'Other examples', and load a short follow-up note. When we run it, notice how the engine provenance dynamically shifts: 'Written by simple rules that copy words from your own text. No AI model was used'. The deterministic rule engine sorts actions by clinical urgency and quotes text verbatim, allowing hackathon judges to test any synthetic text completely offline without API keys.
"@
$synth.Speak($s6)
Start-Sleep -Milliseconds 600

# Segment 7: Verification & Conclusion (2:45 - 2:58)
$s7 = @"
Asclepius passes 114 automated tests across frontend and backend, with zero false reassurances across our synthetic clinical benchmark. Fully open-source on GitHub, Asclepius brings true clarity, accessibility, and confidence to patient discharge. Thank you.
"@
$synth.Speak($s7)

$synth.Dispose()
Write-Host "✅ Voiceover generated successfully at $outFile"
