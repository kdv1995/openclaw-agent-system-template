#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const CONFIG_PATH = path.join(ROOT, "state", "schedule.config.json");
const QUEUE_PATH = path.join(ROOT, "state", "queue.json");
const SCHEDULED_PATH = path.join(ROOT, "state", "scheduled_threads.json");

function arg(name, fallback = null) {
  const flag = `--${name}`;
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : fallback;
}

function hasFlag(name) {
  return process.argv.includes(`--${name}`);
}

function readJson(file, fallback) {
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : fallback;
}

function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

function todayInKyiv() {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Kyiv",
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).formatToParts(new Date());
  const map = Object.fromEntries(parts.map((p) => [p.type, p.value]));
  return `${map.year}-${map.month}-${map.day}`;
}

function slotToIso(date, slot) {
  // Postiz accepts explicit offsets. Kyiv is UTC+03 on May 2026.
  return `${date}T${slot}:00+03:00`;
}

function createdCountForDay(records, date, integrationId) {
  return records.filter(
    (x) =>
      x.status === "created" &&
      x.integrationId === integrationId &&
      x.scheduledFor?.startsWith(date)
  ).length;
}

const dryRun = !hasFlag("publish");
const targetDate = arg("date", todayInKyiv());
const config = readJson(CONFIG_PATH);
const queue = readJson(QUEUE_PATH, { items: [] });
const scheduled = readJson(SCHEDULED_PATH, { records: [] });
const integration = config.defaultIntegration;
const alreadyToday = createdCountForDay(scheduled.records, targetDate, integration.integrationId);
const remaining = Math.max(0, config.maxPostsPerDay - alreadyToday);
const freeSlots = config.slots.slice(alreadyToday, alreadyToday + remaining);

if (!freeSlots.length) {
  console.log(`No free slots for ${targetDate}. Already scheduled: ${alreadyToday}/${config.maxPostsPerDay}`);
  process.exit(0);
}

const candidates = queue.items
  .filter((x) => x.status === "queued")
  .sort((a, b) => b.score - a.score || a.charCount - b.charCount);

const selected = [];
const seenContent = new Set();
const seenFormatByPillar = new Set();
for (const item of candidates) {
  const contentKey = item.content.toLowerCase().replace(/\s+/g, " ").trim();
  const formatKey = `${item.pillar}:${item.format}`;
  if (seenContent.has(contentKey)) continue;
  if (seenFormatByPillar.has(formatKey) && selected.length < candidates.length - 1) continue;
  selected.push(item);
  seenContent.add(contentKey);
  seenFormatByPillar.add(formatKey);
  if (selected.length === freeSlots.length) break;
}

for (const item of candidates) {
  if (selected.length === freeSlots.length) break;
  if (selected.includes(item)) continue;
  const contentKey = item.content.toLowerCase().replace(/\s+/g, " ").trim();
  if (seenContent.has(contentKey)) continue;
  selected.push(item);
  seenContent.add(contentKey);
}

if (!selected.length) {
  console.log("No queued posts to schedule.");
  process.exit(0);
}

const plan = selected.map((item, i) => ({
  item,
  scheduledFor: slotToIso(targetDate, freeSlots[i])
}));

console.log(`${dryRun ? "DRY RUN" : "PUBLISH"} ${plan.length} post(s) for ${targetDate}:`);
for (const row of plan) {
  console.log(`- ${row.scheduledFor} | ${row.item.id} | score=${row.item.score}`);
  console.log(`  ${row.item.content.replace(/\n/g, " ").slice(0, 120)}`);
}

if (dryRun) {
  console.log("Add --publish to create posts in Postiz.");
  process.exit(0);
}

for (const row of plan) {
  const out = execFileSync(
    "postiz",
    [
      "posts:create",
      "--content",
      row.item.content,
      "--date",
      row.scheduledFor,
      "--integrations",
      integration.integrationId,
      "--shortLink=false"
    ],
    { encoding: "utf8", maxBuffer: 10 * 1024 * 1024 }
  );

  row.item.status = "scheduled";
  row.item.scheduledFor = row.scheduledFor;
  row.item.integrationId = integration.integrationId;
  row.item.account = integration.account;

  scheduled.records.push({
    id: row.item.id,
    status: "created",
    account: integration.account,
    integrationId: integration.integrationId,
    scheduledFor: row.scheduledFor,
    content: row.item.content,
    postizResponse: out.trim(),
    createdAt: new Date().toISOString()
  });
}

writeJson(QUEUE_PATH, queue);
writeJson(SCHEDULED_PATH, scheduled);
console.log(`Created ${plan.length} Postiz post(s). State: ${SCHEDULED_PATH}`);
