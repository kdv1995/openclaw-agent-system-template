#!/usr/bin/env node

import fs from "node:fs";

const [rawListPath, postId, outPath] = process.argv.slice(2);

if (!rawListPath || !postId || !outPath) {
  console.error("Usage: verify-postiz-post.mjs <postiz-list-output.txt> <post-id> <out.json>");
  process.exit(2);
}

const raw = fs.readFileSync(rawListPath, "utf8");
const jsonStart = raw.indexOf("{");

if (jsonStart < 0) {
  console.error(`No JSON object found in ${rawListPath}`);
  process.exit(1);
}

let data;
try {
  data = JSON.parse(raw.slice(jsonStart));
} catch (error) {
  console.error(`Failed to parse Postiz list JSON from ${rawListPath}: ${error.message}`);
  process.exit(1);
}

const post = (data.posts || []).find((item) => item.id === postId);

if (!post) {
  console.error(`Postiz post not found: ${postId}`);
  process.exit(1);
}

const verified = {
  checkedAt: new Date().toISOString(),
  id: post.id,
  content: post.content,
  publishDate: post.publishDate,
  releaseURL: post.releaseURL || null,
  releaseId: post.releaseId || null,
  state: post.state,
  intervalInDays: post.intervalInDays ?? null,
  group: post.group,
  creationMethod: post.creationMethod,
  tags: post.tags || [],
  integration: post.integration
    ? {
        id: post.integration.id,
        providerIdentifier: post.integration.providerIdentifier,
        name: post.integration.name,
        picture: post.integration.picture,
      }
    : null,
};

fs.writeFileSync(outPath, `${JSON.stringify(verified, null, 2)}\n`);
console.log(JSON.stringify(verified, null, 2));
