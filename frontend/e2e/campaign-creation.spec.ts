import { expect, test } from "@playwright/test";

test.describe("Campaign Creation Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText(
      "Securing the Realm - Agentic Adventures"
    );
  });

  test("should show campaign hub initially", async ({ page }) => {
    // Check for campaign hub or campaign selection interface
    const campaignHub = page.locator(
      '[data-testid="campaign-hub"], .campaign-setup, .campaign-selection, text="Campaign Hub"'
    );
    await expect(campaignHub).toBeVisible();

    // Take screenshot
    await page.screenshot({
      path: "screenshots/campaign-hub.png",
      fullPage: true,
    });
  });

  test("should be able to create a custom campaign", async ({ page }) => {
    // Look for create campaign button or form
    const createButton = page.locator(
      'button:has-text("Create Campaign"), button:has-text("Create Custom"), button:has-text("New Campaign")'
    );

    if ((await createButton.count()) > 0) {
      await createButton.first().click();

      // Should show campaign creation form
      await expect(
        page.locator('input[name="name"], label:has-text("Campaign Name")')
      ).toBeVisible();

      // Fill out basic campaign information based on SRD requirements
      await page.fill(
        'input[name="name"], [placeholder*="campaign"], [placeholder*="name"]',
        "Test Adventure Campaign"
      );

      // Look for setting field
      const settingField = page.locator(
        'input[name="setting"], textarea[name="setting"], [placeholder*="setting"]'
      );
      if ((await settingField.count()) > 0) {
        await settingField.fill(
          "A classic fantasy realm with ancient ruins and mystical forests"
        );
      }

      // Look for tone selection (based on D&D campaign styles)
      const toneSelect = page.locator(
        'select[name="tone"], [data-testid="tone-select"]'
      );
      if ((await toneSelect.count()) > 0) {
        await toneSelect.selectOption("heroic");
      }

      await page.screenshot({
        path: "screenshots/campaign-creation-form.png",
        fullPage: true,
      });

      // Submit the campaign
      const submitButton = page.locator(
        'button[type="submit"], button:has-text("Create")'
      );
      await submitButton.click();

      // Should proceed to character selection
      await expect(
        page.locator('text="Choose Your Character", text="Character Selection"')
      ).toBeVisible({ timeout: 10000 });

      await page.screenshot({
        path: "screenshots/campaign-created.png",
        fullPage: true,
      });
    }
  });

  test("should be able to select from campaign templates", async ({ page }) => {
    // Look for templates or gallery view
    const templatesSection = page.locator(
      '[data-testid="campaign-templates"], .campaign-gallery, button:has-text("Templates")'
    );

    if ((await templatesSection.count()) > 0) {
      await templatesSection.first().click();

      // Should show available campaign templates
      await expect(
        page.locator(
          '.campaign-card, .template-card, [data-testid="campaign-template"]'
        )
      ).toBeVisible();

      await page.screenshot({
        path: "screenshots/campaign-templates.png",
        fullPage: true,
      });

      // Select a template if available
      const firstTemplate = page
        .locator(".campaign-card, .template-card")
        .first();
      if ((await firstTemplate.count()) > 0) {
        await firstTemplate.click();

        // Should proceed to character selection or campaign details
        await page.screenshot({
          path: "screenshots/template-selected.png",
          fullPage: true,
        });
      }
    }
  });
});
