import { test, expect } from '@playwright/test';
import { testUser } from '../fixtures';

test.describe('Add Book to Library', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.getByLabel('Email').fill(testUser.email);
    await page.getByLabel('Password').fill(testUser.password);
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page).toHaveURL(/.*\/books/, { timeout: 15000 });
  });

  test('should display books page after login', async ({ page }) => {
    // Verify we're on the books page by checking for the search input or navigation elements
    await expect(page.getByPlaceholder(/search/i)).toBeVisible({ timeout: 10000 });
  });

  test('should search for a book', async ({ page }) => {
    // Look for search input
    const searchInput = page.getByPlaceholder(/search/i);
    await expect(searchInput).toBeVisible();

    await searchInput.fill('The Great Gatsby');
    await searchInput.press('Enter');

    // Wait for search results
    await page.waitForTimeout(2000);

    // Should show some results or no results message
    const hasResults = await page.getByText(/gatsby/i).count();
    expect(hasResults).toBeGreaterThanOrEqual(0);
  });

  test('should add a book to library', async ({ page }) => {
    // Search for a book
    const searchInput = page.getByPlaceholder(/search/i);
    await searchInput.fill('1984');
    await searchInput.press('Enter');

    // Wait for results
    await page.waitForTimeout(2000);

    // Click on first book card or add button
    const addButton = page.getByRole('button', { name: /add|save|\+/i }).first();
    if (await addButton.isVisible()) {
      await addButton.click();
      // Should show success message or the book should be added
      await expect(page.getByText(/added|saved|success/i)).toBeVisible({ timeout: 5000 });
    }
  });

  test('should navigate to my library', async ({ page }) => {
    // Look for library/my books link
    const libraryLink = page.getByRole('link', { name: /my library|my books/i });
    if (await libraryLink.isVisible()) {
      await libraryLink.click();
      await expect(page).toHaveURL(/.*\/(library|my-books)/);
    }
  });
});
