#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const QUEUE_PATH = path.join(ROOT, "state", "queue.json");

function readJson(file, fallback) {
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : fallback;
}

function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

function latestBatchPath() {
  const runs = path.join(ROOT, "runs");
  const files = fs.readdirSync(runs).filter((x) => x.endsWith("-threads-batch.json")).sort();
  if (!files.length) throw new Error("No batch files found in runs/");
  return path.join(runs, files.at(-1));
}

const batchPath = process.argv[2] ? path.resolve(process.argv[2]) : latestBatchPath();
const batch = readJson(batchPath);
const queue = readJson(QUEUE_PATH, { items: [] });
const existing = new Set(queue.items.map((x) => `${x.sourceBatch}:${x.sourcePostId}`));
let added = 0;

for (const post of batch.posts) {
  const key = `${path.basename(batchPath)}:${post.id}`;
  if (existing.has(key)) continue;
  queue.items.push({
    id: key,
    status: "queued",
    sourceBatch: path.basename(batchPath),
    sourcePostId: post.id,
    pillar: post.pillar,
    format: post.format,
    score: post.score,
    charCount: post.charCount,
    content: post.post,
    createdAt: new Date().toISOString()
  });
  added += 1;
}

writeJson(QUEUE_PATH, queue);
console.log(`Queued ${added} new post(s). Total queue items: ${queue.items.length}`);
console.log(`Queue: ${QUEUE_PATH}`);
