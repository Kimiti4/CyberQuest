import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const page = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const getRoute = await readFile(new URL("../app/api/demo/mission/route.ts", import.meta.url), "utf8");
const postRoute = await readFile(new URL("../app/api/demo/assessment/route.ts", import.meta.url), "utf8");

test("web demo consumes the API and submits only learner choices", () => {
  assert.match(page, /fetch\("\/api\/demo\/mission"/);
  assert.match(page, /selected_indicator_ids: selected, response_id: response/);
  assert.match(page, /setResult\(body as Assessment\)/);
  assert.match(page, /xp_awarded/);
});

test("web proxy keeps API origin server-side and does not cache demo data", () => {
  assert.match(getRoute, /process\.env\.CYBERQUEST_API_BASE_URL/);
  assert.match(getRoute, /cache: "no-store"/);
  assert.match(postRoute, /process\.env\.CYBERQUEST_API_BASE_URL/);
  assert.match(postRoute, /cache: "no-store"/);
});

test("web demo explicitly labels simulation and inert link", () => {
  assert.match(page, /SIMULATED EMAIL/);
  assert.match(page, /not clickable/);
  assert.match(page, /No data saved/);
});
