<script lang="ts">
  import { ASSET_REGISTRY, type BeCallAssetName } from './registry';
  import { assetSvg } from './svg-source';
  export let name: BeCallAssetName;
  export let size = 72;
  export let decorative = false;
  export let label: string | undefined = undefined;
  export let className = '';
  $: entry = ASSET_REGISTRY[name];
  $: markup = assetSvg(name);
</script>
<span
  class={`bc-icon-host bc-static-asset ${className}`}
  data-icon={name}
  style={`width:${size}px;height:${size}px;`}
  role={decorative ? undefined : 'img'}
  aria-hidden={decorative ? 'true' : undefined}
  aria-label={decorative ? undefined : (label ?? entry.label)}
>
  {@html markup}
</span>
