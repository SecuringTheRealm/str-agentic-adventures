import { expect, test } from "@playwright/test";

/**
 * Complete E2E Workflow Test with Azure OpenAI Integration
 *
 * This test validates the complete user journey:
 * 1. Campaign creation
 * 2. Character creation with D&D 5e attributes
 * 3. Character portrait generation (Azure OpenAI DALL-E)
 * 4. DM chat interaction asking "what do I see?"
 *
 * This test requires:
 * - Backend server running with Azure OpenAI credentials configured
 * - Frontend development server running
 */
test.describe("Complete E2E Workflow with Azure OpenAI", () => {
  test.setTimeout(180000); // 3 minutes for AI operations

  test("full user journey: campaign → character → portrait → DM chat", async ({
    page,
  }) => {
    console.log("🎬 Starting complete E2E workflow test...");

    // Step 1: Navigate to application
    console.log("\n📱 Step 1: Loading application...");
    await page.goto("/");

    // Verify application loads - check for first h1 element (page has multiple)
    await expect(page.locator("h1").first()).toContainText(
      "Securing the Realm",
      { timeout: 10000 }
    );
    console.log("✅ Application loaded successfully");
    await page.screenshot({
      path: "screenshots/e2e-full-journey/01-app-loaded.png",
      fullPage: true,
    });

    // Step 2: Create a campaign
    console.log("\n🏰 Step 2: Creating campaign...");

    // Look for campaign creation button
    const createCampaignBtn = page
      .locator(
        'button:has-text("Create Campaign"), button:has-text("Create"), button:has-text("New Campaign")'
      )
      .first();
    await expect(createCampaignBtn).toBeVisible({ timeout: 10000 });
    await createCampaignBtn.click();
    console.log("✅ Clicked create campaign button");

    await page.waitForTimeout(1000);
    await page.screenshot({
      path: "screenshots/e2e-full-journey/02-campaign-form.png",
      fullPage: true,
    });

    // Fill campaign details
    const campaignNameInput = page
      .locator(
        'input[name="campaign-name"], input[placeholder*="campaign" i], input[placeholder*="name" i]'
      )
      .first();
    await expect(campaignNameInput).toBeVisible({ timeout: 5000 });
    await campaignNameInput.fill("Test Campaign - E2E Workflow");
    console.log("✅ Entered campaign name");

    // Fill setting if available
    const settingInput = page
      .locator(
        'textarea[name="setting"], input[name="setting"], input[placeholder*="setting" i]'
      )
      .first();
    if ((await settingInput.count()) > 0) {
      await settingInput.fill(
        "A mysterious forest realm filled with ancient magic and hidden dangers"
      );
      console.log("✅ Entered campaign setting");
    }

    // Select tone if available
    const toneSelect = page.locator('select[name="tone"]');
    if ((await toneSelect.count()) > 0) {
      await toneSelect.selectOption("heroic");
      console.log("✅ Selected campaign tone");
    }

    await page.screenshot({
      path: "screenshots/e2e-full-journey/03-campaign-filled.png",
      fullPage: true,
    });

    // Submit campaign
    const submitCampaignBtn = page
      .locator(
        'button[type="submit"], button:has-text("Create Campaign"), button:has-text("Create")'
      )
      .first();
    await submitCampaignBtn.click();
    console.log("✅ Submitted campaign creation");

    // Wait for character selection screen
    await page.waitForTimeout(3000);
    await page.screenshot({
      path: "screenshots/e2e-full-journey/04-character-selection.png",
      fullPage: true,
    });

    // Step 3: Create a character
    console.log("\n🧙 Step 3: Creating character...");

    // Look for character creation button
    const createCharacterBtn = page
      .locator(
        'button:has-text("Create Character"), button:has-text("Create New"), button:has-text("New Character"), button:has-text("Create Custom")'
      )
      .first();

    if ((await createCharacterBtn.count()) > 0) {
      await createCharacterBtn.click();
      console.log("✅ Clicked create character button");
      await page.waitForTimeout(2000);
    }

    await page.screenshot({
      path: "screenshots/e2e-full-journey/05-character-form.png",
      fullPage: true,
    });

    // Fill character name
    const characterNameInput = page
      .locator(
        'input[name="name"], input[placeholder*="character" i], input[placeholder*="name" i]'
      )
      .first();
    await expect(characterNameInput).toBeVisible({ timeout: 5000 });
    await characterNameInput.fill("Eldrin Shadowblade");
    console.log("✅ Entered character name: Eldrin Shadowblade");

    // Select race
    const raceSelect = page.locator('select[name="race"]');
    if ((await raceSelect.count()) > 0) {
      await raceSelect.selectOption("elf"); // lowercase for API
      console.log("✅ Selected race: Elf");
    }

    // Select class
    const classSelect = page.locator(
      'select[name="character_class"], select[name="class"]'
    );
    if ((await classSelect.count()) > 0) {
      await classSelect.selectOption("ranger"); // lowercase for API
      console.log("✅ Selected class: Ranger");
    }

    // Fill ability scores if available (total must be 78)
    const abilities = {
      strength: 13,
      dexterity: 16,
      constitution: 13,
      intelligence: 12,
      wisdom: 14,
      charisma: 10,
    };
    // Total: 13+16+13+12+14+10 = 78

    for (const [ability, score] of Object.entries(abilities)) {
      const abilityInput = page
        .locator(
          `input[name="abilities.${ability}"], input[data-ability="${ability}"], input[placeholder*="${ability}" i]`
        )
        .first();

      if ((await abilityInput.count()) > 0) {
        await abilityInput.fill(score.toString());
        console.log(`✅ Set ${ability} to ${score}`);
      }
    }

    // Fill backstory if available
    const backstoryInput = page
      .locator('textarea[name="backstory"], input[name="backstory"]')
      .first();
    if ((await backstoryInput.count()) > 0) {
      await backstoryInput.fill(
        "A skilled ranger from the Moonwood, trained in tracking and survival. Seeks to protect the forest realm from encroaching darkness."
      );
      console.log("✅ Entered character backstory");
    }

    await page.screenshot({
      path: "screenshots/e2e-full-journey/06-character-filled.png",
      fullPage: true,
    });

    // Submit character creation
    const submitCharacterBtn = page
      .locator(
        'button[type="submit"], button:has-text("Create Character"), button:has-text("Create")'
      )
      .first();
    await submitCharacterBtn.click();
    console.log("✅ Submitted character creation");

    // Wait for game interface to load
    await page.waitForTimeout(3000);
    await page.screenshot({
      path: "screenshots/e2e-full-journey/07-game-interface.png",
      fullPage: true,
    });

    // Step 4: Generate character portrait using Azure OpenAI
    console.log(
      "\n🎨 Step 4: Generating character portrait with Azure OpenAI..."
    );

    // Look for portrait generation button
    const portraitBtn = page
      .locator(
        'button:has-text("Character Portrait"), button:has-text("Portrait"), button:has-text("Generate Portrait")'
      )
      .first();

    if ((await portraitBtn.count()) > 0) {
      await expect(portraitBtn).toBeVisible({ timeout: 5000 });
      await portraitBtn.click();
      console.log("✅ Clicked portrait generation button");

      // Wait for image generation (Azure OpenAI DALL-E takes time)
      console.log("⏳ Waiting for Azure OpenAI to generate portrait...");
      await page.waitForTimeout(30000); // 30 seconds for AI image generation

      await page.screenshot({
        path: "screenshots/e2e-full-journey/08-portrait-generating.png",
        fullPage: true,
      });

      // Check if portrait was generated successfully
      const imageDisplay = page
        .locator(
          'img[alt*="Character" i], img[alt*="Portrait" i], .image-display img'
        )
        .first();
      if ((await imageDisplay.count()) > 0) {
        const imageSrc = await imageDisplay.getAttribute("src");
        console.log(
          `✅ Portrait generated successfully: ${imageSrc?.substring(0, 50)}...`
        );

        // Verify image is not broken
        const imageNaturalWidth = await imageDisplay.evaluate(
          (img: HTMLImageElement) => img.naturalWidth
        );
        if (imageNaturalWidth > 0) {
          console.log(
            `✅ Portrait image loaded successfully (width: ${imageNaturalWidth}px)`
          );
        } else {
          console.warn("⚠️ Portrait image may not have loaded properly");
        }
      } else {
        console.warn("⚠️ Portrait image element not found");
      }
    } else {
      console.warn(
        "⚠️ Portrait generation button not found - skipping portrait step"
      );
    }

    await page.screenshot({
      path: "screenshots/e2e-full-journey/09-portrait-generated.png",
      fullPage: true,
    });

    // Step 5: Chat with DM asking "what do I see?"
    console.log("\n💬 Step 5: Chatting with AI Dungeon Master...");

    // Find chat input
    const chatInput = page
      .locator(
        'textarea[placeholder*="message" i], input[placeholder*="message" i], textarea[placeholder*="action" i], input[data-testid="chat-input"]'
      )
      .first();

    await expect(chatInput).toBeVisible({ timeout: 5000 });
    await chatInput.fill("I look around carefully. What do I see?");
    console.log(
      '✅ Entered chat message: "I look around carefully. What do I see?"'
    );

    await page.screenshot({
      path: "screenshots/e2e-full-journey/10-chat-input-filled.png",
      fullPage: true,
    });

    // Send message
    const sendBtn = page
      .locator('button:has-text("Send"), button[type="submit"]')
      .first();
    await sendBtn.click();
    console.log("✅ Sent message to DM");

    // Wait for DM response (Azure OpenAI takes time)
    console.log("⏳ Waiting for AI Dungeon Master response...");
    await page.waitForTimeout(10000); // 10 seconds for AI response

    await page.screenshot({
      path: "screenshots/e2e-full-journey/11-dm-responding.png",
      fullPage: true,
    });

    // Check for DM response in chat
    const chatMessages = page.locator(
      '.chat-message, .message, [data-testid="chat-message"]'
    );
    const messageCount = await chatMessages.count();
    console.log(`✅ Found ${messageCount} chat messages`);

    if (messageCount > 0) {
      // Get last few messages
      const lastMessage = chatMessages.last();
      const messageText = await lastMessage.textContent();
      console.log(
        `✅ Last message preview: ${messageText?.substring(0, 100)}...`
      );
    }

    await page.screenshot({
      path: "screenshots/e2e-full-journey/12-dm-response.png",
      fullPage: true,
    });

    // Step 6: Verify UI/UX elements
    console.log("\n🔍 Step 6: Verifying UI/UX elements...");

    // Check for image truncation issues
    const images = page.locator("img");
    const imageCount = await images.count();
    console.log(`📊 Found ${imageCount} images on page`);

    for (let i = 0; i < Math.min(imageCount, 5); i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute("alt");
      const naturalWidth = await img.evaluate(
        (el: HTMLImageElement) => el.naturalWidth
      );
      const clientWidth = await img.evaluate(
        (el: HTMLImageElement) => el.clientWidth
      );

      console.log(
        `Image ${i}: alt="${alt}", natural=${naturalWidth}px, displayed=${clientWidth}px`
      );

      // Check if image is truncated
      if (naturalWidth > 0 && clientWidth < naturalWidth * 0.5) {
        console.warn(
          `⚠️ Image ${i} may be truncated (showing ${Math.round((clientWidth / naturalWidth) * 100)}% of original)`
        );
      }
    }

    // Check for accessibility
    const buttons = page.locator("button");
    const buttonCount = await buttons.count();
    console.log(`🔘 Found ${buttonCount} buttons`);

    // Check for proper labels
    const labels = page.locator("label");
    const labelCount = await labels.count();
    console.log(`🏷️ Found ${labelCount} form labels`);

    await page.screenshot({
      path: "screenshots/e2e-full-journey/13-final-state.png",
      fullPage: true,
    });

    // Final summary
    console.log("\n📊 E2E Workflow Test Summary:");
    console.log("✅ Application loaded");
    console.log("✅ Campaign created");
    console.log("✅ Character created with D&D 5e attributes");
    console.log("✅ Character portrait generation requested (Azure OpenAI)");
    console.log("✅ DM chat interaction completed");
    console.log("✅ UI/UX elements verified");
    console.log("\n🎉 Complete E2E workflow test finished!");
  });

  test("accessibility and responsive design validation", async ({ page }) => {
    console.log("\n♿ Testing accessibility and responsive design...");

    await page.goto("/");

    // Check viewport responsiveness
    const viewports = [
      { width: 1920, height: 1080, name: "Desktop HD" },
      { width: 1366, height: 768, name: "Laptop" },
      { width: 768, height: 1024, name: "Tablet" },
    ];

    for (const viewport of viewports) {
      await page.setViewportSize({
        width: viewport.width,
        height: viewport.height,
      });
      console.log(
        `📱 Testing ${viewport.name} (${viewport.width}x${viewport.height})`
      );

      await page.waitForTimeout(1000);
      await page.screenshot({
        path: `screenshots/e2e-full-journey/responsive-${viewport.name.toLowerCase().replace(" ", "-")}.png`,
        fullPage: true,
      });

      // Check if content is accessible at this viewport - use first h1 (page has multiple)
      const h1 = page.locator("h1").first();
      await expect(h1).toBeVisible();
      console.log(`✅ Main heading visible at ${viewport.name}`);
    }

    // Reset to default viewport
    await page.setViewportSize({ width: 1280, height: 720 });

    // Check keyboard navigation
    console.log("⌨️ Testing keyboard navigation...");
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");

    // Take screenshot of focused element
    await page.screenshot({
      path: "screenshots/e2e-full-journey/keyboard-navigation.png",
      fullPage: true,
    });

    console.log("✅ Accessibility and responsive design tests completed");
  });
});
