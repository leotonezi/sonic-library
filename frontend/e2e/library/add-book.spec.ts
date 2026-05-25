import { test, expect } from '@playwright/test';
import { API_URL } from '../fixtures';

test.describe('Add Book to Library', () => {
  test('should add a book from popular list to library and verify it appears', async ({ page }) => {
    let addedUserBookId: number | null = null;
    let externalId: string | null = null;

    await page.goto('/books');
    await page.waitForLoadState('networkidle');

    // Wait for popular books to render
    const firstBookLink = page.locator('ul li a').first();
    await expect(firstBookLink).toBeVisible({ timeout: 15000 });

    // Extract external ID from the href for pre-cleanup
    const href = await firstBookLink.getAttribute('href');
    externalId = href?.split('/').pop() ?? null;

    // Pre-cleanup: remove book from library if already added from a previous run
    if (externalId) {
      const existing = await page.request.get(`${API_URL}/user-books/book/external/${externalId}`);
      if (existing.ok()) {
        const existingData = await existing.json();
        const existingId = existingData?.data?.id;
        if (existingId) {
          await page.request.delete(`${API_URL}/user-books/${existingId}`);
        }
      }
    }

    // Navigate to the book detail page
    await firstBookLink.click();
    await page.waitForLoadState('domcontentloaded');

    // Store title for later assertion
    const bookTitle = await page.locator('h1').first().innerText();

    // Listen for the POST /user-books response before clicking
    const addBookResponse = page.waitForResponse(
      (res) =>
        res.url().includes('/user-books') &&
        res.request().method() === 'POST' &&
        res.status() === 201,
    );

    // Click "Add to Reading List"
    const addButton = page.getByRole('button', { name: 'Add to Reading List' });
    await expect(addButton).toBeVisible({ timeout: 10000 });
    await addButton.click();

    // Capture returned user_book id for cleanup
    const res = await addBookResponse;
    const json = await res.json();
    addedUserBookId = json?.data?.id ?? null;

    // Verify success toast
    await expect(page.getByText('Added to Reading List!')).toBeVisible({ timeout: 8000 });

    // Navigate to library and confirm book appears
    await page.goto('/library');
    await page.waitForLoadState('networkidle');
    await expect(page.getByText(bookTitle, { exact: false })).toBeVisible({ timeout: 10000 });

    // Cleanup: remove the added book so future runs start clean
    if (addedUserBookId) {
      await page.request.delete(`${API_URL}/user-books/${addedUserBookId}`);
    }
  });
});
