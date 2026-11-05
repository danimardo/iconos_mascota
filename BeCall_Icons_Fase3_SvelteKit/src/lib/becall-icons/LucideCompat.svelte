<script lang="ts">
  import BeCallIcon from './BeCallIcon.svelte';
  import { resolveLegacy, type IconState } from './registry';
  /** Gradual bridge only. Does not intercept imports from lucide-svelte automatically. */
  export let name: string;
  export let size = 24;
  export let state: IconState = 'idle';
  export let animated = true;
  export let color: string | undefined = undefined;
  export let className = '';
  export let decorative = false;
  export let label: string | undefined = undefined;
  $: mapped = resolveLegacy(name);
</script>
{#if mapped}
  <BeCallIcon name={mapped} {size} {state} {animated} {color} {className} {decorative} {label}/>
{:else}
  <!-- Deliberately fail visibly in the lab; no invented icon substitution. -->
  <span class="bc-unknown-icon" data-missing-lucide={name} role="img" aria-label={`Icono sin equivalencia: ${name}`}>?</span>
{/if}
