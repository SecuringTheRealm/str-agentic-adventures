import { test, expect } from '@playwright/test';

test.describe('Application Health Check', () => {
  test('should load and respond to basic requests', async ({ page }) => {
    // Basic health check - ensure the app loads
    await page.goto('/');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check that the main heading is present
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
    await expect(heading).toContainText('Securing the Realm');
    
    // Take a screenshot for documentation
    await page.screenshot({ path: 'screenshots/health-check.png' });
    
    console.log('✅ Application health check passed');
  });
  
  test('should have proper page structure', async ({ page }) => {
    await page.goto('/');
    
    // Check for basic HTML structure
    await expect(page.locator('html')).toBeVisible();
    await expect(page.locator('head title')).toHaveText(/Securing the Realm/);
    
    // Check for React app structure
    await expect(page.locator('#root')).toBeVisible();
    
    console.log('✅ Page structure validation passed');
  });
});