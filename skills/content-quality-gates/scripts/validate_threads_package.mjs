#!/usr/bin/env node
import fs from "node:fs";

const file = process.argv[2];
if (!file) {
  console.error("Usage: validate_threads_package.mjs <package.json>");
  process.exit(2);
}

const pkg = JSON.parse(fs.readFileSync(file, "utf8"));
const errors = [];
const warnings = [];

if (pkg.platform !== "threads") errors.push("platform must be 'threads'");
if (pkg.integrationId !== "cmn2z0wij06plpb0yrviw718g") {
  errors.push("integrationId must be Threads example_threads_handle (cmn2z0wij06plpb0yrviw718g)");
}
if (!Array.isArray(pkg.posts) || pkg.posts.length === 0) {
  errors.push("posts must be a non-empty array");
}
if (Array.isArray(pkg.posts) && pkg.posts.length < 3 && pkg.format !== "single") {
  errors.push("news Threads packages must be a chain of at least 3 posts; use format='single' only when explicitly requested");
}
if (Array.isArray(pkg.posts) && pkg.posts.length > 7) {
  warnings.push("thread has more than 7 posts; only use if the operator asked for depth");
}

for (const [idx, post] of (pkg.posts || []).entries()) {
  if (typeof post !== "string" || !post.trim()) {
    errors.push(`posts[${idx}] must be non-empty text`);
    continue;
  }
  const chars = [...post].length;
  if (chars > 500) errors.push(`posts[${idx}] is ${chars} chars; Threads limit is 500`);
  if (chars < 80) warnings.push(`posts[${idx}] is short (${chars} chars); check it has enough context`);
  if (/AI\s+(це|is)\s+(майбутн|future)/i.test(post)) {
    warnings.push(`posts[${idx}] may be generic AI hype`);
  }
}

if (errors.length) {
  console.error("FAIL");
  for (const e of errors) console.error(`- ${e}`);
  if (warnings.length) {
    console.error("Warnings:");
    for (const w of warnings) console.error(`- ${w}`);
  }
  process.exit(1);
}

console.log("PASS");
for (const w of warnings) console.log(`warning: ${w}`);
