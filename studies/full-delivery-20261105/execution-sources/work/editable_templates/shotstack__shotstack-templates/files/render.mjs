/**
 * Renders any template in this repo once per row of a CSV.
 *
 * The template's merge fields are read from template.json at runtime, so this
 * one script works for every template folder — no per-template edits needed.
 *
 * Setup (2 minutes):
 *   1. Pick a template folder, e.g. templates/hello-world/
 *   2. Create data.csv inside it. The column names are the template's merge
 *      fields, lowercased — the folder's README lists the exact header row.
 *      Columns you leave out keep the template's default value.
 *   3. npm install csv-parse           (Node 18+)
 *   4. SHOTSTACK_API_KEY=your_production_key node render.mjs templates/hello-world
 *
 * For free watermarked test renders, use a sandbox key and replace /v1/ with
 * /stage/ below (get a key: https://dashboard.shotstack.io/register).
 * For big batches, add a callback URL per request instead of polling:
 * https://shotstack.io/docs/guide/architecting-an-application/webhooks/
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse } from 'csv-parse/sync';

if (!process.env.SHOTSTACK_API_KEY) {
  console.error('Set SHOTSTACK_API_KEY first (step 4). Get a key: https://dashboard.shotstack.io/register');
  process.exit(1);
}

const API = 'https://api.shotstack.io/edit/v1/render';
const headers = { 'x-api-key': process.env.SHOTSTACK_API_KEY, 'Content-Type': 'application/json' };

const dir = process.argv[2] ?? '.';
const read = (file) => {
  try {
    return readFileSync(join(dir, file), 'utf8');
  } catch {
    console.error(`Missing ${join(dir, file)} - see the setup steps at the top of this script.`);
    process.exit(1);
  }
};
const template = JSON.parse(read('template.json'));
const rows = parse(read('data.csv'), { columns: true, bom: true, skip_empty_lines: true, trim: true });

const fields = template.merge ?? [];
if (!fields.length) console.error('Note: this template has no merge fields; every row renders the same output.');
const known = new Set(fields.map((f) => f.find.toLowerCase()));
for (const column of Object.keys(rows[0] ?? {})) {
  if (!known.has(column)) console.error(`Note: CSV column "${column}" matches no merge field; ignored.`);
}

// 1. Queue one render per row: each CSV column overrides the merge field of the
//    same (lowercased) name; missing columns keep the template's default value.
const queued = [];
for (const row of rows) {
  const edit = {
    ...template,
    merge: fields.map((f) => ({ find: f.find, replace: row[f.find.toLowerCase()] ?? f.replace }))
  };
  const body = await fetch(API, { method: 'POST', headers, body: JSON.stringify(edit) })
    .then((r) => r.json())
    .catch(() => null);
  if (!body?.response?.id) {
    console.error('Row failed:', JSON.stringify(row), body?.response?.error ?? body?.message ?? 'network error');
    continue;
  }
  queued.push({ row, id: body.response.id });
  console.log('Queued', body.response.id);
}

// 2. Poll until every render is finished, then print the video URLs
for (const job of queued) {
  let render = { status: 'queued' };
  for (let i = 0; i < 100 && !['done', 'failed'].includes(render.status); i++) {
    await new Promise((r) => setTimeout(r, 3000));
    const body = await fetch(`${API}/${job.id}`, { headers }).then((r) => r.json()).catch(() => null);
    render = body?.response ?? render; // a dropped status check retries on the next pass
  }
  console.log(render.status === 'done' ? render.url : `FAILED: ${render.error ?? render.status}`);
}
