import { test, expect } from '@playwright/test';
import { API_URL } from '../fixtures';

test.describe('Add Book to Library', () => {
  test('should add a book from popular list to library and verify it appears', async ({ page }) => {
    let addedUserBookId: number | null = null;
    let externalId: string | null = null;

    await page.goto('/books');

    // Wait for the /books/popular API response — the list renders only after
    // React's useEffect fires, which can happen after networkidle.
    await page.waitForResponse(
      (res) => res.url().includes('/books/popular') && res.ok(),
      { timeout: 15000 },
    );

    const firstBookLink = page.locator('a[href*="/books/external/"]').first();
    await expect(firstBookLink).toBeVisible({ timeout: 10000 });

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

    // Click "Add to Reading List"
    const addButton = page.getByRole('button', { name: 'Add to Reading List' });
    await expect(addButton).toBeVisible({ timeout: 10000 });
    await addButton.click();

    // Verify success toast — confirms the POST /user-books returned 201
    await expect(page.getByText('Added to Reading List!')).toBeVisible({ timeout: 10000 });

    // Fetch the created user-book ID for cleanup (avoids fragile waitForResponse status check)
    if (externalId) {
      const userBookRes = await page.request.get(`${API_URL}/user-books/book/external/${externalId}`);
      if (userBookRes.ok()) {
        const data = await userBookRes.json();
        addedUserBookId = data?.data?.id ?? null;
      }
    }

    // Navigate to library and confirm book appears
    await page.goto('/library');
    await page.waitForResponse(
      (res) => res.url().includes('/user-books/my-books') && res.ok(),
      { timeout: 15000 },
    );
    await expect(page.getByText(bookTitle, { exact: false })).toBeVisible({ timeout: 10000 });

    // Cleanup: remove the added book so future runs start clean
    if (addedUserBookId) {
      await page.request.delete(`${API_URL}/user-books/${addedUserBookId}`);
    }
  });
});
