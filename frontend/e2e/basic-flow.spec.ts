import { expect, test } from "@playwright/test";

test.describe("Securing the Realm - Basic Application Flow", () => {
  test("should load the main application", async ({ page }) => {
    await page.goto("/");

    // Check that the app loads and shows the main title
    await expect(page.locator("h1")).toContainText(
      "Securing the Realm - Agentic Adventures"
    );

    // Take a screenshot for manual verification
    await page.screenshot({ path: "screenshots/main-app.png", fullPage: true });
  });

  test("should display campaign selection by default", async ({ page }) => {
    await page.goto("/");

    // Wait for the app to load
    await expect(page.locator("h1")).toBeVisible();

    // Should show campaign hub or selection interface
    // Based on the code, it should show CampaignSelection component initially
    await expect(
      page.locator(
        '.campaign-setup, .campaign-selection, [data-testid="campaign-hub"]'
      )
    ).toBeVisible();

    await page.screenshot({
      path: "screenshots/campaign-selection.png",
      fullPage: true,
    });
  });
});
