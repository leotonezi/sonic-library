import { test, expect } from '@playwright/test';

test.describe('Admin dashboard tab validation', () => {
  test('should show error for invalid tab param', async ({ page }) => {
    await page.goto('/admin?tab=hax');

    await expect(page.getByText('Invalid tab: hax')).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: 'Go to dashboard' })).toBeVisible();
  });

  test('should reset to default when clicking Go to dashboard', async ({ page }) => {
    await page.goto('/admin?tab=hax');

    await expect(page.getByText('Invalid tab: hax')).toBeVisible({ timeout: 10000 });
    await page.getByRole('button', { name: 'Go to dashboard' }).click();

    await expect(page).toHaveURL(/\/admin$/, { timeout: 10000 });
    await expect(page.getByText('Invalid tab: hax')).not.toBeVisible();
  });

  test('should render users table for valid tab', async ({ page }) => {
    await page.goto('/admin?tab=users');

    await expect(page.getByText('Invalid tab:')).not.toBeVisible();
    await expect(page.getByRole('heading', { name: 'Admin Dashboard' })).toBeVisible({ timeout: 10000 });
  });

  test('should render reviews table for valid reviews tab', async ({ page }) => {
    await page.goto('/admin?tab=reviews');

    await expect(page.getByText('Invalid tab:')).not.toBeVisible();
    await expect(page.getByRole('heading', { name: 'Admin Dashboard' })).toBeVisible({ timeout: 10000 });
  });
});
