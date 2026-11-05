import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import assert from 'node:assert/strict';
const root = process.cwd();
const m = JSON.parse(readFileSync(join(root,'docs/manifest-fase3.json'),'utf8'));
assert.equal(m.inventory.length,63,'Must map 63 source entries');
const counts = Object.create(null);
let total = 0;
for (const e of m.inventory) {
  counts[e.category]=(counts[e.category]||0)+1;
  for(const p of e.new_files.filter(x=>x.endsWith('.svg'))) {
    const f=join(root,'src/lib/becall-icons',p);
    assert.ok(existsSync(f),`Missing ${p}`);
    const markup=readFileSync(f,'utf8');
    assert.match(markup,/<svg\b/);
    assert.match(markup,/<\/svg>/);
    assert.doesNotMatch(markup,/<(?:script|foreignObject)\b|\son[a-z]+\s*=|javascript:/i,`Unsafe SVG: ${p}`);
    total++;
  }
  assert.ok(existsSync(join(root,'static/originales',e.original_path)));
}
assert.deepEqual({...counts},{app:2,bandeja:12,'design-system':12,ilustraciones:2,interfaz:35});
assert.equal(total,157,'157 SVG total / 141 UI + 16 static');
for(const e of m.inventory.filter(x=>['interfaz','design-system'].includes(x.category))){
  assert.equal(e.new_files.filter(x=>x.endsWith('.svg')).length,3);
}
for(const f of ['BeCallIcon.svelte','BeCallAsset.svelte','LucideCompat.svelte','RiveSlot.svelte','registry.ts','svg-source.ts','tokens.css','motion.css'])
 assert.ok(existsSync(join(root,'src/lib/becall-icons',f)),`Missing component ${f}`);
console.log(`OK: ${m.inventory.length} mapped originals | ${total} SVG | ${JSON.stringify(counts)} | interactive components & reference copies`);
