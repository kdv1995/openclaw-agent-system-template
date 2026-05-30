#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const CONFIG_PATH = path.join(ROOT, 'config.json');
const STATE_PATH = path.join(ROOT, 'state', 'seen.json');
const REPORTS_DIR = path.join(ROOT, 'reports');
const OPENCLAW_ENV = process.env.OPENCLAW_ENV_FILE || path.join(ROOT, '.env');
const OPENCLAW_CONFIG = process.env.OPENCLAW_CONFIG_FILE || path.join(process.env.HOME || '.', '.openclaw', 'openclaw.json');
const DEFAULT_CHAT_ID = process.env.OPENCLAW_TELEGRAM_TARGET || '';

const args = new Set(process.argv.slice(2));
const shouldNotify = args.has('--notify');
const forceNotify = args.has('--force');

function nowKyivDate() {
  return new Intl.DateTimeFormat('sv-SE', {
    timeZone: 'Europe/Kyiv',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(new Date()).replace(' ', 'T').replaceAll(':', '-');
}

async function readJson(file, fallback) {
  try {
    return JSON.parse(await fs.readFile(file, 'utf8'));
  } catch (error) {
    if (error.code === 'ENOENT') return fallback;
    throw error;
  }
}

async function loadDotEnv(file) {
  try {
    const text = await fs.readFile(file, 'utf8');
    for (const line of text.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const eq = trimmed.indexOf('=');
      if (eq === -1) continue;
      const key = trimmed.slice(0, eq).trim();
      let value = trimmed.slice(eq + 1).trim();
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      if (!(key in process.env)) process.env[key] = value;
    }
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
}

async function getTelegramToken() {
  if (process.env.TELEGRAM_BOT_TOKEN || process.env.OPENCLAW_TELEGRAM_BOT_TOKEN) {
    return process.env.TELEGRAM_BOT_TOKEN || process.env.OPENCLAW_TELEGRAM_BOT_TOKEN;
  }
  try {
    const cfg = JSON.parse(await fs.readFile(OPENCLAW_CONFIG, 'utf8'));
    const channels = cfg.channels || cfg.messaging?.channels || [];
    const telegram = Array.isArray(channels)
      ? channels.find((c) => c.type === 'telegram' || c.provider === 'telegram')
      : null;
    return telegram?.botToken || telegram?.token || '';
  } catch {
    return '';
  }
}

async function sendTelegram(chatId, text) {
  const token = await getTelegramToken();
  if (!token) throw new Error('Telegram bot token not found');
  const response = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      disable_web_page_preview: true
    })
  });
  if (!response.ok) {
    throw new Error(`Telegram send failed: HTTP ${response.status} ${await response.text()}`);
  }
}

async function getEbayToken() {
  const clientId = process.env.EBAY_CLIENT_ID || process.env.EBAY_APP_ID;
  const clientSecret = process.env.EBAY_CLIENT_SECRET || process.env.EBAY_CERT_ID;
  if (!clientId || !clientSecret) {
    return {
      ok: false,
      reason: 'Missing EBAY_CLIENT_ID/EBAY_CLIENT_SECRET in environment or configured .env'
    };
  }
  const body = new URLSearchParams({
    grant_type: 'client_credentials',
    scope: 'https://api.ebay.com/oauth/api_scope'
  });
  const response = await fetch('https://api.ebay.com/identity/v1/oauth2/token', {
    method: 'POST',
    headers: {
      authorization: `Basic ${Buffer.from(`${clientId}:${clientSecret}`).toString('base64')}`,
      'content-type': 'application/x-www-form-urlencoded'
    },
    body
  });
  if (!response.ok) {
    return {
      ok: false,
      reason: `eBay OAuth failed: HTTP ${response.status} ${await response.text()}`
    };
  }
  const json = await response.json();
  return { ok: true, token: json.access_token };
}

function buildFilter(search) {
  const filters = [];
  if (search.minPrice != null || search.maxPrice != null) {
    const min = search.minPrice ?? '';
    const max = search.maxPrice ?? '';
    filters.push(`price:[${min}..${max}]`);
  }
  if (search.conditions?.length) filters.push(`conditions:{${search.conditions.join('|')}}`);
  if (search.buyingOptions?.length) filters.push(`buyingOptions:{${search.buyingOptions.join('|')}}`);
  return filters.join(',');
}

