import { expect, test } from "@playwright/test";

/**
 * Helper: create a campaign via the real /campaigns/new route (rendered by
 * CampaignEditor) and land on the character-selection screen. The old
 * version of this file drove a "Create Campaign" button/form that doesn't
 * exist on the home page and referenced fields from CampaignCreation.tsx,
 * a component no page ever renders -- CampaignEditor is what's actually
 * mounted at /campaigns/new, so we drive that instead.
 */
async function createCampaign(
  page: import("@playwright/test").Page,
  name: string
) {
  await page.goto("/campaigns/new");
  await page.getByLabel("Campaign Name *").fill(name);
  await page
    .getByLabel("Campaign Setting *")
    .fill("A classic fantasy realm with ancient ruins and mystical forests");
  await page.getByRole("button", { name: "Create Campaign" }).click();
  await page.waitForURL(/\/campaigns\/[^/]+\/characters$/, {
    timeout: 15000,
  });
  await expect(page.getByText("Choose Your Character")).toBeVisible();
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

test.describe("Character Creation Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText(
      "Securing the Realm - Agentic Adventures"
    );
  });

  test("should show character selection options", async ({ page }) => {
    await createCampaign(page, "Test Campaign for Character");

    await expect(page.getByTestId("create-character-btn")).toBeVisible();
    await expect(page.getByTestId("browse-characters-btn")).toBeVisible();
  });

  test("should be able to create a new D&D 5e character", async ({ page }) => {
    await createCampaign(page, "Test Campaign");
    await page.getByTestId("create-character-btn").click();

    await expect(page.getByTestId("character-name-input")).toBeVisible();
    await page.getByTestId("character-name-input").fill("Thorin Ironbeard");

    // NOTE: API expects lowercase values (e.g., "dwarf" not "Dwarf") --
    // CharacterCreation.tsx lowercases the option value itself, the visible
    // option text stays capitalised.
    await chooseSelectOption(page, "character-race-select", "Dwarf");
    await chooseSelectOption(page, "character-class-select", "Fighter");

    await page
      .getByTestId("character-backstory-input")
      .fill(
        "A veteran warrior from the mountain clans, skilled in combat and loyal to his companions."
      );

    // Defaults are 13 across the board (78 total, the required point-buy
    // sum) -- keep the net change at zero so the form's total-points
    // validation still passes.
    await page.getByTestId("ability-strength").fill("15");
    await page.getByTestId("ability-dexterity").fill("11");

    await page.getByTestId("submit-character-btn").click();

    await page.waitForURL(/\/campaigns\/[^/]+\/play\/[^/]+$/, {
      timeout: 15000,
    });
    await expect(page.getByTestId("game-interface")).toBeVisible({
      timeout: 10000,
    });
  });

  test("should be able to browse predefined characters", async ({ page }) => {
    await createCampaign(page, "Test Campaign");
    await page.getByTestId("browse-characters-btn").click();

    await expect(
      page.getByText("Choose a Pre-Defined Character")
    ).toBeVisible();

    const selectButtons = page.getByRole("button", {
      name: /Select This Character/,
    });
    await expect(selectButtons.first()).toBeVisible();
    await selectButtons.first().click();

    await page.waitForURL(/\/campaigns\/[^/]+\/play\/[^/]+$/, {
      timeout: 15000,
    });
    await expect(page.getByTestId("game-interface")).toBeVisible({
      timeout: 10000,
    });
  });

  test("should validate D&D 5e character creation rules", async ({ page }) => {
    await createCampaign(page, "Test Campaign SRD");
    await page.getByTestId("create-character-btn").click();
    await expect(page.getByTestId("character-name-input")).toBeVisible();

    const validRaces = [
      "Human",
      "Elf",
      "Dwarf",
      "Halfling",
      "Dragonborn",
      "Gnome",
      "Half-Elf",
      "Half-Orc",
      "Tiefling",
    ];
    await page.getByTestId("character-race-select").click();
    const raceOptions = await page.getByRole("option").allTextContents();
    for (const option of raceOptions) {
      expect(validRaces).toContain(option.trim());
    }
    // Close the popover before opening the next one.
    await page.keyboard.press("Escape");

    const validClasses = [
      "Barbarian",
      "Bard",
      "Cleric",
      "Druid",
      "Fighter",
      "Monk",
      "Paladin",
      "Ranger",
      "Rogue",
      "Sorcerer",
      "Warlock",
      "Wizard",
    ];
    await page.getByTestId("character-class-select").click();
    const classOptions = await page.getByRole("option").allTextContents();
    for (const option of classOptions) {
      expect(validClasses).toContain(option.trim());
    }
    await page.keyboard.press("Escape");

    // Ability score inputs are clamped to the D&D 5e 8-18 range via
    // min/max attributes (see CharacterCreation.tsx).
    const strengthInput = page.getByTestId("ability-strength");
    await expect(strengthInput).toHaveAttribute("min", "8");
    await expect(strengthInput).toHaveAttribute("max", "18");
  });
});
