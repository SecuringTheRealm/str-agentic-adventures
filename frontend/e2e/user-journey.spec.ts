import { expect, test } from "@playwright/test";

/**
 * Drive a campaign through /campaigns/new (CampaignEditor -- the component
 * actually mounted there, not the unused CampaignCreation.tsx the old test
 * assumed) and land on the character-selection screen.
 */
async function createCampaign(
  page: import("@playwright/test").Page,
  name: string,
  setting: string
) {
  await page.goto("/campaigns/new");
  await page.getByLabel("Campaign Name *").fill(name);
  await page.getByLabel("Campaign Setting *").fill(setting);
  await page.getByRole("button", { name: "Create Campaign" }).click();
  await page.waitForURL(/\/campaigns\/[^/]+\/characters$/, {
    timeout: 15000,
  });
}

/** Open a shadcn/Radix <Select> by its trigger testid and pick an option by text. */
async function chooseSelectOption(
  page: import("@playwright/test").Page,
  triggerTestId: string,
  optionText: string
) {
  await page.getByTestId(triggerTestId).click();
  await page.getByRole("option", { name: optionText, exact: true }).click();
}

test.describe("Complete User Journey", () => {
  test("campaign creation to character creation to gameplay", async ({
    page,
  }) => {
    // Step 1: Load the application
    await page.goto("/");
    await expect(page.locator("h1")).toContainText(
      "Securing the Realm - Agentic Adventures"
    );

    // Step 2: Create a campaign
    await createCampaign(
      page,
      "The Lost Mines of Phandelver",
      "The Sword Coast region of Faerûn, featuring the frontier town of Phandalin and the mysterious Lost Mine of Phandelver."
    );
    await expect(page.getByText("Choose Your Character")).toBeVisible();

    // Step 3: Create a character
    await page.getByTestId("create-character-btn").click();
    await page.getByTestId("character-name-input").fill("Thorin Ironshield");
    await chooseSelectOption(page, "character-race-select", "Dwarf");
    await chooseSelectOption(page, "character-class-select", "Fighter");
    await page
      .getByTestId("character-backstory-input")
      .fill(
        "A veteran warrior from the mountain halls of the Ironshield clan, seeking adventure and glory in the wider world."
      );
    await page.getByTestId("submit-character-btn").click();

    // Step 4: Land in the game interface
    await page.waitForURL(/\/campaigns\/[^/]+\/play\/[^/]+$/, {
      timeout: 15000,
    });
    await expect(page.getByTestId("game-interface")).toBeVisible({
      timeout: 10000,
    });

    // Step 5: Send a chat message to the AI Dungeon Master
    await page
      .getByTestId("chat-input")
      .fill(
        "I look around the tavern, taking note of the other patrons and searching for any potential allies or threats."
      );
    await page.getByTestId("chat-send-btn").click();

    // Step 6: Roll a d20 via the dice roller
    await page.getByRole("button", { name: "d20", exact: true }).click();

    // Step 7: Character sheet shows core D&D 5e stats
    await expect(page.getByText("Hit Points")).toBeVisible();
    await expect(page.getByText("Armour Class")).toBeVisible();
    await expect(page.getByText("STR", { exact: true })).toBeVisible();
    await expect(page.getByText("DEX", { exact: true })).toBeVisible();
  });

  test("accessibility and usability assessment", async ({ page }) => {
    await page.goto("/");

    // Page has a single top-level heading identifying the app.
    const headings = await page
      .locator("h1, h2, h3, h4, h5, h6")
      .allTextContents();
    expect(headings.length).toBeGreaterThan(0);

    // Interactive controls exist and are reachable.
    const buttonCount = await page.locator("button").count();
    expect(buttonCount).toBeGreaterThan(0);

    // Images (if any) should carry alt text.
    const images = page.locator("img");
    const imageCount = await images.count();
    for (let i = 0; i < imageCount; i++) {
      await expect(images.nth(i)).toHaveAttribute("alt", /.*/);
    }

    // Keyboard navigation reaches an interactive element.
    await page.keyboard.press("Tab");
    const focused = await page.evaluate(() => document.activeElement?.tagName);
    expect(focused).not.toBe("BODY");
  });
});
