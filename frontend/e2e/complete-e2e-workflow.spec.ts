import { expect, test } from "@playwright/test";

/**
 * Complete E2E Workflow Test
 *
 * Validates the full user journey against whatever the backend reports at
 * /health/dependencies: campaign creation, D&D 5e character creation,
 * character-portrait generation (skipped gracefully when Azure OpenAI isn't
 * configured -- see GameInterface's imageGenerationAvailable check), and a
 * DM chat round-trip (the backend falls back to deterministic responses
 * without Azure OpenAI per this repo's agent-fallback contract, so a reply
 * still arrives).
 *
 * Requires: backend server + frontend dev server running (as CI does via
 * e2e-tests.yml). Portrait generation only runs end-to-end when Azure
 * OpenAI credentials are configured; otherwise it asserts the button is
 * disabled with an explanatory tooltip instead.
 */

test.describe.configure({ mode: "serial" });

async function createCampaign(
  page: import("@playwright/test").Page,
  name: string
) {
  await page.goto("/campaigns/new");
  await page.getByLabel("Campaign Name *").fill(name);
  await page
    .getByLabel("Campaign Setting *")
    .fill(
      "A mysterious forest realm filled with ancient magic and hidden dangers"
    );
  await page.getByRole("button", { name: "Create Campaign" }).click();
  await page.waitForURL(/\/campaigns\/[^/]+\/characters$/, {
    timeout: 15000,
  });
}

async function chooseSelectOption(
  page: import("@playwright/test").Page,
  triggerTestId: string,
  optionText: string
) {
  await page.getByTestId(triggerTestId).click();
  await page.getByRole("option", { name: optionText, exact: true }).click();
}

test.describe("Complete E2E Workflow", () => {
  test.setTimeout(120000);

  test("full user journey: campaign -> character -> portrait -> DM chat", async ({
    page,
  }) => {
    // Step 1: Load the application
    await page.goto("/");
    await expect(page.locator("h1").first()).toContainText(
      "Securing the Realm",
      { timeout: 10000 }
    );

    // Step 2: Create a campaign
    await createCampaign(page, "Test Campaign - E2E Workflow");
    await expect(page.getByText("Choose Your Character")).toBeVisible();

    // Step 3: Create a character. Ability scores must total 78 (the
    // point-buy budget CharacterCreation.tsx enforces).
    await page.getByTestId("create-character-btn").click();
    await page.getByTestId("character-name-input").fill("Eldrin Shadowblade");
    await chooseSelectOption(page, "character-race-select", "Elf");
    await chooseSelectOption(page, "character-class-select", "Ranger");
    await page.getByTestId("ability-strength").fill("13");
    await page.getByTestId("ability-dexterity").fill("16");
    await page.getByTestId("ability-constitution").fill("13");
    await page.getByTestId("ability-intelligence").fill("12");
    await page.getByTestId("ability-wisdom").fill("14");
    await page.getByTestId("ability-charisma").fill("10");
    await page
      .getByTestId("character-backstory-input")
      .fill(
        "A skilled ranger from the Moonwood, trained in tracking and survival. Seeks to protect the forest realm from encroaching darkness."
      );
    await page.getByTestId("submit-character-btn").click();

    await page.waitForURL(/\/campaigns\/[^/]+\/play\/[^/]+$/, {
      timeout: 15000,
    });
    await expect(page.getByTestId("game-interface")).toBeVisible({
      timeout: 10000,
    });

    // Step 4: Character portrait generation -- only proceeds end-to-end
    // when Azure OpenAI is configured; otherwise the button is disabled
    // and a status message explains why (see GameInterface.tsx).
    const portraitBtn = page.getByTestId("generate-portrait-button");
    await expect(portraitBtn).toBeVisible();
    if (await portraitBtn.isEnabled()) {
      await portraitBtn.click();
      await expect(page.locator("img").first()).toBeVisible({
        timeout: 60000,
      });
    } else {
      await expect(page.getByTestId("visual-generation-status")).toBeVisible();
    }

    // Step 5: Chat with the DM
    const chatLog = page.getByRole("log", { name: "Chat messages" });
    const messagesBefore = await chatLog.locator("> div").count();

    await page
      .getByTestId("chat-input")
      .fill("I look around carefully. What do I see?");
    await page.getByTestId("chat-send-btn").click();

    // A reply always arrives -- either an AI-generated one or the
    // deterministic fallback used when Azure OpenAI isn't configured.
    await expect
      .poll(async () => chatLog.locator("> div").count(), { timeout: 30000 })
      .toBeGreaterThan(messagesBefore);

    // Step 6: Basic UI/UX sanity checks
    const images = page.locator("img");
    const imageCount = await images.count();
    for (let i = 0; i < imageCount; i++) {
      await expect(images.nth(i)).toHaveAttribute("alt", /.*/);
    }
  });

  test("accessibility and responsive design validation", async ({ page }) => {
    await page.goto("/");

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
      await expect(page.locator("h1").first()).toBeVisible();
    }

    await page.setViewportSize({ width: 1280, height: 720 });

    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    const focused = await page.evaluate(() => document.activeElement?.tagName);
    expect(focused).not.toBe("BODY");
  });
});
