#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../..");
const ENV_PATH = process.env.OPENCLAW_ENV_FILE || path.join(process.env.HOME || ".", ".openclaw", ".env");
const DEFAULT_OUT_DIR = process.env.META_ANALYTICS_OUT_DIR || path.join(ROOT, "analytics", "reports");
const FETCH_TIMEOUT_MS = Number(process.env.META_ANALYTICS_FETCH_TIMEOUT_MS || 15000);

function loadEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return;
  for (const line of fs.readFileSync(filePath, "utf8").split(/\r?\n/)) {
    if (!line || line.trim().startsWith("#")) continue;
    const match = line.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!match) continue;
    process.env[match[1]] = match[2].trim().replace(/^['"]|['"]$/g, "");
  }
}

function argValue(name, fallback) {
  const idx = process.argv.indexOf(name);
  if (idx === -1 || idx + 1 >= process.argv.length) return fallback;
  return process.argv[idx + 1];
}

function hmacProof(token, secret) {
  if (!token || !secret) return null;
  return crypto.createHmac("sha256", secret).update(token).digest("hex");
}

async function graphGet(baseUrl, pathPart, token, secret, params = {}) {
  const url = new URL(`${baseUrl}/${pathPart}`);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, String(value));
  }
  url.searchParams.set("access_token", token);
  const proof = hmacProof(token, secret);
  if (proof) url.searchParams.set("appsecret_proof", proof);

  const res = await fetch(url, { signal: AbortSignal.timeout(FETCH_TIMEOUT_MS) });
  const body = await res.json().catch(() => ({}));
  if (!res.ok || body.error) {
    const err = body.error || body;
    const error = new Error(err.message || `${res.status} ${res.statusText}`);
    error.status = res.status;
    error.code = err.code;
    error.type = err.type;
    error.subcode = err.error_subcode;
    throw error;
  }
  return body;
}

async function collectThreads({ limit }) {
  const accessToken = process.env.THREADS_ACCESS_TOKEN;
  const userId = process.env.THREADS_USER_ID || "me";
  const appSecret = process.env.THREADS_APP_SECRET || process.env.META_APP_SECRET || "";
  if (!accessToken) return { ok: false, error: "THREADS_ACCESS_TOKEN missing" };

  const base = "https://graph.threads.net/v1.0";
  const profile = await graphGet(base, userId, accessToken, appSecret, {
    fields: "id,username,name,threads_biography",
  });
  const accountInsights = await graphGet(base, `${userId}/threads_insights`, accessToken, appSecret, {
    metric: "views,likes,replies,reposts,quotes,followers_count",
    period: "day",
  });

  const posts = [];
  let page = await graphGet(base, `${userId}/threads`, accessToken, appSecret, {
    fields: "id,shortcode,permalink,timestamp,media_type,text",
    limit: Math.min(limit, 100),
  });

  while (page?.data?.length && posts.length < limit) {
    for (const post of page.data) {
      if (posts.length >= limit) break;
      let metrics = {};
      try {
        const insights = await graphGet(base, `${post.id}/insights`, accessToken, appSecret, {
          metric: "views,likes,replies,reposts,quotes,shares",
        });
        metrics = Object.fromEntries(
          (insights.data || []).map((item) => [item.name, item.values?.[0]?.value ?? item.total_value?.value ?? null]),
        );
      } catch (error) {
        metrics = { error: error.message, code: error.code || null };
      }
      posts.push({
        ...post,
        text_preview: post.text ? post.text.replace(/\s+/g, " ").slice(0, 180) : "",
        metrics,
      });
    }

    const next = page.paging?.next;
    if (!next || posts.length >= limit) break;
    const res = await fetch(next, { signal: AbortSignal.timeout(FETCH_TIMEOUT_MS) });
    page = await res.json().catch(() => ({}));
  }

  return {
    ok: true,
    profile,
    accountInsights: accountInsights.data || [],
    posts,
  };
}

async function collectFacebook({ limit }) {
  const pageId = process.env.FB_PAGE_ID;
  const pageAccessToken = process.env.FB_PAGE_ACCESS_TOKEN;
  const appSecret = process.env.META_APP_SECRET || "";
  if (!pageId || !pageAccessToken) return { ok: false, error: "FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN missing" };

  const base = "https://graph.facebook.com/v24.0";
  try {
    const page = await graphGet(base, pageId, pageAccessToken, appSecret, {
      fields: `id,name,fan_count,followers_count,posts.limit(${Math.min(limit, 100)}){id,message,created_time,permalink_url,shares,comments.summary(true).limit(0),reactions.summary(true).limit(0)}`,
    });
    return {
      ok: true,
      page: {
        id: page.id,
        name: page.name,
        fan_count: page.fan_count ?? null,
        followers_count: page.followers_count ?? null,
      },
      posts: (page.posts?.data || []).map((post) => ({
        id: post.id,
        created_time: post.created_time,
        permalink_url: post.permalink_url,
        text_preview: post.message ? post.message.replace(/\s+/g, " ").slice(0, 180) : "",
        metrics: {
          reactions: post.reactions?.summary?.total_count ?? null,
          comments: post.comments?.summary?.total_count ?? null,
          shares: post.shares?.count ?? 0,
        },
      })),
    };
  } catch (error) {
    return {
      ok: false,
      status: error.status || null,
      code: error.code || null,
      subcode: error.subcode || null,
      type: error.type || null,
      error: error.message,
    };
  }
}

