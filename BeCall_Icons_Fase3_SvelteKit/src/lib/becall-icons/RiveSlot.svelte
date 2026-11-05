<script lang="ts">
  import type { Action } from 'svelte/action';
  import BeCallIcon from './BeCallIcon.svelte';
  import type { BeCallIconName, IconState } from './registry';
  import type { RiveDriver, RiveStartOptions } from './rive-contract';

  export let name: BeCallIconName;
  export let state: IconState = 'idle';
  export let size = 48;
  export let driver: RiveDriver | undefined = undefined;
  export let reducedMotion = false;

  // A Svelte action runs only in the browser. It is destroyed if the
  // component switches to its accessible, reduced-motion SVG fallback.
  const mountRive: Action<HTMLSpanElement, RiveStartOptions> = (node, options) => {
    const instance = driver;
    const cleanup = instance?.mount(node, options);
    return {
      update(next) { instance?.setState?.(next.state); },
      destroy() { if (typeof cleanup === 'function') cleanup(); }
    };
  };
</script>

{#if driver && !reducedMotion}
  <span
    use:mountRive={{name,state,size,reducedMotion}}
    class="bc-rive-slot"
    role="img"
    aria-label={name}
    style={`width:${size}px;height:${size}px`}
  ></span>
{:else}
  <BeCallIcon {name} {state} {size} animated={!reducedMotion}/>
{/if}
