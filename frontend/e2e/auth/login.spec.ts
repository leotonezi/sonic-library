import { test, expect } from '@playwright/test';
import { testUser, invalidUser } from '../fixtures';

test.describe('Login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.getByLabel('Email').fill(invalidUser.email);
    await page.getByLabel('Password').fill(invalidUser.password);
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Wait for error message
    await expect(page.getByText(/invalid|incorrect|failed/i)).toBeVisible({ timeout: 10000 });
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.getByLabel('Email').fill(testUser.email);
    await page.getByLabel('Password').fill(testUser.password);
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Should redirect to books page
    await expect(page).toHaveURL(/.*\/books/, { timeout: 15000 });
  });

  test('should have link to signup page', async ({ page }) => {
    const signupLink = page.getByRole('link', { name: /sign up/i });
    await expect(signupLink).toBeVisible();
    await signupLink.click();
    await expect(page).toHaveURL(/.*\/signup/);
  });

  test('should require email and password fields', async ({ page }) => {
    // Try to submit empty form
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Check for HTML5 validation (form should not submit)
    const emailInput = page.getByLabel('Email');
    await expect(emailInput).toHaveAttribute('required');

    const passwordInput = page.getByLabel('Password');
    await expect(passwordInput).toHaveAttribute('required');
  });
});
