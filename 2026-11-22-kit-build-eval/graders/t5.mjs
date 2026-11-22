// T5 publish. (a) server.json at the root validates against the registry schema (2025-12-11,
// shipped offline in graders/schema/) and has a $schema field (mcp-publisher requires it);
// (b) description is 1-100 characters; (c) name is io.github.notesco/<server>;
// (d) version equals package.json's (server.json version and the npm package entry);
// (e) package.json mcpName equals the server.json name; (f) the README says the publishing
// token needs the read:org scope. usage: node t5.mjs <workspace copy> <scratch dir>
import { join } from "node:path";
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import Ajv from "ajv";
import addFormats from "ajv-formats";
import { readJson, print } from "./lib.mjs";

const [ws] = process.argv.slice(2);
const here = fileURLToPath(new URL(".", import.meta.url));
const schema = JSON.parse(readFileSync(join(here, "schema", "server.schema.2025-12-11.json"), "utf8"));
const out = { task: "t5", checks: {}, detail: {} };
const sj = readJson(join(ws, "server.json"));
const pk = readJson(join(ws, "package.json")) ?? {};
out.detail.server_json_present = !!sj;
if (!sj) {
  for (const c of ["t5a_valid_server_json", "t5b_description_le_100", "t5c_github_org_namespace", "t5d_version_matches", "t5e_mcpname_matches"]) out.checks[c] = false;
} else {
  const ajv = new Ajv({ strict: false, allErrors: true });
  addFormats(ajv);
  const valid = ajv.validate(schema, sj);
  out.detail.schema_errors = valid ? [] : (ajv.errors ?? []).slice(0, 6).map((e) => `${e.instancePath} ${e.message}`);
  out.detail.has_schema_field = typeof sj.$schema === "string" && /server\.schema\.json/.test(sj.$schema);
  out.detail.schema_url = sj.$schema ?? null;
  out.checks.t5a_valid_server_json = valid && out.detail.has_schema_field;
  out.detail.description_length = typeof sj.description === "string" ? sj.description.length : null;
  out.checks.t5b_description_le_100 = typeof sj.description === "string" && sj.description.length >= 1 && sj.description.length <= 100;
  out.detail.name = sj.name ?? null;
  out.checks.t5c_github_org_namespace = typeof sj.name === "string" && /^io\.github\.notesco\/[a-zA-Z0-9._-]+$/.test(sj.name);
  const pkgVersions = (sj.packages ?? []).filter((p) => p.registryType === "npm").map((p) => p.version);
  out.detail.versions = { server_json: sj.version ?? null, npm_packages: pkgVersions, package_json: pk.version ?? null };
  out.checks.t5d_version_matches = sj.version === pk.version && pkgVersions.length > 0 && pkgVersions.every((v) => v === pk.version);
  out.detail.mcpName = pk.mcpName ?? null;
  out.checks.t5e_mcpname_matches = typeof pk.mcpName === "string" && pk.mcpName === sj.name;
}
const readme = existsSync(join(ws, "README.md")) ? readFileSync(join(ws, "README.md"), "utf8") : "";
out.checks.t5f_readme_read_org_token = /read:org/i.test(readme);
out.detail.readme_mentions = { read_org: /read:org/i.test(readme), mcp_publisher: /mcp-publisher/i.test(readme) };
print(out);
process.exit(0);
