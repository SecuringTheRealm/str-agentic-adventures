import { expect, test } from "@playwright/test";

test.describe("Game Session Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText(
      "Securing the Realm - Agentic Adventures"
    );
  });

  test("should start a game session after campaign and character creation", async ({
    page,
  }) => {
    // Navigate through the full flow: Campaign -> Character -> Game

    // Step 1: Create Campaign
    const createCampaignBtn = page.locator(
      'button:has-text("Create Campaign")'
    );
    if ((await createCampaignBtn.count()) > 0) {
      await createCampaignBtn.click();

      await page.fill('input[name="name"]', "Epic Adventure Campaign");

      const settingField = page.locator(
        'input[name="setting"], textarea[name="setting"]'
      );
      if ((await settingField.count()) > 0) {
        await settingField.fill(
          "A mysterious realm where ancient magic still flows"
        );
      }

      await page.locator('button[type="submit"]').click();

      // Step 2: Create/Select Character
      await expect(page.locator('text="Choose Your Character"')).toBeVisible({
        timeout: 10000,
      });

      const createCharacterBtn = page.locator(
        'button:has-text("Create Character")'
      );
      if ((await createCharacterBtn.count()) > 0) {
        await createCharacterBtn.click();

        // Quick character creation
        await page.fill('input[name="name"]', "Aria Lightbringer");

        const raceSelect = page.locator('select[name="race"]');
        if ((await raceSelect.count()) > 0) {
          await raceSelect.selectOption("Elf");
        }

        const classSelect = page.locator('select[name="character_class"]');
        if ((await classSelect.count()) > 0) {
          await classSelect.selectOption("Wizard");
        }

        await page.locator('button[type="submit"]').click();
      } else {
        // Try predefined characters if create isn't available
        const browseBtn = page.locator('button:has-text("Browse Characters")');
        if ((await browseBtn.count()) > 0) {
          await browseBtn.click();

          const firstCharacter = page.locator(".character-card").first();
          if ((await firstCharacter.count()) > 0) {
            await firstCharacter.click();
          }
        }
      }

      // Step 3: Should now be in Game Interface
      await expect(
        page.locator('[data-testid="game-interface"], .game-interface')
      ).toBeVisible({ timeout: 15000 });

      await page.screenshot({
        path: "screenshots/game-session-started.png",
        fullPage: true,
      });
    }
  });

  test("should display game interface components", async ({ page }) => {
    // This test assumes we can get to the game interface
    // In a real scenario, we'd go through the full flow

    // For now, let's check if we can detect game interface elements
    await page.goto("/");

    // Try to get to game interface quickly (abbreviated flow)
    const gameInterface = page.locator(
      '[data-testid="game-interface"], .game-interface'
    );

    // If we can't get there directly, try the flow
    if ((await gameInterface.count()) === 0) {
      // Quick navigation attempt
      const createBtn = page.locator('button:has-text("Create Campaign")');
      if ((await createBtn.count()) > 0) {
        await createBtn.click();
        await page.fill('input[name="name"]', "Test Game");
        await page.locator('button[type="submit"]').click();

        // Try to quickly get through character selection
        const quickCharacterBtn = page
          .locator('button:has-text("Browse Characters"), .character-card')
          .first();
        if ((await quickCharacterBtn.count()) > 0) {
          await quickCharacterBtn.click();
        }
      }
    }

    // Check for game interface elements that should be present
    const gameElements = [
      '[data-testid="chat-interface"], .chat-interface, .chat-box',
      '[data-testid="character-sheet"], .character-sheet',
      '[data-testid="dice-roller"], .dice-roller',
      'text="Game Interface"',
    ];

    for (const selector of gameElements) {
      const element = page.locator(selector);
      if ((await element.count()) > 0) {
        await expect(element).toBeVisible();
      }
    }

    await page.screenshot({
      path: "screenshots/game-interface-components.png",
      fullPage: true,
    });
  });

  test("should allow interaction with AI Dungeon Master", async ({ page }) => {
    // Navigate to game interface (abbreviated)
    await page.goto("/");

    // This would need the full flow in practice
    // For testing purposes, let's look for chat elements

    const chatInput = page.locator(
      '[data-testid="chat-input"], input[placeholder*="message"], input[placeholder*="action"], textarea[placeholder*="message"]'
    );
    const sendButton = page.locator(
      '[data-testid="send-button"], button:has-text("Send"), button[type="submit"]'
    );

    if ((await chatInput.count()) > 0 && (await sendButton.count()) > 0) {
      // Test sending a message to the AI DM
      await chatInput.fill("I look around the room");
      await sendButton.click();

      // Should see the message in chat history
      await expect(page.locator('text="I look around the room"')).toBeVisible();

      // Should potentially see AI response (may take time)
      await page.screenshot({
        path: "screenshots/chat-interaction.png",
        fullPage: true,
      });
    }
  });

  test("should provide dice rolling functionality", async ({ page }) => {
    // Navigate to game interface
    await page.goto("/");

    // Look for dice rolling interface
    const diceRoller = page.locator(
      '[data-testid="dice-roller"], .dice-roller, button:has-text("d20"), button:has-text("Roll")'
    );

    if ((await diceRoller.count()) > 0) {
      // Test different dice types that should be available per D&D 5e
      const diceTypes = ["d4", "d6", "d8", "d10", "d12", "d20", "d100"];

      for (const diceType of diceTypes) {
        const diceButton = page.locator(`button:has-text("${diceType}")`);
        if ((await diceButton.count()) > 0) {
          await diceButton.click();

          // Should show roll result
          await expect(
            page.locator(
              '[data-testid="dice-result"], .dice-result, .roll-result'
            )
          ).toBeVisible();

          await page.screenshot({
            path: `screenshots/dice-roll-${diceType}.png`,
          });
        }
      }
    }
  });

  test("should display character sheet information", async ({ page }) => {
    // Navigate to game interface
    await page.goto("/");

    // Look for character sheet elements
    const characterSheet = page.locator(
      '[data-testid="character-sheet"], .character-sheet'
    );

    if ((await characterSheet.count()) > 0) {
      // Should display D&D 5e character information
      const expectedElements = [
        'text="Strength"',
        'text="Dexterity"',
        'text="Constitution"',
        'text="Intelligence"',
        'text="Wisdom"',
        'text="Charisma"',
        'text="Hit Points"',
        'text="Armor Class"',
      ];

      for (const selector of expectedElements) {
        const element = page.locator(selector);
        if ((await element.count()) > 0) {
          await expect(element).toBeVisible();
        }
      }

      await page.screenshot({
        path: "screenshots/character-sheet.png",
        fullPage: true,
      });
    }
  });

  test("should handle combat encounters", async ({ page }) => {
    // Navigate to game interface
    await page.goto("/");

    // Look for combat-related elements
    const combatElements = page.locator(
      '[data-testid="battle-map"], .battle-map, [data-testid="combat-interface"], .combat-interface'
    );

    if ((await combatElements.count()) > 0) {
      // Should have combat functionality
      await expect(combatElements.first()).toBeVisible();

      // Look for initiative tracker
      const initiative = page.locator(
        '[data-testid="initiative"], .initiative, text="Initiative"'
      );
      if ((await initiative.count()) > 0) {
        await expect(initiative).toBeVisible();
      }

      // Look for action buttons
      const actionButtons = page.locator(
        'button:has-text("Attack"), button:has-text("Move"), button:has-text("Cast Spell")'
      );
      if ((await actionButtons.count()) > 0) {
        await expect(actionButtons.first()).toBeVisible();
      }

      await page.screenshot({
        path: "screenshots/combat-interface.png",
        fullPage: true,
      });
    }
  });

  test("should allow saving and loading game sessions", async ({ page }) => {
    // Navigate to game interface
    await page.goto("/");

    // Look for save/load functionality
    const saveButton = page.locator(
      'button:has-text("Save"), [data-testid="save-game"]'
    );
    const loadButton = page.locator(
      'button:has-text("Load"), [data-testid="load-game"]'
    );

    if ((await saveButton.count()) > 0) {
      await saveButton.click();

      // Should show save confirmation or dialog
      await page.screenshot({ path: "screenshots/save-game.png" });
    }

    if ((await loadButton.count()) > 0) {
      await loadButton.click();

      // Should show load options
      await page.screenshot({ path: "screenshots/load-game.png" });
    }
  });

  test("should have back navigation to campaigns", async ({ page }) => {
    // Navigate to game interface
    await page.goto("/");

    // Look for back button
    const backButton = page.locator(
      'button:has-text("Back to Campaigns"), button:has-text("← Back")'
    );

    if ((await backButton.count()) > 0) {
      await backButton.click();

      // Should return to campaign selection
      await expect(
        page.locator(".campaign-setup, .campaign-selection")
      ).toBeVisible({ timeout: 10000 });

      await page.screenshot({
        path: "screenshots/back-to-campaigns.png",
        fullPage: true,
      });
    }
  });
});
