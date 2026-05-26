import { test as setup, expect } from '@playwright/test';
import { adminUser } from './fixtures';
import path from 'path';
import fs from 'fs';

const authFile = path.join(__dirname, '.auth/admin.json');

setup.beforeAll(() => {
  fs.mkdirSync(path.dirname(authFile), { recursive: true });
});

setup('authenticate as admin', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(adminUser.email);
  await page.getByLabel('Password').fill(adminUser.password);
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page).toHaveURL(/.*\/books/, { timeout: 15000 });
  await page.context().storageState({ path: authFile });
});
