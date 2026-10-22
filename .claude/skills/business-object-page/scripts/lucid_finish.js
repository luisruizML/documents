// Finishing pass for the generated Lucid documents (the simplified graph and the global model), run once after the import with lucid_run_script (`source` = this file).
// The Standard Import JSON cannot set either of these, so the pass does it:
//   1. every line goes behind every shape: lines cannot be re-ordered, so every block (shapes, names, legend) is brought to the front,
//      in the order the importer drew them (shapes, then names, then legend), which leaves all lines at the back;
//   2. line jumps are on for the page and for every line, so a line that crosses another hops over it.
// It returns a report: the counts, any line whose end is not glued to a shape, and the validator's findings.
const read = await skills.basecanvasediting.read({});
const ids = new Set();
(function walk(v) {
  if (Array.isArray(v)) v.forEach(walk);
  else if (v && typeof v === 'object') {
    for (const [k, x] of Object.entries(v)) {
      if (typeof x === 'string' && (k === 'id' || k.endsWith('Id'))) ids.add(x);
      else if (Array.isArray(x) && k.endsWith('Ids')) x.forEach((i) => typeof i === 'string' && ids.add(i));
      walk(x);
    }
  }
})(read.pages[0].data);
const items = skills.basecanvasediting.inspect([...ids]);
const blocks = items.filter((i) => i.kind === 'block' && !i.id.startsWith('band_'));   // the bands of the global diagram stay at the back
const lines = items.filter((i) => i.kind === 'line');
const rank = (id) => (/^n\d+$/.test(id) ? 0 : /^l\d+$/.test(id) ? 1 : 2);
const number = (id) => parseInt(id.replace(/\D+/g, '') || '0', 10);
blocks.sort((a, b) => rank(a.id) - rank(b.id) || number(a.id) - number(b.id) || a.id.localeCompare(b.id));
for (const b of blocks) skills.basecanvasediting.setZOrder(b.id, 'top');
skills.secondarycanvasediting.setLineJumps(true);
for (const l of lines) skills.lines.setLineJumps(l.id, true);
const loose = lines
  .filter((l) => l.id.startsWith('e') || l.id.startsWith('u'))
  .filter((l) => typeof l.from !== 'string' || typeof l.to !== 'string')
  .map((l) => l.id);
const check = await skills.basecanvasediting.validateCanvas({ validators: ['disconnectedEndpoint'] });
return {
  blocks: blocks.length,
  lines: lines.length,
  structural: lines.filter((l) => l.id.startsWith('e')).length,
  uses: lines.filter((l) => l.id.startsWith('u')).length,
  pageJumps: skills.secondarycanvasediting.getLineJumps(),
  loose,
  disconnected: check.issues,
};