async function collectInstagram({ limit }) {
  const pageId = process.env.FB_PAGE_ID;
  const pageAccessToken = process.env.FB_PAGE_ACCESS_TOKEN;
  const appSecret = process.env.META_APP_SECRET || "";
  if (!pageId || !pageAccessToken) return { ok: false, error: "FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN missing" };

  const base = "https://graph.facebook.com/v24.0";
  try {
    let igUserId = process.env.INSTAGRAM_BUSINESS_ACCOUNT_ID || process.env.IG_USER_ID || process.env.INSTAGRAM_USER_ID;
    if (!igUserId) {
      const page = await graphGet(base, pageId, pageAccessToken, appSecret, {
        fields: "instagram_business_account{id,username,name,followers_count,media_count}",
      });
      igUserId = page.instagram_business_account?.id;
    }
    if (!igUserId) return { ok: false, error: "No instagram_business_account connected to FB_PAGE_ID" };

    const profile = await graphGet(base, igUserId, pageAccessToken, appSecret, {
      fields: "id,username,name,followers_count,media_count",
    });
    const accountInsights = await graphGet(base, `${igUserId}/insights`, pageAccessToken, appSecret, {
      metric: "reach,profile_views,accounts_engaged,total_interactions,likes,comments,shares,saves",
      period: "day",
      metric_type: "total_value",
    });
    const media = await graphGet(base, `${igUserId}/media`, pageAccessToken, appSecret, {
      fields: "id,caption,media_type,permalink,timestamp,like_count,comments_count",
      limit: Math.min(limit, 100),
    });

    const posts = [];
    for (const item of media.data || []) {
      let metrics = { likes: item.like_count ?? null, comments: item.comments_count ?? null };
      try {
        const insights = await graphGet(base, `${item.id}/insights`, pageAccessToken, appSecret, {
          metric: "reach,likes,comments,shares,saved,total_interactions",
        });
        metrics = {
          ...metrics,
          ...Object.fromEntries((insights.data || []).map((metric) => [metric.name, metric.values?.[0]?.value ?? null])),
        };
      } catch (error) {
        metrics.error = error.message;
        metrics.code = error.code || null;
      }
      posts.push({
        id: item.id,
        permalink: item.permalink,
        timestamp: item.timestamp,
        media_type: item.media_type,
        text_preview: item.caption ? item.caption.replace(/\s+/g, " ").slice(0, 180) : "",
        metrics,
      });
    }

    return { ok: true, profile, accountInsights: accountInsights.data || [], posts };
  } catch (error) {
    return {
      ok: false,
      status: error.status || null,
      code: error.code || null,
      subcode: error.subcode || null,
      type: error.type || null,
      error: error.message,
    };
  }
}

function totalThreads(posts) {
  const keys = ["views", "likes", "replies", "reposts", "quotes", "shares"];
  const totals = Object.fromEntries(keys.map((key) => [key, 0]));
  for (const post of posts) {
    for (const key of keys) {
      const value = Number(post.metrics?.[key] || 0);
      if (Number.isFinite(value)) totals[key] += value;
    }
  }
  return totals;
}

function totalInstagram(posts) {
  const keys = ["reach", "likes", "comments", "shares", "saved", "total_interactions"];
  const totals = Object.fromEntries(keys.map((key) => [key, 0]));
  for (const post of posts) {
    for (const key of keys) {
      const value = Number(post.metrics?.[key] || 0);
      if (Number.isFinite(value)) totals[key] += value;
    }
  }
  return totals;
}

