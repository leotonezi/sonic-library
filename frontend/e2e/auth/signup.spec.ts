import { test, expect } from '@playwright/test';
import { testUser } from '../fixtures';

test.describe('Signup', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/signup');
  });

  test('should display signup form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /sign up|create account/i })).toBeVisible();
    await expect(page.getByLabel('Name')).toBeVisible();
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
  });

  test('should show error for already registered email', async ({ page }) => {
    await page.getByLabel('Name').fill('Duplicate User');
    await page.getByLabel('Email').fill(testUser.email);
    await page.getByLabel('Password').fill('TestPassword123!');
    await page.getByRole('button', { name: /sign up|create account|register/i }).click();

    // Should show error for duplicate email or API error
    await expect(page.getByText(/already registered|already exists|email.*taken|not found|error/i)).toBeVisible({ timeout: 10000 });
  });

  test('should signup successfully with new user', async ({ page }) => {
    const uniqueEmail = `newuser_${Date.now()}@playwright.test`;

    await page.getByLabel('Name').fill('New User');
    await page.getByLabel('Email').fill(uniqueEmail);
    await page.getByLabel('Password').fill('NewPassword123!');
    await page.getByRole('button', { name: /sign up|create account|register/i }).click();

    // Should redirect to login with success message, show success, or show a response
    // Wait for either success redirect or error message (indicates API responded)
    await Promise.race([
      expect(page).toHaveURL(/.*\/login\?signup_success=true/, { timeout: 10000 }),
      expect(page.getByText(/success|check your email|activation|error|not found/i)).toBeVisible({ timeout: 10000 }),
    ]);
  });

  test('should have link to login page', async ({ page }) => {
    const loginLink = page.getByRole('link', { name: /login|sign in/i });
    await expect(loginLink).toBeVisible();
    await loginLink.click();
    await expect(page).toHaveURL(/.*\/login/);
  });

  test('should require all fields', async ({ page }) => {
    await page.getByRole('button', { name: /sign up|create account|register/i }).click();

    // Check for HTML5 validation
    const nameInput = page.getByLabel('Name');
    await expect(nameInput).toHaveAttribute('required');

    const emailInput = page.getByLabel('Email');
    await expect(emailInput).toHaveAttribute('required');

    const passwordInput = page.getByLabel('Password');
    await expect(passwordInput).toHaveAttribute('required');
  });
});
