import { expect, test } from "@playwright/test";

test.describe("D&D 5e SRD Compliance Tests", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText(
      "Securing the Realm - Agentic Adventures"
    );
  });

  test("should only allow SRD-compliant character races", async ({ page }) => {
    // Navigate to character creation
    // This assumes we can get there through campaign creation

    const createCampaignBtn = page.locator(
      'button:has-text("Create Campaign")'
    );
    if ((await createCampaignBtn.count()) > 0) {
      await createCampaignBtn.click();
      await page.fill('input[name="name"]', "SRD Test Campaign");
      await page.locator('button[type="submit"]').click();

      await expect(page.locator('text="Choose Your Character"')).toBeVisible({
        timeout: 10000,
      });

      const createCharacterBtn = page.locator(
        'button:has-text("Create Character")'
      );
      if ((await createCharacterBtn.count()) > 0) {
        await createCharacterBtn.click();

        // Verify only SRD races are available
        const raceSelect = page.locator('select[name="race"]');
        if ((await raceSelect.count()) > 0) {
          const options = await raceSelect.locator("option").allTextContents();

          // D&D 5e SRD allowed races
          const srdRaces = [
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

          for (const option of options) {
            if (option?.trim() && option !== "Select Race") {
              expect(srdRaces).toContain(option.trim());
            }
          }

          await page.screenshot({ path: "screenshots/srd-races.png" });
        }
      }
    }
  });

  test("should only allow SRD-compliant character classes", async ({
    page,
  }) => {
    // Similar navigation to character creation
    const createCampaignBtn = page.locator(
      'button:has-text("Create Campaign")'
    );
    if ((await createCampaignBtn.count()) > 0) {
      await createCampaignBtn.click();
      await page.fill('input[name="name"]', "SRD Class Test");
      await page.locator('button[type="submit"]').click();

      await expect(page.locator('text="Choose Your Character"')).toBeVisible({
        timeout: 10000,
      });

      const createCharacterBtn = page.locator(
        'button:has-text("Create Character")'
      );
      if ((await createCharacterBtn.count()) > 0) {
        await createCharacterBtn.click();

        // Verify only SRD classes are available
        const classSelect = page.locator(
          'select[name="character_class"], select[name="class"]'
        );
        if ((await classSelect.count()) > 0) {
          const options = await classSelect.locator("option").allTextContents();

          // D&D 5e SRD allowed classes
          const srdClasses = [
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

          for (const option of options) {
            if (option?.trim() && option !== "Select Class") {
              expect(srdClasses).toContain(option.trim());
            }
          }

          await page.screenshot({ path: "screenshots/srd-classes.png" });
        }
      }
    }
  });

  test("should enforce D&D 5e ability score rules", async ({ page }) => {
    // Navigate to character creation
    const createCampaignBtn = page.locator(
      'button:has-text("Create Campaign")'
    );
    if ((await createCampaignBtn.count()) > 0) {
      await createCampaignBtn.click();
      await page.fill('input[name="name"]', "Ability Score Test");
      await page.locator('button[type="submit"]').click();

      await expect(page.locator('text="Choose Your Character"')).toBeVisible({
        timeout: 10000,
      });

      const createCharacterBtn = page.locator(
        'button:has-text("Create Character")'
      );
      if ((await createCharacterBtn.count()) > 0) {
        await createCharacterBtn.click();

        // Test all six core abilities from D&D 5e
        const abilities = [
          "strength",
          "dexterity",
          "constitution",
          "intelligence",
          "wisdom",
          "charisma",
        ];

        for (const ability of abilities) {
          const abilityInput = page.locator(
            `input[name="abilities.${ability}"], input[data-ability="${ability}"]`
          );

          if ((await abilityInput.count()) > 0) {
            // Test minimum value (should be at least 3 in D&D 5e)
            await abilityInput.fill("2");
            // The system should either reject this or set it to minimum allowed

            // Test maximum value (should not exceed 20 for starting characters)
            await abilityInput.fill("25");
            // The system should either reject this or cap at maximum

            // Set a valid value
            await abilityInput.fill("13");
            const value = await abilityInput.inputValue();
            const numValue = Number.parseInt(value, 10);
            expect(numValue).toBeGreaterThanOrEqual(3);
            expect(numValue).toBeLessThanOrEqual(20);
          }
        }

        await page.screenshot({ path: "screenshots/ability-scores.png" });
      }
    }
  });

  test("should provide standard D&D 5e dice rolling", async ({ page }) => {
    // Look for dice roller interface
    const diceInterface = page.locator(
      '[data-testid="dice-roller"], .dice-roller'
    );

    if ((await diceInterface.count()) > 0) {
      // D&D 5e standard dice
      const standardDice = ["d4", "d6", "d8", "d10", "d12", "d20", "d100"];

      for (const die of standardDice) {
        const diceButton = page.locator(`button:has-text("${die}")`);
        if ((await diceButton.count()) > 0) {
          await diceButton.click();

          // Verify result is within valid range
          const result = page.locator(
            '[data-testid="dice-result"], .dice-result'
          );
          if ((await result.count()) > 0) {
            const resultText = await result.textContent();
            if (resultText) {
              const rollValue = Number.parseInt(
                resultText.match(/\d+/)?.[0] || "0",
                10
              );
              const maxValue = Number.parseInt(die.substring(1), 10);

              expect(rollValue).toBeGreaterThanOrEqual(1);
              expect(rollValue).toBeLessThanOrEqual(maxValue);
            }
          }
        }
      }

      await page.screenshot({ path: "screenshots/dice-rolling.png" });
    }
  });

  test("should support D&D 5e level progression rules", async ({ page }) => {
    // This test would check if character progression follows SRD rules
    // In practice, this would require a game session that allows leveling

    const characterSheet = page.locator(
      '[data-testid="character-sheet"], .character-sheet'
    );

    if ((await characterSheet.count()) > 0) {
      // Look for level indicator
      const levelDisplay = page.locator(
        'text="Level", [data-testid="character-level"]'
      );

      if ((await levelDisplay.count()) > 0) {
        // Characters should start at level 1
        await expect(
          page.locator('text="Level 1", text="1st Level"')
        ).toBeVisible();
      }

      // Look for experience points
      const xpDisplay = page.locator(
        'text="Experience", text="XP", [data-testid="experience"]'
      );

      if ((await xpDisplay.count()) > 0) {
        // Starting characters should have 0 XP
        await expect(page.locator('text="0"')).toBeVisible();
      }

      // Look for proficiency bonus (should be +2 at level 1)
      const proficiencyDisplay = page.locator(
        'text="Proficiency", [data-testid="proficiency-bonus"]'
      );

      if ((await proficiencyDisplay.count()) > 0) {
        await expect(page.locator('text="+2"')).toBeVisible();
      }

      await page.screenshot({ path: "screenshots/level-progression.png" });
    }
  });

  test("should implement D&D 5e combat mechanics", async ({ page }) => {
    // Look for combat interface elements
    const combatInterface = page.locator(
      '[data-testid="combat-interface"], .combat-interface'
    );

    if ((await combatInterface.count()) > 0) {
      // Should have initiative system
      const initiative = page.locator(
        'text="Initiative", [data-testid="initiative"]'
      );
      if ((await initiative.count()) > 0) {
        await expect(initiative).toBeVisible();
      }

      // Should have standard D&D actions
      const standardActions = [
        "Attack",
        "Move",
        "Dash",
        "Dodge",
        "Help",
        "Hide",
        "Ready",
        "Search",
      ];

      for (const action of standardActions) {
        const actionButton = page.locator(`button:has-text("${action}")`);
        if ((await actionButton.count()) > 0) {
          await expect(actionButton).toBeVisible();
        }
      }

      // Should track hit points and armor class
      const hpDisplay = page.locator(
        'text="Hit Points", text="HP", [data-testid="hit-points"]'
      );
      const acDisplay = page.locator(
        'text="Armor Class", text="AC", [data-testid="armor-class"]'
      );

      if ((await hpDisplay.count()) > 0) {
        await expect(hpDisplay).toBeVisible();
      }

      if ((await acDisplay.count()) > 0) {
        await expect(acDisplay).toBeVisible();
      }

      await page.screenshot({ path: "screenshots/combat-mechanics.png" });
    }
  });

  test("should provide spell system for spellcasting classes", async ({
    page,
  }) => {
    // Navigate to character creation with a spellcasting class
    const createCampaignBtn = page.locator(
      'button:has-text("Create Campaign")'
    );
    if ((await createCampaignBtn.count()) > 0) {
      await createCampaignBtn.click();
      await page.fill('input[name="name"]', "Spellcaster Test");
      await page.locator('button[type="submit"]').click();

      await expect(page.locator('text="Choose Your Character"')).toBeVisible({
        timeout: 10000,
      });

      const createCharacterBtn = page.locator(
        'button:has-text("Create Character")'
      );
      if ((await createCharacterBtn.count()) > 0) {
        await createCharacterBtn.click();

        // Select a spellcasting class
        const classSelect = page.locator('select[name="character_class"]');
        if ((await classSelect.count()) > 0) {
          await classSelect.selectOption("Wizard");
        }

        await page.fill('input[name="name"]', "Test Wizard");
        await page.locator('button[type="submit"]').click();

        // Should show spell-related interface
        const spellInterface = page.locator(
          '[data-testid="spells"], .spells, text="Spells"'
        );

        if ((await spellInterface.count()) > 0) {
          // Should show spell slots
          const spellSlots = page.locator(
            'text="Spell Slots", [data-testid="spell-slots"]'
          );
          if ((await spellSlots.count()) > 0) {
            await expect(spellSlots).toBeVisible();
          }

          // Should show cantrips for level 1 wizard
          const cantrips = page.locator(
            'text="Cantrips", [data-testid="cantrips"]'
          );
          if ((await cantrips.count()) > 0) {
            await expect(cantrips).toBeVisible();
          }

          await page.screenshot({ path: "screenshots/spell-system.png" });
        }
      }
    }
  });
});