function writeMarkdown(report, filePath) {
  const lines = [];
  lines.push("# Meta/Threads Analytics");
  lines.push(`Generated: ${report.generatedAt}`);
  lines.push("");

  if (report.threads?.ok) {
    const totals = totalThreads(report.threads.posts);
    lines.push(`## Threads @${report.threads.profile.username}`);
    lines.push(`Posts fetched: ${report.threads.posts.length}`);
    lines.push(`Totals: views ${totals.views}, likes ${totals.likes}, replies ${totals.replies}, reposts ${totals.reposts}, quotes ${totals.quotes}, shares ${totals.shares}`);
    lines.push("");
    lines.push("### Top Threads Posts");
    for (const post of [...report.threads.posts].sort((a, b) => (b.metrics?.views || 0) - (a.metrics?.views || 0)).slice(0, 12)) {
      lines.push(`- ${post.metrics?.views ?? "?"} views / ${post.metrics?.likes ?? "?"} likes / ${post.metrics?.replies ?? "?"} replies / ${post.metrics?.shares ?? "?"} shares - ${post.permalink} - ${post.text_preview}`);
    }
  } else {
    lines.push("## Threads");
    lines.push(`Blocked: ${report.threads?.error || "unknown error"}`);
  }

  lines.push("");
  if (report.facebook?.ok) {
    lines.push(`## Facebook ${report.facebook.page.name}`);
    lines.push(`Followers: ${report.facebook.page.followers_count ?? "unknown"}`);
    lines.push(`Posts fetched: ${report.facebook.posts.length}`);
    for (const post of report.facebook.posts.slice(0, 12)) {
      lines.push(`- reactions ${post.metrics.reactions ?? "?"} / comments ${post.metrics.comments ?? "?"} / shares ${post.metrics.shares ?? "?"} - ${post.permalink_url} - ${post.text_preview}`);
    }
  } else {
    lines.push("## Facebook");
    lines.push(`Blocked: ${report.facebook?.error || "unknown error"}`);
    if (report.facebook?.code) lines.push(`Code: ${report.facebook.code}${report.facebook.subcode ? ` / subcode ${report.facebook.subcode}` : ""}`);
  }

  lines.push("");
  if (report.instagram?.ok) {
    const totals = totalInstagram(report.instagram.posts);
    lines.push(`## Instagram @${report.instagram.profile.username}`);
    lines.push(`Followers: ${report.instagram.profile.followers_count ?? "unknown"}`);
    lines.push(`Media count: ${report.instagram.profile.media_count ?? "unknown"}`);
    lines.push(`Posts fetched: ${report.instagram.posts.length}`);
    lines.push(`Totals: reach ${totals.reach}, likes ${totals.likes}, comments ${totals.comments}, shares ${totals.shares}, saved ${totals.saved}, interactions ${totals.total_interactions}`);
    lines.push("");
    lines.push("### Top Instagram Media");
    for (const post of [...report.instagram.posts].sort((a, b) => (b.metrics?.reach || 0) - (a.metrics?.reach || 0)).slice(0, 12)) {
      lines.push(`- reach ${post.metrics?.reach ?? "?"} / likes ${post.metrics?.likes ?? "?"} / comments ${post.metrics?.comments ?? "?"} / shares ${post.metrics?.shares ?? "?"} / saved ${post.metrics?.saved ?? "?"} - ${post.permalink} - ${post.text_preview}`);
    }
  } else {
    lines.push("## Instagram");
    lines.push(`Blocked: ${report.instagram?.error || "unknown error"}`);
    if (report.instagram?.code) lines.push(`Code: ${report.instagram.code}${report.instagram.subcode ? ` / subcode ${report.instagram.subcode}` : ""}`);
  }

  fs.writeFileSync(filePath, `${lines.join("\n")}\n`);
}

async function main() {
  loadEnvFile(ENV_PATH);
  const limit = Math.max(1, Math.min(500, Number(argValue("--limit", "100")) || 100));
  const outDir = argValue("--out-dir", DEFAULT_OUT_DIR);
  fs.mkdirSync(outDir, { recursive: true });

  const generatedAt = new Date().toISOString();
  const stamp = generatedAt.replace(/[:.]/g, "-");
  const report = {
    generatedAt,
    source: "Threads API + Meta Graph API read-only analytics",
    threads: await collectThreads({ limit }),
    facebook: await collectFacebook({ limit }),
    instagram: await collectInstagram({ limit }),
  };

  const jsonPath = path.join(outDir, `${stamp}-meta-analytics.json`);
  const mdPath = path.join(outDir, `${stamp}-meta-analytics.md`);
  fs.writeFileSync(jsonPath, `${JSON.stringify(report, null, 2)}\n`);
  writeMarkdown(report, mdPath);
  console.log(JSON.stringify({ ok: true, jsonPath, mdPath, facebookOk: !!report.facebook?.ok, instagramOk: !!report.instagram?.ok, threadsOk: !!report.threads?.ok }, null, 2));
}

main().catch((error) => {
  console.error(JSON.stringify({ ok: false, error: error.message }, null, 2));
  process.exit(1);
});
