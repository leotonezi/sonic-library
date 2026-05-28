import { test, expect } from '@playwright/test';

test.describe('Submit Review', () => {
  test('should navigate to a book detail page', async ({ page }) => {
    await page.goto('/books');
    const bookCard = page.locator('[data-testid="book-card"]').first();
    if (await bookCard.isVisible()) {
      await bookCard.click();
      await expect(page).toHaveURL(/.*\/books\/\d+/);
    }
  });

  test('should display review section on book detail', async ({ page }) => {
    await page.goto('/books');
    const bookCard = page.locator('[data-testid="book-card"]').first();
    if (await bookCard.isVisible()) {
      await bookCard.click();
      await expect(page).toHaveURL(/.*\/books\/\d+/);

      const reviewSection = page.getByText(/review|rating/i);
      await expect(reviewSection).toBeVisible({ timeout: 5000 });
    }
  });

  test('should render book info before reviews section streams in', async ({ page }) => {
    await page.goto('/books');
    const bookCard = page.locator('[data-testid="book-card"]').first();
    if (!(await bookCard.isVisible())) return;
    await bookCard.click();
    await expect(page).toHaveURL(/.*\/books\/\d+/);

    // Book title (server-renders without waiting for reviews)
    const bookTitle = page.locator('h1').first();
    await expect(bookTitle).toBeVisible({ timeout: 5000 });

    // Reviews section eventually streams in (skeleton resolves)
    await expect(page.getByText('Reviews')).toBeVisible({ timeout: 10000 });
  });

  test('should submit a review', async ({ page }) => {
    await page.goto('/books');
    const bookCard = page.locator('[data-testid="book-card"]').first();
    if (await bookCard.isVisible()) {
      await bookCard.click();
      await expect(page).toHaveURL(/.*\/books\/\d+/);

      const reviewTextarea = page.getByPlaceholder(/review|comment|thoughts/i);
      if (await reviewTextarea.isVisible()) {
        await reviewTextarea.fill('This is a test review from Playwright E2E tests.');

        const starRating = page.locator('[data-testid="star-rating"]').first();
        if (await starRating.isVisible()) {
          await starRating.click();
        }

        const submitButton = page.getByRole('button', { name: /submit|post|save/i });
        await submitButton.click();

        await expect(page.getByText(/success|posted|submitted|test review/i)).toBeVisible({ timeout: 5000 });
      }
    }
  });
});
