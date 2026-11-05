import { expect, test } from '@playwright/test';
test('63 resources visible, categories, search and theme', async ({page}) => {
  await page.goto('/');
  await expect(page.getByRole('status')).toContainText('63 de 63');
  await expect(page.locator('[data-testid^="icon-"]')).toHaveCount(63);
  await page.getByTestId('category').selectOption('interfaz');
  await expect(page.locator('[data-testid^="icon-"]')).toHaveCount(35);
  await page.getByTestId('category').selectOption('all');
  await page.getByTestId('search').fill('micrófono');
  await expect(page.getByTestId('icon-microphone')).toBeVisible();
  await page.getByTestId('theme').selectOption('dark');
  await expect(page.locator('.laboratory')).toHaveClass(/bc-theme-dark/);
});
test('optical size and accessible states', async ({page}) => {
  await page.goto('/');
  await page.getByTestId('size').selectOption('16');
  await expect(page.getByTestId('icon-microphone').locator('[data-variant]')).toHaveAttribute('data-variant','compact');
  await page.getByTestId('size').selectOption('48');
  await expect(page.getByTestId('icon-microphone').locator('[data-variant]')).toHaveAttribute('data-variant','large');
  await page.getByTestId('state').selectOption('listening');
  await expect(page.getByTestId('icon-microphone').locator('[data-state]')).toHaveAttribute('data-state','listening');
  await expect(page.getByTestId('icon-settings').locator('[data-state]')).toHaveAttribute('data-state','idle');
  await page.getByLabel('Reducir movimiento').check();
  await expect(page.locator('.laboratory')).toHaveClass(/bc-reduced-motion/);
});
