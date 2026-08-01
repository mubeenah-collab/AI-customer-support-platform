const { chromium } = require('./frontend/node_modules/playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const outputDir = path.join(__dirname, 'recordings');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log('Starting 1080p Playwright video recorder...');

  const browser = await chromium.launch({
    headless: false,
    args: ['--window-size=1920,1080', '--force-device-scale-factor=1.25']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: outputDir,
      size: { width: 1920, height: 1080 }
    }
  });

  const page = await context.newPage();

  // Custom zoom script for text clarity
  await page.addInitScript(() => {
    window.addEventListener('DOMContentLoaded', () => {
      document.body.style.zoom = '1.15';
    });
  });

  console.log('1. Navigating to Register page...');
  await page.goto('http://localhost:3100/register');
  await page.waitForTimeout(1000);

  const email = `demo_${Date.now()}@company.com`;

  try {
    await page.fill('input[placeholder="John Doe"]', 'Alex Morgan');
    await page.fill('input[placeholder="name@company.com"]', email);
    await page.fill('input[placeholder="••••••••"] >> nth=0', 'Password123!');
    await page.fill('input[placeholder="••••••••"] >> nth=1', 'Password123!');
    await page.selectOption('select', 'admin');
    await page.waitForTimeout(800);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
  } catch (err) {
    console.log('Registration skipped, logging in...');
  }

  console.log('2. Showcasing Executive Dashboard...');
  await page.goto('http://localhost:3100/admin/dashboard');
  await page.waitForTimeout(1500);
  await page.mouse.wheel(0, 250);
  await page.waitForTimeout(2500);
  await page.mouse.wheel(0, -250);
  await page.waitForTimeout(1000);

  console.log('3. Navigating to Multi-Agent AI Support Chat...');
  await page.goto('http://localhost:3100/customer/chat');
  await page.waitForTimeout(2000);

  try {
    const chatInput = page.locator('textarea, input[placeholder*="Ask"], input[placeholder*="message"], input[type="text"]').first();
    if (await chatInput.isVisible({ timeout: 3000 })) {
      await chatInput.click();
      await chatInput.type('How does the multi-agent AI system handle customer support escalations using CrewAI and Gemini?', { delay: 30 });
      await page.waitForTimeout(800);
      const sendBtn = page.locator('button:has-text("Send"), button[type="submit"]').first();
      if (await sendBtn.isVisible()) {
        await sendBtn.click();
      } else {
        await page.keyboard.press('Enter');
      }
      await page.waitForTimeout(7000);
    }
  } catch (e) {
    console.log('Chat interaction step completed.');
  }

  console.log('4. Navigating to Knowledge Base RAG Documents...');
  await page.goto('http://localhost:3100/admin/documents');
  await page.waitForTimeout(4000);

  console.log('5. Navigating to Hybrid Semantic Search Console...');
  await page.goto('http://localhost:3100/admin/search');
  await page.waitForTimeout(2000);

  try {
    const searchInput = page.locator('input[placeholder*="search"], input[type="text"]').first();
    if (await searchInput.isVisible({ timeout: 3000 })) {
      await searchInput.click();
      await searchInput.type('OAuth2 security rate limiter architecture', { delay: 40 });
      await page.waitForTimeout(800);
      await page.keyboard.press('Enter');
    }
  } catch (e) {}
  await page.waitForTimeout(4500);

  console.log('6. Navigating to Support Tickets Queue...');
  await page.goto('http://localhost:3100/admin/tickets');
  await page.waitForTimeout(4000);

  console.log('7. Navigating to Analytics & System Health Reports...');
  await page.goto('http://localhost:3100/admin/reports');
  await page.waitForTimeout(4500);

  console.log('8. Navigating to System Settings...');
  await page.goto('http://localhost:3100/admin/settings');
  await page.waitForTimeout(3000);

  console.log('9. Finishing recording...');
  const videoPath = await page.video().path();
  await context.close();
  await browser.close();

  console.log(`RECORDING_COMPLETE: ${videoPath}`);
})();
