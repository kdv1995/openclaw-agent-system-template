#!/usr/bin/env node
import fs from "node:fs";
import { execFileSync } from "node:child_process";

const file = process.argv[2];
if (!file) {
  console.error("Usage: validate_facebook_package.mjs <package.json>");
  process.exit(2);
}

const pkg = JSON.parse(fs.readFileSync(file, "utf8"));
const errors = [];
const warnings = [];

if (pkg.platform !== "facebook") errors.push("platform must be 'facebook'");
if (pkg.integrationId !== "cmojta1o20165o70ygbci5fit") {
  errors.push("integrationId must be Facebook example brand (cmojta1o20165o70ygbci5fit)");
}
if (typeof pkg.content !== "string" || !pkg.content.trim()) errors.push("content is required");
if (pkg.content && pkg.content.length < 700) warnings.push("Facebook post is short; business case may need more context");
if (pkg.content && pkg.content.length > 6000) warnings.push("Facebook post is long; consider tightening before publishing");

if (!pkg.imagePath || !fs.existsSync(pkg.imagePath)) {
  errors.push("imagePath must point to an existing image");
} else {
  try {
    const out = execFileSync("sips", ["-g", "pixelWidth", "-g", "pixelHeight", pkg.imagePath], { encoding: "utf8" });
    const width = Number(out.match(/pixelWidth:\s*(\d+)/)?.[1]);
    const height = Number(out.match(/pixelHeight:\s*(\d+)/)?.[1]);
    if (!width || !height) errors.push("could not read image dimensions");
    const ratio = width / height;
    const squareOk = width >= 1024 && height >= 1024 && Math.abs(ratio - 1) < 0.03;
    const portraitOk = width >= 1080 && height >= 1350 && Math.abs(ratio - 0.8) < 0.03;
    if (!squareOk && !portraitOk) {
      errors.push(`image dimensions ${width}x${height} are not approved; use 1:1 >=1024x1024 or 4:5 >=1080x1350`);
    }
  } catch {
    errors.push("failed to inspect image with sips");
  }
}

const firstTwoLines = (pkg.content || "").split(/\n+/).filter(Boolean).slice(0, 2).join(" ");
if (firstTwoLines && !/(рахунк|лід|клієнт|продаж|підтрим|документ|гро|час|хаос|власник|бізнес|CRM|операц)/i.test(firstTwoLines)) {
  warnings.push("first two lines may not name a concrete business pain");
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
