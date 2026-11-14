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
    if (path.startsWith("/v1/") && !path.startsWith("/v1/demo/")) {
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
  assert.ok(!contract.servers || contract.servers.length === 0);
});

test("stateless demo routes are explicitly unauthenticated and non-authoritative", () => {
  const mission = contract.paths["/v1/demo/missions/phishing-detective"].get;
  const assessment = contract.paths["/v1/demo/missions/phishing-detective/assessment"].post;
  assert.deepEqual(mission.security, []);
  assert.deepEqual(assessment.security, []);
  const submission = contract.components.schemas.DemoAssessmentSubmission;
  assert.equal(submission.additionalProperties, false);
  assert.ok(!("xp" in submission.properties));
  assert.equal(contract.components.schemas.DemoAssessmentResult.properties.xp_awarded.const, 0);
});


test("demo mission and assessment schemas describe the actual API payloads", () => {
  const mission = contract.components.schemas.DemoMission;
  assert.ok(mission.properties.email.properties.from_address);
  assert.ok(mission.properties.email.properties.reply_to);
  assert.ok(mission.properties.indicators.items.properties.id);
  assert.ok(mission.properties.response_options.items.properties.id);
  const result = contract.components.schemas.DemoAssessmentResult;
  for (const field of ["missed_indicators", "incorrect_selections", "response_correct", "response_explanation"]) {
    assert.ok(result.properties[field], field);
  }
  assert.equal(result.properties.persistence.const, "not_saved");
});
