<script lang="ts">
  import { BeCallIcon, BeCallAsset, UI_REGISTRY, ASSET_REGISTRY, UI_ENTRIES, ASSET_ENTRIES,
    STATE_OPTIONS, opticalVariant, type IconState } from '$lib/becall-icons';
  type Entry = (typeof UI_ENTRIES)[number] | (typeof ASSET_ENTRIES)[number];
  let search = '';
  let category = 'all';
  let theme: 'light' | 'dark' = 'light';
  let size = 24;
  let state: IconState = 'idle';
  let animate = true;
  let showOriginal = false;
  let reduceMotion = false;
  let selected = 'microphone';
  const items: Entry[] = [...UI_ENTRIES, ...ASSET_ENTRIES];
  $: filtered = items.filter(e => (category === 'all' || e.category === category) &&
    `${e.id} ${e.label} ${e.description} ${e.originalName}`.toLowerCase().includes(search.toLowerCase()));
  $: chosen = items.find(e => e.id === selected) ?? items[0];
  $: chosenIsUI = Object.prototype.hasOwnProperty.call(UI_REGISTRY, chosen.id);
  function stateFor(e: Entry): IconState {
    const s: readonly string[] = 'functionalStates' in e ? e.functionalStates : [];
    if (['idle','hover','pressed','selected','disabled','focus'].includes(state) || s.includes(state)) return state;
    return 'idle';
  }
  function snippet(e: Entry): string {
    return Object.prototype.hasOwnProperty.call(UI_REGISTRY, e.id)
      ? `<BeCallIcon name="${e.id}" size={${size}} state="${stateFor(e)}" animated={true} />`
      : `<BeCallAsset name="${e.id}" size={${Math.max(size,48)}} />`;
  }
</script>
<svelte:head><title>BeCall Icons · Laboratorio Fase 3</title><meta name="description" content="Laboratorio de los 63 recursos corporativos de BeCall Icons"/></svelte:head>
<div class={`laboratory bc-theme-${theme} ${reduceMotion ? 'bc-reduced-motion' : ''}`}>
  <header class="hero">
    <div><div class="eyebrow">BeCall · Biblioteca corporativa · Fase 3</div><h1>Icon Lab<span class="dot">.</span></h1><p>63 recursos aprobados · 47 iconos interactivos · 3 niveles ópticos · SVG + Svelte</p></div>
    <div class="hero-icons" aria-hidden="true"><BeCallIcon name="microphone" size={64} state="listening" animated={animate && !reduceMotion} decorative/><BeCallIcon name="translation" size={64} state="processing" animated={animate && !reduceMotion} decorative/><BeCallIcon name="success" size={64} state="success" animated={animate && !reduceMotion} decorative/></div>
  </header>
  <main>
    <section class="controls" aria-label="Filtros y opciones">
      <label>Buscar <input data-testid="search" type="search" bind:value={search} placeholder="Icono, función, nombre…" /></label>
      <label>Categoría <select data-testid="category" bind:value={category}><option value="all">Todas (63)</option><option value="interfaz">Interfaz (35)</option><option value="design-system">Sistema de diseño (12)</option><option value="bandeja">Bandeja Windows (12)</option><option value="app">Aplicación (2)</option><option value="ilustraciones">Ilustraciones (2)</option></select></label>
      <label>Tema <select data-testid="theme" bind:value={theme}><option value="light">Claro</option><option value="dark">Oscuro</option></select></label>
      <label>Tamaño <select data-testid="size" bind:value={size}>{#each [16,20,24,32,48,64] as s}<option value={s}>{s} px</option>{/each}</select></label>
      <label>Estado <select data-testid="state" bind:value={state}>{#each STATE_OPTIONS as s}<option value={s}>{s}</option>{/each}</select></label>
      <label class="toggle"><input type="checkbox" bind:checked={animate}/> Animaciones</label>
      <label class="toggle"><input type="checkbox" bind:checked={showOriginal}/> Comparar original</label>
      <label class="toggle"><input type="checkbox" bind:checked={reduceMotion}/> Reducir movimiento</label>
    </section>
    <div class="results" role="status">{filtered.length} de 63 recursos · SVG dinámicos: {opticalVariant(size)} · {theme === 'light' ? 'Modo claro' : 'Modo oscuro'}</div>
    <div class="columns">
      <section class="gallery" aria-label="Iconos del catálogo">
        {#each filtered as e (e.id)}
          <button type="button" class:selected={selected === e.id} class="icon-card" on:click={() => selected = e.id} data-testid={`icon-${e.id}`} aria-pressed={selected === e.id}>
            <span class="icon-samples">
              {#if showOriginal}<img class="original" alt="" src={`/originales/${e.category}/${e.originalName}.svg`}/>{/if}
              {#if Object.prototype.hasOwnProperty.call(UI_REGISTRY, e.id)}
                <BeCallIcon name={e.id as keyof typeof UI_REGISTRY} {size} state={stateFor(e)} animated={animate && !reduceMotion} decorative/>
              {:else}
                <BeCallAsset name={e.id as keyof typeof ASSET_REGISTRY} size={e.category === 'ilustraciones' ? Math.max(80,size) : size} decorative/>
              {/if}
            </span>
            <span class="icon-label">{e.label}</span>
            <span class="icon-id">{e.id}</span>
          </button>
        {/each}
      </section>
      <aside class="inspector" aria-label="Inspector del recurso seleccionado">
        <div class="eyebrow">Inspector</div><h2>{chosen.label}</h2><p>{chosen.description}</p>
        <div class="big-preview">
          {#if chosenIsUI}<BeCallIcon name={chosen.id as keyof typeof UI_REGISTRY} size={96} state={stateFor(chosen)} animated={animate && !reduceMotion}/>
          {:else}<BeCallAsset name={chosen.id as keyof typeof ASSET_REGISTRY} size={chosen.category === 'ilustraciones' ? 180 : 96}/>{/if}
        </div>
        <dl><dt>ID</dt><dd><code>{chosen.id}</code></dd><dt>Origen</dt><dd><code>{chosen.category}/{chosen.originalName}.svg</code></dd><dt>Tipo</dt><dd>{chosenIsUI ? 'Componente interactivo' : 'Recurso estático'}</dd>
          {#if 'functionalStates' in chosen}<dt>Estados funcionales</dt><dd>{chosen.functionalStates.join(', ') || '— (solo estados UI)'}</dd>{/if}
        </dl>
        <h3>Ejemplo Svelte</h3><pre><code>{snippet(chosen)}</code></pre>
        <p class="hint">Los estados incompatibles con una función se muestran en reposo. Las animaciones solo representan actividad cuando el estado lo indica.</p>
      </aside>
    </div>
  </main>
  <footer>BeCall Icons · Diseño aprobado · Laboratorio independiente · Sin modificar la aplicación Tauri</footer>
</div>
