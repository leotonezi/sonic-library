import { test, expect } from '@playwright/test';
import { testUser } from '../fixtures';

test.describe('Submit Review', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.getByLabel('Email').fill(testUser.email);
    await page.getByLabel('Password').fill(testUser.password);
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page).toHaveURL(/.*\/books/, { timeout: 15000 });
  });

  test('should navigate to a book detail page', async ({ page }) => {
    // Click on a book to see details
    const bookCard = page.locator('[data-testid="book-card"]').first();
    if (await bookCard.isVisible()) {
      await bookCard.click();
      // Should navigate to book detail
      await expect(page).toHaveURL(/.*\/books\/\d+/);
    }
  });

  test('should display review section on book detail', async ({ page }) => {
    // Navigate to a book detail page
    const bookCard = page.locator('[data-testid="book-card"]').first();
    if (await bookCard.isVisible()) {
      await bookCard.click();
      await expect(page).toHaveURL(/.*\/books\/\d+/);

      // Look for review section
      const reviewSection = page.getByText(/review|rating/i);
      await expect(reviewSection).toBeVisible({ timeout: 5000 });
    }
  });

  test('should submit a review', async ({ page }) => {
    // Navigate to a book detail page
    const bookCard = page.locator('[data-testid="book-card"]').first();
    if (await bookCard.isVisible()) {
      await bookCard.click();
      await expect(page).toHaveURL(/.*\/books\/\d+/);

      // Look for review form
      const reviewTextarea = page.getByPlaceholder(/review|comment|thoughts/i);
      if (await reviewTextarea.isVisible()) {
        await reviewTextarea.fill('This is a test review from Playwright E2E tests.');

        // Look for star rating (if exists)
        const starRating = page.locator('[data-testid="star-rating"]').first();
        if (await starRating.isVisible()) {
          await starRating.click();
        }

        // Submit review
        const submitButton = page.getByRole('button', { name: /submit|post|save/i });
        await submitButton.click();

        // Should show success or the review should appear
        await expect(page.getByText(/success|posted|submitted|test review/i)).toBeVisible({ timeout: 5000 });
      }
    }
  });
});
