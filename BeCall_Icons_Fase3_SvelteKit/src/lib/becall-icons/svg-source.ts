import type { BeCallIconName, BeCallAssetName, OpticalVariant } from './registry';
import { UI_REGISTRY, ASSET_REGISTRY } from './registry';
/** All imports are statically bundled by Vite; no HTTP request or user-controlled SVG URLs. */
const raw = import.meta.glob('./svg/**/*.svg', {
  eager: true, query: '?raw', import: 'default'
}) as Record<string, string>;
const cache = new Map<string, string>();
function trustedInline(key: string): string {
  const cached = cache.get(key);
  if (cached) return cached;
  const markup = raw[key];
  if (!markup) throw new Error(`Falta SVG aprobado: ${key}`);
  // The icons come exclusively from the bundled, locally reviewed assets.
  // Do not call this function with arbitrary user-supplied or remote SVGs.
  const prepared = markup
    .replace(/<title\b[^>]*>[\s\S]*?<\/title>/g, '')
    .replace(/\srole="img"/g, '')
    .replace(/\saria-label="[^"]*"/g, '')
    .replace(/<svg\b/, '<svg aria-hidden="true" focusable="false"');
  cache.set(key, prepared);
  return prepared;
}
export function iconSvg(name: BeCallIconName, variant: OpticalVariant): string {
  const entry = UI_REGISTRY[name];
  const suffix = variant === 'standard' ? '' : `.${variant}`;
  return trustedInline(`./svg/${entry.category}/${entry.originalName}${suffix}.svg`);
}
export function assetSvg(name: BeCallAssetName): string {
  const entry = ASSET_REGISTRY[name];
  return trustedInline(`./svg/${entry.category}/${entry.originalName}.svg`);
}
