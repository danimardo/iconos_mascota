/** Optional, injected runtime; no fake .riv files and no mandatory Rive dependency. */
import type { BeCallIconName, IconState } from './registry';
export type RiveStartOptions = {
  name: BeCallIconName;
  state: IconState;
  size: number;
  reducedMotion: boolean;
};
export interface RiveDriver {
  /** Called after client-side mount; must release all canvases/listeners. */
  mount(host: HTMLElement, options: RiveStartOptions): void | (() => void);
  /** Called on reactive state changes, if the runtime provides a state machine. */
  setState?(state: IconState): void;
}
