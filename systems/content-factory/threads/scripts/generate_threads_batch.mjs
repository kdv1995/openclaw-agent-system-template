#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const FORMATS = ["myth", "case", "howto", "opinion", "checklist", "comparison"];
const MAX_CHARS = 500;

function arg(name, fallback) {
  const flag = `--${name}`;
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : fallback;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.resolve(ROOT, file), "utf8"));
}

function slug(s) {
  return s
    .toLowerCase()
    .replace(/[^a-zа-яіїєґ0-9]+/giu, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 48);
}

function pick(arr, n) {
  return arr[n % arr.length];
}

function compact(text) {
  return text
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function render(format, pillar, angle, cta, index) {
  const templates = {
    myth: [
      `Міф: ${angle}.`,
      `Реальність простіша: AI працює тільки там, де є зрозумілий процес, приклад входу і критерій хорошого результату.`,
      `Правило: спочатку опиши ручний workflow, потім автоматизуй один крок.`,
      cta,
    ],
    case: [
      `Типовий кейс: команда хоче "${angle}".`,
      `Але bottleneck не в інструменті. Він у тому, що ніхто не описав, що саме має вийти на виході.`,
      `AI варто давати роль, контекст, приклад і формат відповіді. Без цього він просто красиво імпровізує.`,
      cta,
    ],
    howto: [
      `Як впровадити ${pillar.name.toLowerCase()} без хаосу:`,
      `1. Випиши ручний процес.`,
      `2. Знайди один повторюваний крок.`,
      `3. Дай AI приклад хорошого результату.`,
      `4. Перевір 10 запусків перед масштабуванням.`,
      cta,
    ],
    opinion: [
      `Непопулярна думка: ${angle}.`,
      `Більшість проблем з AI не через модель. Вони через нечітку задачу, відсутність контексту і нульову перевірку результату.`,
      `AI підсилює мислення. Він не замінює його.`,
      cta,
    ],
    checklist: [
      `Перед тим як автоматизувати "${angle}", перевір:`,
      `- чи є повторюваний сценарій`,
      `- чи є приклади хорошого виходу`,
      `- хто перевіряє результат`,
      `- що робимо при помилці`,
      `Якщо цього нема, ти автоматизуєш хаос.`,
      cta,
    ],
    comparison: [
      `${pillar.name}: інструмент vs процес.`,
      `Інструмент дає швидкість. Процес дає стабільність.`,
      `Якщо купити AI tool без workflow, буде ще один чат у закладках. Якщо спочатку описати процес, навіть простий prompt вже дасть результат.`,
      cta,
    ],
  };

  return compact(templates[format].join("\n\n"));
}

function trimToLimit(post) {
  if (post.length <= MAX_CHARS) return post;
  const withoutCta = post.split("\n\n").slice(0, -1).join("\n\n");
  if (withoutCta.length <= MAX_CHARS) return withoutCta;
  return `${withoutCta.slice(0, MAX_CHARS - 1).trim()}…`;
}

function warningsFor(post) {
  const warnings = [];
  if (post.length > MAX_CHARS) warnings.push(`over ${MAX_CHARS} chars`);
  if (/AI will change everything/i.test(post)) warnings.push("generic AI hype");
  if ((post.match(/#/g) || []).length > 3) warnings.push("too many hashtags");
  return warnings;
}

function scorePost(post, warnings) {
  let score = 8;
  if (post.length < 180) score -= 1;
  if (post.length > 470) score -= 1;
  if (warnings.length) score -= warnings.length;
  if (/[0-9]\.|- /.test(post)) score += 1;
  return Math.max(1, Math.min(10, score));
}

function main() {
  const briefPath = arg("brief", "state/brief.sample.json");
  const count = Number(arg("count", "20"));
  const brief = readJson(briefPath);
  const posts = [];

  for (let i = 0; i < count; i += 1) {
    const pillar = pick(brief.pillars, i);
    const angle = pick(pillar.angles, Math.floor(i / brief.pillars.length) + i);
    const format = pick(FORMATS, i);
    const cta = pick(brief.ctaBank, i);
    const rawPost = render(format, pillar, angle, cta, i);
    const post = trimToLimit(rawPost);
    const warnings = warningsFor(post);
    const [hook, ...rest] = post.split("\n\n");
    const ctaLine = brief.ctaBank.find((x) => post.includes(x)) || "";
    const body = rest.filter((x) => x !== ctaLine).join("\n\n");

    posts.push({
      id: `${String(i + 1).padStart(2, "0")}-${slug(pillar.name)}-${crypto.randomBytes(3).toString("hex")}`,
      pillar: pillar.name,
      format,
      angle,
      hook,
      body,
      cta: ctaLine,
      post,
      charCount: post.length,
      score: scorePost(post, warnings),
      warnings,
    });
  }

  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const out = {
    generatedAt: new Date().toISOString(),
    brief,
    posts,
  };
  const jsonPath = path.join(ROOT, "runs", `${stamp}-threads-batch.json`);
  const mdPath = path.join(ROOT, "runs", `${stamp}-threads-batch.md`);
  fs.mkdirSync(path.dirname(jsonPath), { recursive: true });
  fs.writeFileSync(jsonPath, JSON.stringify(out, null, 2));
  fs.writeFileSync(
    mdPath,
    posts.map((p) => `## ${p.id} | ${p.pillar} | ${p.format} | ${p.charCount} chars\n\n${p.post}\n`).join("\n---\n\n")
  );

  console.log(`Wrote ${jsonPath}`);
  console.log(`Wrote ${mdPath}`);
}

main();
