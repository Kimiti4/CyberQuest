import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const contract = JSON.parse(
  await readFile(new URL("../../openapi/cyberquest-v1.json", import.meta.url), "utf8"),
);

test("OpenAPI contract declares health and learning entry points", () => {
  assert.ok(contract.paths["/health/live"]);
  assert.ok(contract.paths["/health/ready"]);
  assert.ok(contract.paths["/v1/learning-paths"]);
});

test("learner endpoints require bearer authentication", () => {
  for (const [path, item] of Object.entries(contract.paths)) {
    if (path.startsWith("/v1/")) {
      for (const operation of Object.values(item)) {
        assert.ok(operation.security?.some((scheme) => "BearerAuth" in scheme), path);
      }
    }
  }
});

test("mission event contract does not accept client reward authority", () => {
  const schema = contract.components.schemas.MissionEvent;
  assert.deepEqual(schema.required, ["event_id", "stage_id", "choice_id"]);
  assert.equal(schema.additionalProperties, false);
  assert.ok(!("xp" in schema.properties));
  assert.ok(!("mastery" in schema.properties));
});

test("health probes are explicitly public", () => {
  assert.deepEqual(contract.paths["/health/live"].get.security, []);
  assert.deepEqual(contract.paths["/health/ready"].get.security, []);
});

test("OpenAPI tags are documented and no production endpoint is implied", () => {
  assert.ok(contract.tags.every((tag) => tag.description?.trim()));
  assert.ok(contract.servers.every((server) => server.url.startsWith("http://localhost:")));
});
