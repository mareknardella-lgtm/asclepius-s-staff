const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// Require playwright from existing node_modules
const { chromium } = require('C:/Users/Marek/Desktop/Projects/Nexora/node_modules/playwright');

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function main() {
  console.log('🎬 Starting Asclepius 3-Minute Demo Video Recording...');
  const outputDir = path.resolve(__dirname, '../public/video');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Clear previous raw webm recordings
  const oldFiles = fs.readdirSync(outputDir);
  for (const f of oldFiles) {
    if (f.endsWith('.webm')) {
      try { fs.unlinkSync(path.join(outputDir, f)); } catch {}
    }
  }

  const browser = await chromium.launch({
    channel: 'chrome',
    headless: true,
    args: ['--enable-webgl', '--no-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: {
      dir: outputDir,
      size: { width: 1280, height: 720 }
    }
  });

  const page = await context.newPage();

  // Inject a high-contrast cursor to make mouse movements and clicks clear on video
  await page.addInitScript(() => {
    window.addEventListener('DOMContentLoaded', () => {
      const cursor = document.createElement('div');
      cursor.id = 'demo-cursor';
      cursor.style.cssText = `
        position: fixed;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: rgba(36, 94, 82, 0.45);
        border: 2px solid #245e52;
        box-shadow: 0 0 14px rgba(36, 94, 82, 0.6);
        pointer-events: none;
        z-index: 999999;
        transition: transform 0.12s ease, background 0.15s ease;
        transform: translate(-50%, -50%);
        display: none;
      `;
      document.body.appendChild(cursor);

      window.addEventListener('mousemove', (e) => {
        cursor.style.display = 'block';
        cursor.style.left = `${e.clientX}px`;
        cursor.style.top = `${e.clientY}px`;
      });

      window.addEventListener('mousedown', () => {
        cursor.style.transform = 'translate(-50%, -50%) scale(0.75)';
        cursor.style.background = 'rgba(161, 46, 40, 0.85)';
      });

      window.addEventListener('mouseup', () => {
        cursor.style.transform = 'translate(-50%, -50%) scale(1)';
        cursor.style.background = 'rgba(36, 94, 82, 0.45)';
      });
    });
  });

  async function smoothMove(x, y, steps = 25) {
    await page.mouse.move(x, y, { steps });
  }

  async function smoothClick(selector, pauseAfter = 1800) {
    const loc = page.locator(selector).first();
    await loc.waitFor({ state: 'attached', timeout: 10000 });
    try {
      await loc.scrollIntoViewIfNeeded({ timeout: 3000 });
    } catch {}
    await delay(300);
    const box = await loc.boundingBox();
    if (box) {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 20 });
      await delay(200);
      await page.mouse.down();
      await delay(120);
      await page.mouse.up();
    } else {
      await loc.click({ force: true, timeout: 3000 });
    }
    await delay(pauseAfter);
  }

  async function smoothCheck(selector = 'input[type="checkbox"]', pauseAfter = 1800) {
    const loc = page.locator(selector).first();
    await loc.waitFor({ state: 'attached', timeout: 10000 });
    try {
      await loc.scrollIntoViewIfNeeded({ timeout: 3000 });
    } catch {}
    await delay(200);
    const isChecked = await loc.isChecked();
    if (!isChecked) {
      const box = await loc.boundingBox();
      if (box) {
        await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 20 });
        await delay(200);
      }
      await loc.check({ force: true });
    }
    await delay(pauseAfter);
  }

  console.log('🌐 Opening http://127.0.0.1:5173...');
  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle' });
  await delay(2000);

  // =========================================================================
  // SCENE 1: INTRODUCTION & THE CLINICAL PROBLEM (0:00 - 0:25, ~25s)
  // =========================================================================
  console.log('📌 Scene 1: Introduction & The Core Healthcare Problem (0:00 - 0:25)');
  await smoothMove(640, 180, 25);
  await delay(3500);

  // Hover over the main question
  await smoothMove(420, 120, 20);
  await delay(4000);

  // Hover over the synthetic practice patient banner
  await smoothMove(280, 220, 20);
  await delay(4500);

  // Scroll slightly to view note lines S1 to S9
  await page.evaluate(() => window.scrollBy({ top: 100, behavior: 'smooth' }));
  await delay(3000);

  // Move along note lines S4 to S6
  await smoothMove(260, 370, 20);
  await delay(4000);
  await smoothMove(260, 420, 15);
  await delay(4000);

  // =========================================================================
  // SCENE 2: CLINICAL NOTE & LAB METADATA (0:25 - 0:50, ~25s)
  // =========================================================================
  console.log('📌 Scene 2: Structured Clinical Note & Laboratory Metadata (0:25 - 0:50)');
  // Expand metadata summary
  await smoothClick('summary:has-text("The medicine and test results")', 2500);

  // Hover on medication and reference intervals
  await smoothMove(280, 480, 20);
  await delay(4000);
  await smoothMove(280, 560, 20);
  await delay(4500);

  // Move over to the right panel consent checkbox
  await smoothMove(850, 280, 25);
  await delay(3000);

  // Check consent box
  await smoothCheck('input[type="checkbox"]', 2000);
  await delay(3000);

  // Hover over primary button
  await smoothMove(850, 360, 20);
  await delay(3500);

  // =========================================================================
  // SCENE 3: GROUNDED STEP EXTRACTION & CITATIONS (0:50 - 1:20, ~30s)
  // =========================================================================
  console.log('📌 Scene 3: Grounded Step Extraction & Interactive Citations (0:50 - 1:20)');
  await smoothClick('button:has-text("Show me my steps")', 2000);
  await page.locator('a[href="#source-s4"]').first().waitFor({ state: 'visible', timeout: 15000 });

  // Observe provenance header and Step 1
  await smoothMove(820, 190, 25);
  await delay(4500);

  // Click citation Source S4 to highlight original wording
  console.log('🔗 Clicking Citation Source S4...');
  await smoothClick('a[href="#source-s4"]', 3500);

  // Hover over highlighted line S4 on the left
  await smoothMove(260, 360, 25);
  await delay(4500);

  // Scroll down to observe Step 2 and Things to ask doctor
  await page.evaluate(() => window.scrollBy({ top: 220, behavior: 'smooth' }));
  await delay(3000);
  await smoothMove(840, 320, 20);
  await delay(4000);
  await smoothMove(840, 440, 20);
  await delay(4500);

  // =========================================================================
  // SCENE 4: AHRQ TEACH-BACK IN ACTION (1:20 - 1:55, ~35s)
  // =========================================================================
  console.log('📌 Scene 4: Interactive AHRQ Teach-Back Check (1:20 - 1:55)');
  // Scroll to Teach-Back section
  await page.evaluate(() => window.scrollBy({ top: 240, behavior: 'smooth' }));
  await delay(2500);

  // Click "Example that misses something"
  console.log('⚠️ Submitting misunderstood example...');
  await smoothClick('button:has-text("Example that misses something")', 2000);
  await smoothClick('button:has-text("Check what I said")', 3500);

  // Hover over the amber clarification badge
  await smoothMove(840, 520, 20);
  await delay(5000);

  // Now click "Example that matches"
  console.log('✅ Submitting matching example...');
  await smoothClick('button:has-text("Example that matches")', 2000);
  await smoothClick('button:has-text("Check what I said")', 3500);

  // Hover over the green match confirmation
  await smoothMove(840, 520, 20);
  await delay(6000);

  // =========================================================================
  // SCENE 5: HUMAN REVIEW DESK & DOSSIER (1:55 - 2:25, ~30s)
  // =========================================================================
  console.log('📌 Scene 5: Human-in-the-Loop Review Desk & JSON Dossier (1:55 - 2:25)');
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await delay(1200);

  // Navigate to Screen 2 via top nav
  await smoothClick('nav.journey-nav button:has-text("Check it and save")', 3000);

  // Move through the review items
  await smoothMove(500, 280, 20);
  await delay(3500);

  // Quick accept all suggestions
  console.log('⚡ Quick-accepting all suggestions...');
  await smoothClick('button:has-text("Quick-accept all suggestions")', 2500);

  // Check the confirmation agreement
  await smoothCheck('input[type="checkbox"]', 2000);

  // Open the "How this was made" disclosure
  await smoothClick('summary:has-text("How this was made")', 2500);

  // Hover over provenance metrics and download button
  await smoothMove(500, 580, 20);
  await delay(4000);
  await smoothMove(750, 480, 20);
  await delay(5000);

  // =========================================================================
  // SCENE 6: DYNAMIC OFFLINE RULE ENGINE ON FREE TEXT (2:25 - 2:45, ~20s)
  // =========================================================================
  console.log('📌 Scene 6: 100% Offline Rule Engine on Free Text (2:25 - 2:45)');
  // Scroll to top and click back to Screen 1 via top nav
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await delay(1200);
  await smoothClick('nav.journey-nav button:has-text("Understand your instructions")', 2000);

  // Open "Other examples" and select Short follow-up note
  await smoothClick('summary:has-text("Other examples")', 1500);
  await smoothClick('button:has-text("Short follow-up note")', 2000);

  // Check consent and run
  await smoothCheck('input[type="checkbox"]', 1500);
  await smoothClick('button:has-text("Show me my steps")', 3000);
  await page.locator('.result-content').first().waitFor({ state: 'visible', timeout: 15000 });

  // Hover over the dynamic rule engine origin banner
  await smoothMove(820, 180, 20);
  await delay(5000);

  // =========================================================================
  // SCENE 7: VERIFICATION, REPO & CONCLUSION (2:45 - 3:02, ~17s)
  // =========================================================================
  console.log('📌 Scene 7: Verification & Outro (2:45 - 3:02)');
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  await delay(2000);

  // Hover over Asclepius header
  await smoothMove(300, 45, 20);
  await delay(5000);
  await smoothMove(640, 200, 20);
  await delay(5000);

  // Close browser cleanly to finalize webm video file
  console.log('💾 Finalizing video capture...');
  await page.close();
  await context.close();
  await browser.close();

  // Locate the generated webm file
  const videoFiles = fs.readdirSync(outputDir).filter((f) => f.endsWith('.webm'));
  if (videoFiles.length === 0) {
    console.error('❌ Error: No webm video file found.');
    return;
  }

  const rawWebmPath = path.join(outputDir, videoFiles[0]);
  const voiceoverPath = path.join(outputDir, 'voiceover.wav');
  const finalMp4Path = path.join(outputDir, 'asclepius_demo_3min.mp4');

  console.log(`🎬 Captured raw video: ${rawWebmPath}`);
  console.log('⚙️ Merging synchronized voiceover and encoding high-definition MP4 with FFmpeg...');

  try {
    const ffmpegCmd = `ffmpeg -y -i "${rawWebmPath}" -i "${voiceoverPath}" -c:v libx264 -pix_fmt yuv420p -preset fast -crf 20 -c:a aac -b:a 192k -shortest "${finalMp4Path}"`;
    execSync(ffmpegCmd, { stdio: 'inherit' });
    console.log(`\n🎉 SUCCESS! High-quality 3-Minute Demo Video produced at: ${finalMp4Path}`);

    // Copy to frontend/public/video as well
    const frontendVideoDir = path.resolve(__dirname, '../frontend/public/video');
    if (!fs.existsSync(frontendVideoDir)) {
      fs.mkdirSync(frontendVideoDir, { recursive: true });
    }
    fs.copyFileSync(finalMp4Path, path.join(frontendVideoDir, 'asclepius_demo_3min.mp4'));
    console.log('📦 Copied to frontend/public/video/asclepius_demo_3min.mp4 for public asset serving.');
  } catch (err) {
    console.error('FFmpeg execution error:', err.message);
  }
}

main().catch((err) => {
  console.error('Recording error:', err);
  process.exit(1);
});
