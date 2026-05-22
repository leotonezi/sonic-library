import { test as setup, expect } from '@playwright/test';
import { testUser } from './fixtures';
import path from 'path';
import fs from 'fs';

const authFile = path.join(__dirname, '.auth/user.json');

setup.beforeAll(() => {
  fs.mkdirSync(path.dirname(authFile), { recursive: true });
});

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(testUser.email);
  await page.getByLabel('Password').fill(testUser.password);
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page).toHaveURL(/.*\/books/, { timeout: 15000 });
  await page.context().storageState({ path: authFile });
});
