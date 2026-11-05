/* Galería de revisión: reproduce los .riv de la entrega con @rive-app/canvas 2.47.0. */
(() => {
  'use strict';
  const labels = {
    idle:'Reposo',hover:'Al pasar',pressed:'Pulsación',selected:'Seleccionado',focus:'Foco',disabled:'Desactivado',
    listening:'Escuchando',processing:'Procesando',speaking:'Hablando',success:'Correcto',error:'Error',
    warning:'Advertencia',muted:'Silenciado',connecting:'Conectando',disconnected:'Sin conexión',paused:'Pausado',completed:'Completado',
    wait:'Esperando',listen:'Escuchar',receive:'Recibir conversación',translate:'Traducir',speak:'Hablar',
    conversation:'Conversar',explain:'Explicar',wave:'Saludar',walk:'Caminar',turn:'Girarse',celebrate:'Celebrar',blink:'Parpadear'
  };
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const $ = (id) => document.getElementById(id);
  const state = {manifest:null,cards:[],variant:'standard',playing:!reduced.matches,observer:null,beca:null,becaAnimation:'idle',becaTour:!reduced.matches,becaTimer:0,audioTimer:0};
  const status = (message, type='ready') => { $('status').textContent=message; $('status-dot').className='statusdot '+type; };
  const title = (name) => labels[name] || name;
  const bytes = (base64) => {const raw=atob(base64);const out=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)out[i]=raw.charCodeAt(i);return out.buffer;};
  const fileBuffer = (path) => {
    const base64=window.BECALL_DEMO_DATA?.files?.[path];
    if(!base64)throw new Error('Falta el archivo Rive '+path+' en data.js');
    return bytes(base64);
  };
  const isLoop = (name) => ['listening','processing','speaking','connecting','wait','listen','receive','translate','speak','conversation','walk','idle'].includes(name);
  const iconStart = (animations) => ['listening','processing','speaking','connecting'].find(n=>animations.includes(n)) || 'hover';

  function option(select, value, text) {
    const node = document.createElement('option'); node.value=value; node.textContent=text; select.append(node);
  }

  class IconCard {
    constructor(item) {
      this.item=item;this.animation=iconStart(item.animations);this.instance=null;this.loaded=false;this.visible=false;this.timer=0;
      this.el=document.createElement('article');this.el.className='icon-card loading-card';
      const visual=document.createElement('div');visual.className='icon-visual';
      this.canvas=document.createElement('canvas');this.canvas.width=240;this.canvas.height=240;
      this.canvas.setAttribute('aria-hidden','true');visual.append(this.canvas);
      const meta=document.createElement('div');meta.className='icon-meta';
      const head=document.createElement('div');head.className='icon-title';
      const strong=document.createElement('strong');strong.textContent=item.label;
      const code=document.createElement('code');code.textContent=item.id;head.append(strong,code);
      const label=document.createElement('label');label.textContent='Animación';
      this.select=document.createElement('select');this.select.setAttribute('aria-label','Animación de '+item.label);
      for(const name of item.animations) option(this.select,name,title(name));
      this.select.value=this.animation;
      this.select.addEventListener('change',()=>{this.animation=this.select.value;this.play();});
      const foot=document.createElement('div');foot.className='icon-footer';
      this.note=document.createElement('span');this.note.textContent='Cargando Rive…';
      const replay=document.createElement('button');replay.type='button';replay.textContent='Repetir';
      replay.setAttribute('aria-label','Repetir animación de '+item.label);
      replay.addEventListener('click',()=>this.play());
      foot.append(this.note,replay);meta.append(head,label,this.select,foot);this.el.append(visual,meta);
    }
    load() {
      if(this.instance||!this.visible)return;
      const self=this;
      this.instance=new window.rive.Rive({
        buffer:fileBuffer(this.item.riv),canvas:this.canvas,artboard:state.variant,animations:this.animation,
        autoplay:state.playing,onLoad(){
          self.loaded=true;self.el.classList.remove('loading-card');self.note.textContent=state.variant+' · '+Math.round(self.item.bytes/1024)+' KB';
          self.instance.resizeDrawingSurfaceToCanvas();self.schedule();
          if(!state.playing)self.instance.pause();
        },onLoadError(error){self.note.textContent='No se pudo cargar';console.error(self.item.id,error);}
      });
    }
    play() {
      clearInterval(this.timer);this.timer=0;
      if(!this.instance||!this.loaded)return;
      this.instance.stop();
      this.instance.play(this.animation);
      if(!state.playing||!this.visible)this.instance.pause();
      this.schedule();
    }
    schedule() {
      clearInterval(this.timer);this.timer=0;
      if(!this.loaded||!state.playing||!this.visible||isLoop(this.animation)||this.animation==='disabled')return;
      this.timer=setInterval(()=>{if(this.instance){this.instance.stop();this.instance.play(this.animation);}},2700);
    }
    show(visible) {
      this.visible=visible;
      if(visible){this.load();if(this.loaded&&state.playing){this.instance.play(this.animation);this.schedule();}}
      else{clearInterval(this.timer);this.timer=0;this.instance?.pause();}
    }
    variant() {
      clearInterval(this.timer);this.timer=0;
      if(this.instance){this.instance.cleanup();this.instance=null;this.loaded=false;}
      this.note.textContent='Cargando Rive…';this.el.classList.add('loading-card');this.load();
    }
    destroy(){clearInterval(this.timer);this.instance?.cleanup();this.instance=null;}
  }

  const tourOrder=['wave','idle','wait','listen','receive','translate','speak','conversation','explain','walk','turn','celebrate','error','blink'];
  const tourDelay={idle:5500,wait:3900,listen:2800,receive:2800,translate:3100,speak:3100,conversation:3200,walk:3300,turn:2600,explain:2600,wave:2300,celebrate:2200,error:2000,blink:1700};
  let tourIndex=0;
  function setAudio(value){
    const normalized=Math.max(0,Math.min(1,Number(value)||0));$('beca-audio').value=String(normalized);$('beca-audio-value').textContent=normalized.toFixed(2).replace('.',',');
    const property=state.beca?.viewModelInstance?.number('audioLevel');if(property)property.value=normalized;
  }
  function autoMouth(active){
    clearInterval(state.audioTimer);state.audioTimer=0;
    if(!active){setAudio(0);return;}
    let tick=0;
    state.audioTimer=setInterval(()=>{tick++;setAudio(.25+Math.abs(Math.sin(tick*.7))*.62);},110);
  }
  function setBecaAnimation(name,fromTour=false){
    state.becaAnimation=name;$('beca-animation').value=name;$('beca-now').textContent='Beca · '+title(name);
    if(state.beca){const motion=state.beca.viewModelInstance?.number('motion');if(motion)motion.value=state.manifest.mascot.motionCodes[name];if(!state.playing)state.beca.pause();}
    autoMouth(state.playing && ['speak','conversation'].includes(name) && fromTour);
    if(!fromTour){state.becaTour=false;clearTimeout(state.becaTimer);$('beca-tour').textContent='Recorrer todos los gestos';$('beca-tour').setAttribute('aria-pressed','false');}
  }
  function nextTour(){
    if(!state.becaTour||!state.playing)return;
    const name=tourOrder[tourIndex++%tourOrder.length];setBecaAnimation(name,true);
    state.becaTimer=setTimeout(nextTour,tourDelay[name]||2600);
  }
  function startBeca(manifest){
    for(const name of tourOrder)option($('beca-animation'),name,title(name));
    $('beca-animation').value=state.becaAnimation;
    $('beca-animation').addEventListener('change',e=>setBecaAnimation(e.target.value));
    $('beca-replay').addEventListener('click',()=>{
      const name=state.becaAnimation;setBecaAnimation(name);
      const motion=state.beca?.viewModelInstance?.number('motion');
      if(motion&&name!=='idle'){motion.value=0;requestAnimationFrame(()=>{motion.value=state.manifest.mascot.motionCodes[name];});}
    });
    $('beca-pause').addEventListener('click',()=>{
      if(!state.beca)return;
      if(state.beca.isPlaying){state.beca.pause();$('beca-pause').textContent='Continuar';autoMouth(false);}
      else{state.beca.play('BecaMachine');$('beca-pause').textContent='Pausar';}
    });
    $('beca-audio').addEventListener('input',e=>{clearInterval(state.audioTimer);state.audioTimer=0;setAudio(e.target.value);});
    $('beca-tour').addEventListener('click',()=>{
      state.becaTour=!state.becaTour;clearTimeout(state.becaTimer);
      $('beca-tour').textContent=state.becaTour?'Detener recorrido':'Recorrer todos los gestos';
      $('beca-tour').setAttribute('aria-pressed',String(state.becaTour));
      if(state.becaTour){tourIndex=0;nextTour();}else autoMouth(false);
    });
    const canvas=$('beca-canvas');canvas.width=512;canvas.height=552;
    state.beca=new window.rive.Rive({buffer:fileBuffer(manifest.mascot.riv),canvas,stateMachine:'BecaMachine',autoBind:true,autoplay:state.playing,
      onLoad(){state.beca.resizeDrawingSurfaceToCanvas();$('beca-detail').textContent='· '+Math.round(manifest.mascot.bytes/1024)+' KB';setAudio(0);if(state.becaTour)nextTour();else setBecaAnimation('idle');},
      onLoadError(error){$('beca-now').textContent='No se pudo cargar Beca';console.error(error);}
    });
  }

  function filter(){
    const query=$('search').value.trim().toLocaleLowerCase('es');let shown=0;
    for(const card of state.cards){
      const matches=(card.item.id+' '+card.item.label).toLocaleLowerCase('es').includes(query);
      card.el.hidden=!matches;if(!matches)card.show(false);else shown++;
    }
    $('shown').textContent=shown+' de '+state.cards.length;$('empty').hidden=shown>0;
  }
  function setPlaying(value){
    state.playing=value;
    $('toggle-all').textContent=value?'Pausar todos':'Reproducir todos';
    for(const card of state.cards){if(!card.instance)continue;if(value&&card.visible)card.play();else{card.instance.pause();clearInterval(card.timer);}}
    if(state.beca){if(value){state.beca.play('BecaMachine');if(state.becaTour)nextTour();}else{state.beca.pause();clearTimeout(state.becaTimer);autoMouth(false);}}
  }

  async function main(){
    if(!window.rive?.Rive)throw new Error('No se ha cargado el runtime Rive local.');
    const embedded=window.BECALL_DEMO_DATA;
    if(!embedded?.manifest||!embedded?.wasm)throw new Error('Faltan los datos locales del visor. Regenera data.js.');
    const wasmUrl=URL.createObjectURL(new Blob([bytes(embedded.wasm)],{type:'application/wasm'}));
    window.rive.RuntimeLoader.setWasmUrl(wasmUrl);
    window.rive.RuntimeLoader.setWasmFallbackUrl(null);
    const manifest=embedded.manifest;state.manifest=manifest;
    $('count').textContent=manifest.icons.length+' iconos · 1 mascota';status('Runtime local listo · archivos Rive auténticos');
    const grid=$('grid');
    for(const item of manifest.icons){const card=new IconCard(item);state.cards.push(card);grid.append(card.el);}
    state.observer=new IntersectionObserver(entries=>{for(const entry of entries){const card=state.cards.find(c=>c.el===entry.target);if(card)card.show(entry.isIntersecting&&!card.el.hidden);}}, {rootMargin:'100px'});
    for(const card of state.cards)state.observer.observe(card.el);
    $('search').addEventListener('input',filter);
    $('variant').addEventListener('change',e=>{state.variant=e.target.value;for(const card of state.cards)card.variant();});
    $('toggle-all').addEventListener('click',()=>setPlaying(!state.playing));
    startBeca(manifest);filter();
    if(reduced.matches){status('Movimiento reducido del sistema · vista estática');$('toggle-all').disabled=true;$('beca-tour').disabled=true;}
    addEventListener('beforeunload',()=>{state.observer.disconnect();for(const card of state.cards)card.destroy();state.beca?.cleanup();clearTimeout(state.becaTimer);clearInterval(state.audioTimer);URL.revokeObjectURL(wasmUrl);});
  }
  main().catch(error=>{console.error(error);status(error.message,'error');});
})();