async function searchEbay(token, config, search) {
  const url = new URL('https://api.ebay.com/buy/browse/v1/item_summary/search');
  if (search.query) url.searchParams.set('q', search.query);
  if (search.categoryIds?.length) url.searchParams.set('category_ids', search.categoryIds.join(','));
  url.searchParams.set('limit', String(search.limit || config.limit || 30));
  url.searchParams.set('sort', 'newlyListed');
  const filter = buildFilter(search);
  if (filter) url.searchParams.set('filter', filter);

  const response = await fetch(url, {
    headers: {
      authorization: `Bearer ${token}`,
      'x-ebay-c-marketplace-id': config.marketplace || 'EBAY_US'
    }
  });
  if (!response.ok) {
    throw new Error(`eBay search failed for ${search.id}: HTTP ${response.status} ${await response.text()}`);
  }
  const json = await response.json();
  return json.itemSummaries || [];
}

function textMatch(item, keywords) {
  const haystack = `${item.title || ''} ${item.shortDescription || ''}`.toLowerCase();
  return keywords.every((keyword) => haystack.includes(String(keyword).toLowerCase()));
}

function hasExcluded(item, keywords) {
  const haystack = `${item.title || ''} ${item.shortDescription || ''}`.toLowerCase();
  return keywords.some((keyword) => haystack.includes(String(keyword).toLowerCase()));
}

function scoreItem(item, search) {
  const rules = search.scoreRules || {};
  let score = 50;
  const price = Number(item.price?.value);
  if (Number.isFinite(price) && search.maxPrice && price <= search.maxPrice) {
    score += rules.belowMaxPriceBonus ?? 20;
  }
  if (item.shippingOptions?.some((s) => Number(s.shippingCost?.value || 0) === 0)) {
    score += rules.freeShippingBonus ?? 8;
  }
  const feedback = Number(item.seller?.feedbackPercentage);
  if (Number.isFinite(feedback) && feedback >= (rules.sellerFeedbackMin ?? 98)) {
    score += rules.sellerFeedbackBonus ?? 10;
  }
  if (item.itemCreationDate && rules.newListingHours) {
    const ageHours = (Date.now() - new Date(item.itemCreationDate).getTime()) / 36e5;
    if (ageHours <= rules.newListingHours) score += rules.newListingBonus ?? 12;
  }
  if (hasExcluded(item, search.excludeKeywords || [])) score -= 100;
  if (!textMatch(item, search.requiredKeywords || [])) score -= 40;
  return score;
}

function normalizeItem(item, search) {
  const price = item.price ? `${item.price.value} ${item.price.currency}` : 'n/a';
  const shipping = item.shippingOptions?.[0]?.shippingCost
    ? `${item.shippingOptions[0].shippingCost.value} ${item.shippingOptions[0].shippingCost.currency}`
    : 'n/a';
  return {
    searchId: search.id,
    searchLabel: search.label || search.id,
    itemId: item.itemId,
    title: item.title,
    price,
    rawPrice: Number(item.price?.value),
    currency: item.price?.currency,
    shipping,
    condition: item.condition,
    buyingOptions: item.buyingOptions || [],
    seller: item.seller?.username,
    feedback: item.seller?.feedbackPercentage,
    url: item.itemWebUrl,
    createdAt: item.itemCreationDate,
    score: scoreItem(item, search)
  };
}

function formatDigest(run) {
  if (run.blocker) {
    return [
      'eBay Watch blocker',
      '',
      run.blocker,
      '',
      `Report: ${run.reportPath}`
    ].join('\n');
  }
  const lines = [];
  lines.push('eBay Watch report');
  lines.push('');
  lines.push(`Searches checked: ${run.searchesChecked}`);
  lines.push(`Items found: ${run.itemsFound}`);
  lines.push(`New items: ${run.newItems.length}`);
  lines.push(`Top matches: ${run.topItems.length}`);
  lines.push('');
  for (const item of run.topItems.slice(0, 8)) {
    lines.push(`• [${item.score}] ${item.title}`);
    lines.push(`  ${item.price}, ship ${item.shipping}, ${item.condition || 'condition n/a'}`);
    lines.push(`  ${item.url}`);
  }
  if (!run.topItems.length) lines.push('No new matching items this run.');
  lines.push('');
  lines.push(`Report: ${run.reportPath}`);
  return lines.join('\n');
}

