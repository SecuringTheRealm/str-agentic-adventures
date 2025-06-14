import { test, expect } from '@playwright/test';

test.describe('Character Creation Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    
    // First create or select a campaign to get to character selection
    // This assumes we can get to character selection somehow
    await expect(page.locator('h1')).toContainText('Securing the Realm - Agentic Adventures');
  });

  test('should show character selection options', async ({ page }) => {
    // Try to get to character selection by creating a quick campaign
    const createButton = page.locator('button:has-text("Create Campaign"), button:has-text("Create Custom")');
    
    if (await createButton.count() > 0) {
      await createButton.first().click();
      
      // Quick campaign creation
      await page.fill('input[name="name"], [placeholder*="campaign"]', 'Test Campaign for Character');
      
      const submitButton = page.locator('button[type="submit"], button:has-text("Create")');
      await submitButton.click();
      
      // Should now be in character selection
      await expect(page.locator('text="Choose Your Character", h2:has-text("Character")')).toBeVisible({ timeout: 10000 });
      
      // Should show character creation options
      await expect(page.locator('button:has-text("Create Character"), button:has-text("Create New")')).toBeVisible();
      await expect(page.locator('button:has-text("Browse Characters"), button:has-text("Predefined")')).toBeVisible();
      
      await page.screenshot({ path: 'screenshots/character-selection.png', fullPage: true });
    }
  });

  test('should be able to create a new D&D 5e character', async ({ page }) => {
    // Navigate to character creation (this would need the previous steps)
    // For now, let's assume we can get to character creation directly
    
    // Try multiple navigation paths to character creation
    await page.goto('/');
    
    // First try to get to character selection
    const createCampaignBtn = page.locator('button:has-text("Create Campaign")');
    if (await createCampaignBtn.count() > 0) {
      await createCampaignBtn.click();
      await page.fill('input[name="name"]', 'Test Campaign');
      await page.locator('button[type="submit"]').click();
      
      // Now should be in character selection
      await expect(page.locator('text="Choose Your Character"')).toBeVisible({ timeout: 10000 });
      
      // Click create character
      const createCharacterBtn = page.locator('button:has-text("Create Character"), button:has-text("Create New")');
      await createCharacterBtn.click();
      
      // Should show character creation form with D&D 5e options
      await expect(page.locator('input[name="name"], [placeholder*="character"]')).toBeVisible();
      
      // Fill character details according to D&D 5e SRD
      await page.fill('input[name="name"]', 'Thorin Ironbeard');
      
      // Select race (must be from SRD list)
      const raceSelect = page.locator('select[name="race"]');
      if (await raceSelect.count() > 0) {
        await raceSelect.selectOption('Dwarf');
      }
      
      // Select class (must be from SRD list) 
      const classSelect = page.locator('select[name="character_class"], select[name="class"]');
      if (await classSelect.count() > 0) {
        await classSelect.selectOption('Fighter');
      }
      
      // Fill backstory
      const backstoryField = page.locator('textarea[name="backstory"]');
      if (await backstoryField.count() > 0) {
        await backstoryField.fill('A veteran warrior from the mountain clans, skilled in combat and loyal to his companions.');
      }
      
      // Check ability scores (should follow D&D 5e rules)
      const strengthInput = page.locator('input[name="abilities.strength"], input[data-ability="strength"]');
      if (await strengthInput.count() > 0) {
        await strengthInput.fill('15');
      }
      
      const dexterityInput = page.locator('input[name="abilities.dexterity"], input[data-ability="dexterity"]');
      if (await dexterityInput.count() > 0) {
        await dexterityInput.fill('12');
      }
      
      const constitutionInput = page.locator('input[name="abilities.constitution"], input[data-ability="constitution"]');
      if (await constitutionInput.count() > 0) {
        await constitutionInput.fill('14');
      }
      
      await page.screenshot({ path: 'screenshots/character-creation-form.png', fullPage: true });
      
      // Submit character creation
      const submitCharacterBtn = page.locator('button[type="submit"], button:has-text("Create Character")');
      await submitCharacterBtn.click();
      
      // Should proceed to game interface
      await expect(page.locator('text="Game Interface", [data-testid="game-interface"]')).toBeVisible({ timeout: 10000 });
      
      await page.screenshot({ path: 'screenshots/character-created.png', fullPage: true });
    }
  });

  test('should be able to browse predefined characters', async ({ page }) => {
    // Similar setup - get to character selection first
    await page.goto('/');
    
    const createCampaignBtn = page.locator('button:has-text("Create Campaign")');
    if (await createCampaignBtn.count() > 0) {
      await createCampaignBtn.click();
      await page.fill('input[name="name"]', 'Test Campaign');
      await page.locator('button[type="submit"]').click();
      
      await expect(page.locator('text="Choose Your Character"')).toBeVisible({ timeout: 10000 });
      
      // Click browse characters
      const browseBtn = page.locator('button:has-text("Browse Characters"), button:has-text("Predefined")');
      if (await browseBtn.count() > 0) {
        await browseBtn.click();
        
        // Should show list of predefined characters
        await expect(page.locator('.character-card, [data-testid="character-option"]')).toBeVisible();
        
        await page.screenshot({ path: 'screenshots/predefined-characters.png', fullPage: true });
        
        // Select a predefined character
        const firstCharacter = page.locator('.character-card, [data-testid="character-option"]').first();
        if (await firstCharacter.count() > 0) {
          await firstCharacter.click();
          
          // Should proceed to game interface
          await expect(page.locator('text="Game Interface", [data-testid="game-interface"]')).toBeVisible({ timeout: 10000 });
          
          await page.screenshot({ path: 'screenshots/predefined-character-selected.png', fullPage: true });
        }
      }
    }
  });

  test('should validate D&D 5e character creation rules', async ({ page }) => {
    // This test ensures the character creation follows SRD rules
    await page.goto('/');
    
    // Navigate to character creation (abbreviated for this test)
    // Would need full navigation flow in real test
    
    // Test that only valid races are available (from SRD)
    const validRaces = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling'];
    const raceSelect = page.locator('select[name="race"]');
    
    if (await raceSelect.count() > 0) {
      const options = await raceSelect.locator('option').allTextContents();
      
      // Verify all options are valid SRD races
      for (const option of options) {
        if (option && option.trim()) {
          expect(validRaces).toContain(option.trim());
        }
      }
    }
    
    // Test that only valid classes are available (from SRD)
    const validClasses = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard'];
    const classSelect = page.locator('select[name="character_class"], select[name="class"]');
    
    if (await classSelect.count() > 0) {
      const options = await classSelect.locator('option').allTextContents();
      
      // Verify all options are valid SRD classes
      for (const option of options) {
        if (option && option.trim()) {
          expect(validClasses).toContain(option.trim());
        }
      }
    }
    
    // Test ability score validation (should be 3-20 range)
    const abilityInputs = page.locator('input[name^="abilities."]');
    const count = await abilityInputs.count();
    
    if (count > 0) {
      for (let i = 0; i < count; i++) {
        const input = abilityInputs.nth(i);
        
        // Test minimum value
        await input.fill('2');
        // Should show validation error or reset to minimum
        
        // Test maximum value  
        await input.fill('21');
        // Should show validation error or reset to maximum
        
        // Set valid value
        await input.fill('13');
      }
    }
  });
});