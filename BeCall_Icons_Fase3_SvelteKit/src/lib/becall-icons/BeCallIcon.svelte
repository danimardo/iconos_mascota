<script lang="ts">
  import { UI_REGISTRY, opticalVariant, type BeCallIconName, type IconState, type OpticalVariant } from './registry';
  import { iconSvg } from './svg-source';

  export let name: BeCallIconName;
  export let size = 24;
  export let variant: OpticalVariant | undefined = undefined;
  export let state: IconState = 'idle';
  /** Animations only run on real state or user interaction, never just because mounted. */
  export let animated = true;
  export let interactive = false;
  export let decorative = false;
  export let label: string | undefined = undefined;
  export let color: string | undefined = undefined;
  export let className = '';

  $: entry = UI_REGISTRY[name];
  $: detail = variant ?? opticalVariant(size);
  $: markup = iconSvg(name, detail);
  $: animationActive = animated && !['idle', 'disabled', 'paused', 'disconnected', 'muted', 'hover', 'pressed', 'focus', 'selected'].includes(state);
  $: hostClass = `bc-icon-host ${className} ${interactive ? 'bc-interactive' : ''} bc-state-${state} ${animationActive ? 'bc-motion-on' : ''}`;
</script>

<span
  class={hostClass}
  data-icon={name}
  data-state={state}
  data-variant={detail}
  style={`width:${size}px;height:${size}px;${color ? `--bc-primary:${color};` : ''}`}
  role={decorative ? undefined : 'img'}
  aria-hidden={decorative ? 'true' : undefined}
  aria-label={decorative ? undefined : (label ?? entry.label)}
>
  {@html markup}
</span>
