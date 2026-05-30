#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const MAX_CHARS = 500;
const batchPath = process.argv[2];

if (!batchPath) {
  console.error("Usage: node scripts/validate_batch.mjs runs/<batch>.json");
  process.exit(2);
}

const batch = JSON.parse(fs.readFileSync(path.resolve(batchPath), "utf8"));
const failures = [];

if (!Array.isArray(batch.posts)) {
  failures.push("posts must be an array");
} else {
  for (const post of batch.posts) {
    if (!post.id) failures.push("post without id");
    if (!post.post) failures.push(`${post.id}: missing post`);
    if ((post.post || "").length > MAX_CHARS) failures.push(`${post.id}: over ${MAX_CHARS} chars`);
    if (!post.hook) failures.push(`${post.id}: missing hook`);
    if (post.warnings?.length) failures.push(`${post.id}: warnings: ${post.warnings.join(", ")}`);
  }
}

if (failures.length) {
  console.error(`INVALID: ${failures.length} issue(s)`);
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(`OK: ${batch.posts.length} posts, all <= ${MAX_CHARS} chars`);
