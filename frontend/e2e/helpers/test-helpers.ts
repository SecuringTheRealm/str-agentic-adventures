import type { Page } from '@playwright/test';
import { TEST_CAMPAIGNS, TEST_CHARACTERS } from '../constants/srd-data';

/**
 * Helper function to create a test campaign
 * @param page Playwright page object
 * @param campaignData Optional campaign data (uses default if not provided)
 */
export async function createTestCampaign(
  page: Page,
  campaignData?: {
    name?: string;
    setting?: string;
    tone?: string;
    homebrewRules?: string;
  }
): Promise<void> {
  const campaign = campaignData || TEST_CAMPAIGNS.heroic_fantasy;

  // Navigate to home if not already there
  const url = page.url();
  if (!url.includes('localhost') && !url.includes('127.0.0.1')) {
    await page.goto('/');
  }

  // Click create campaign button (if visible)
  const createBtn = page.getByTestId('create-campaign-btn');
  const createBtnCount = await createBtn.count();
  if (createBtnCount > 0) {
    await createBtn.click();
    await page.waitForTimeout(500);
  }

  // Fill campaign form
  await page.getByTestId('campaign-name-input').fill(campaign.name);
  await page.getByTestId('campaign-setting-input').fill(campaign.setting);
  await page.getByTestId('campaign-tone-select').selectOption(campaign.tone);

  if (campaignData?.homebrewRules) {
    await page
      .getByTestId('campaign-homebrew-input')
      .fill(campaignData.homebrewRules);
  }

  // Submit the form
  await page.getByTestId('submit-campaign-btn').click();

  // Wait for character selection screen
  await page.waitForTimeout(2000);
}

/**
 * Helper function to create a test character
 * @param page Playwright page object
 * @param characterType Type of character to create (elf_ranger, dwarf_fighter, human_wizard)
 */
export async function createTestCharacter(
  page: Page,
  characterType: keyof typeof TEST_CHARACTERS = 'elf_ranger'
): Promise<void> {
  const character = TEST_CHARACTERS[characterType];

  // Click create character button
  await page.getByTestId('create-character-btn').click();
  await page.waitForTimeout(1000);

  // Fill basic information
  await page.getByTestId('character-name-input').fill(character.name);
  await page.getByTestId('character-race-select').selectOption(character.race);
  await page
    .getByTestId('character-class-select')
    .selectOption(character.character_class);

  // Fill ability scores
  for (const [ability, score] of Object.entries(character.abilities)) {
    await page.getByTestId(`ability-${ability}`).fill(score.toString());
  }

  // Fill backstory
  await page
    .getByTestId('character-backstory-input')
    .fill(character.backstory);

  // Submit the form
  await page.getByTestId('submit-character-btn').click();

  // Wait for game interface
  await page.waitForTimeout(3000);
}

/**
 * Complete workflow: Create campaign and character
 * @param page Playwright page object
 * @param campaignType Optional campaign type
 * @param characterType Optional character type
 */
export async function setupGameSession(
  page: Page,
  options?: {
    campaignType?: keyof typeof TEST_CAMPAIGNS;
    characterType?: keyof typeof TEST_CHARACTERS;
  }
): Promise<void> {
  const campaignType = options?.campaignType || 'heroic_fantasy';
  const characterType = options?.characterType || 'elf_ranger';

  await page.goto('/');
  await createTestCampaign(page, TEST_CAMPAIGNS[campaignType]);
  await createTestCharacter(page, characterType);
}

/**
 * Send a chat message to the DM
 * @param page Playwright page object
 * @param message Message to send
 */
export async function sendChatMessage(
  page: Page,
  message: string
): Promise<void> {
  await page.getByTestId('chat-input').fill(message);
  await page.getByTestId('chat-send-btn').click();
}

/**
 * Wait for DM response in chat
 * @param page Playwright page object
 * @param timeout Timeout in milliseconds
 */
export async function waitForDMResponse(
  page: Page,
  timeout = 10000
): Promise<void> {
  await page.waitForTimeout(timeout);
}

/**
 * Check if Azure OpenAI is configured
 * @param page Playwright page object
 * @returns true if Azure OpenAI is configured
 */
export async function isAzureConfigured(page: Page): Promise<boolean> {
  try {
    const response = await page.request.get('http://localhost:8000/health');
    const data = await response.json();
    return data.azure_configured === true;
  } catch {
    return false;
  }
}

/**
 * Take a screenshot with a descriptive name
 * @param page Playwright page object
 * @param name Screenshot name
 * @param fullPage Whether to capture full page
 */
export async function takeScreenshot(
  page: Page,
  name: string,
  fullPage = true
): Promise<void> {
  await page.screenshot({
    path: `screenshots/test-run/${name}.png`,
    fullPage,
  });
}