function markdownReport(run) {
  const lines = [];
  lines.push(`# eBay Watch Report`);
  lines.push('');
  lines.push(`Generated: ${run.generatedAt}`);
  lines.push('');
  if (run.blocker) {
    lines.push(`## Blocker`);
    lines.push('');
    lines.push(run.blocker);
    lines.push('');
    return lines.join('\n');
  }
  lines.push(`## Summary`);
  lines.push('');
  lines.push(`- Searches checked: ${run.searchesChecked}`);
  lines.push(`- Items found: ${run.itemsFound}`);
  lines.push(`- New items: ${run.newItems.length}`);
  lines.push(`- Top matches: ${run.topItems.length}`);
  lines.push('');
  lines.push(`## Top Items`);
  lines.push('');
  for (const item of run.topItems) {
    lines.push(`### ${item.title}`);
    lines.push(`- Score: ${item.score}`);
    lines.push(`- Search: ${item.searchLabel}`);
    lines.push(`- Price: ${item.price}`);
    lines.push(`- Shipping: ${item.shipping}`);
    lines.push(`- Condition: ${item.condition || 'n/a'}`);
    lines.push(`- Seller: ${item.seller || 'n/a'} (${item.feedback || 'n/a'}%)`);
    lines.push(`- Created: ${item.createdAt || 'n/a'}`);
    lines.push(`- URL: ${item.url}`);
    lines.push('');
  }
  if (!run.topItems.length) lines.push('No new matching items this run.');
  return lines.join('\n');
}

async function main() {
  await loadDotEnv(OPENCLAW_ENV);
  await fs.mkdir(REPORTS_DIR, { recursive: true });
  await fs.mkdir(path.dirname(STATE_PATH), { recursive: true });
  const config = await readJson(CONFIG_PATH, null);
  if (!config) throw new Error(`Missing config: ${CONFIG_PATH}`);

  const generatedAt = nowKyivDate();
  const reportBase = path.join(REPORTS_DIR, `${generatedAt}-ebay-watch`);
  const enabled = (config.searches || []).filter((s) => s.enabled);
  let run = {
    generatedAt,
    searchesChecked: 0,
    itemsFound: 0,
    newItems: [],
    topItems: [],
    reportPath: `${reportBase}.md`
  };

  if (!enabled.length) {
    run.blocker = 'No enabled searches in ebay-watch/config.json. Set a query/category and enabled=true.';
  } else {
    const auth = await getEbayToken();
    if (!auth.ok) {
      run.blocker = auth.reason;
    } else {
      const state = await readJson(STATE_PATH, { seenItemIds: {}, runs: [] });
      const all = [];
      for (const search of enabled) {
        const items = await searchEbay(auth.token, config, search);
        run.searchesChecked += 1;
        run.itemsFound += items.length;
        for (const raw of items) {
          const item = normalizeItem(raw, search);
          if (item.score < 0) continue;
          all.push(item);
        }
      }
      const newItems = all.filter((item) => forceNotify || !state.seenItemIds[item.itemId]);
      for (const item of all) state.seenItemIds[item.itemId] = { firstSeenAt: generatedAt, title: item.title, url: item.url };
      state.runs = [...(state.runs || []), { generatedAt, itemsFound: run.itemsFound, newItems: newItems.length }].slice(-100);
      await fs.writeFile(STATE_PATH, JSON.stringify(state, null, 2));
      run.newItems = newItems;
      run.topItems = (config.notifyOnlyNew === false ? all : newItems)
        .sort((a, b) => b.score - a.score || (a.rawPrice || Infinity) - (b.rawPrice || Infinity))
        .slice(0, 20);
    }
  }

  await fs.writeFile(`${reportBase}.json`, JSON.stringify(run, null, 2));
  await fs.writeFile(`${reportBase}.md`, markdownReport(run));

  const digest = formatDigest(run);
  console.log(digest);
  if (shouldNotify) {
    await sendTelegram(config.telegramChatId || DEFAULT_CHAT_ID, digest.slice(0, 3900));
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
