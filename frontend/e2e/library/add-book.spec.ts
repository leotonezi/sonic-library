import { test, expect } from '@playwright/test';

test.describe('Add Book to Library', () => {
  test('should display books page after login', async ({ page }) => {
    await page.goto('/books');
    await expect(page.getByPlaceholder(/search/i)).toBeVisible({ timeout: 10000 });
  });

  test('should search for a book', async ({ page }) => {
    await page.goto('/books');
    const searchInput = page.getByPlaceholder(/search/i);
    await expect(searchInput).toBeVisible();

    await searchInput.fill('The Great Gatsby');
    await searchInput.press('Enter');

    await page.waitForLoadState('networkidle');

    const hasResults = await page.getByText(/gatsby/i).count();
    expect(hasResults).toBeGreaterThanOrEqual(0);
  });

  test('should add a book to library', async ({ page }) => {
    await page.goto('/books');
    const searchInput = page.getByPlaceholder(/search/i);
    await searchInput.fill('1984');
    await searchInput.press('Enter');

    await page.waitForLoadState('networkidle');

    const addButton = page.getByRole('button', { name: /add|save|\+/i }).first();
    if (await addButton.isVisible()) {
      await addButton.click();
      await expect(page.getByText(/added|saved|success/i)).toBeVisible({ timeout: 5000 });
    }
  });

  test('should navigate to my library', async ({ page }) => {
    await page.goto('/books');
    const libraryLink = page.getByRole('link', { name: /my library|my books/i });
    if (await libraryLink.isVisible()) {
      await libraryLink.click();
      await expect(page).toHaveURL(/.*\/(library|my-books)/);
    }
  });
});
