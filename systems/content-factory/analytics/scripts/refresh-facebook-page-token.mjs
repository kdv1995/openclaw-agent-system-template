#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../..");
const ENV_PATH = process.env.OPENCLAW_ENV_FILE || path.join(process.env.HOME || ".", ".openclaw", ".env");
const STATE_PATH =
  process.env.FB_PAGE_TOKEN_STATE_PATH || path.join(ROOT, "analytics", "reports", "facebook-token-state.json");

function loadEnvText() {
  return fs.existsSync(ENV_PATH) ? fs.readFileSync(ENV_PATH, "utf8") : "";
}

function parseEnv(text) {
  const env = {};
  for (const line of text.split(/\r?\n/)) {
    if (!line || line.trim().startsWith("#")) continue;
    const match = line.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (match) env[match[1]] = match[2].trim().replace(/^['"]|['"]$/g, "");
  }
  return env;
}

function upsertEnvValue(text, key, value) {
  const escaped = value.replace(/"/g, '\\"');
  const line = `${key}="${escaped}"`;
  const pattern = new RegExp(`^${key}=.*$`, "m");
  return pattern.test(text) ? text.replace(pattern, line) : `${text.trimEnd()}\n${line}\n`;
}

function argValue(name) {
  const index = process.argv.indexOf(name);
  return index === -1 ? "" : process.argv[index + 1] || "";
}

function appsecretProof(token, secret) {
  return crypto.createHmac("sha256", secret).update(token).digest("hex");
}

async function graphGet(path, params) {
  const url = new URL(`https://graph.facebook.com/v24.0/${path}`);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, String(value));
  }
  const response = await fetch(url);
  const body = await response.json().catch(() => ({}));
  if (!response.ok || body.error) {
    const err = body.error || body;
    const error = new Error(err.message || `${response.status} ${response.statusText}`);
    error.status = response.status;
    error.code = err.code;
    error.subcode = err.error_subcode;
    error.type = err.type;
    throw error;
  }
  return body;
}

function writeState(state) {
  fs.mkdirSync(STATE_PATH.replace(/\/[^/]+$/, ""), { recursive: true });
  fs.writeFileSync(STATE_PATH, `${JSON.stringify({ checkedAt: new Date().toISOString(), ...state }, null, 2)}\n`);
}

async function main() {
  const envText = loadEnvText();
  const env = parseEnv(envText);

  const appId = env.META_APP_ID || env.FACEBOOK_APP_ID;
  const appSecret = env.META_APP_SECRET || env.FACEBOOK_APP_SECRET;
  const pageId = env.FB_PAGE_ID;
  const userToken = argValue("--user-token") || env.FB_USER_ACCESS_TOKEN || env.META_USER_ACCESS_TOKEN;

  if (!appId || !appSecret || !pageId) {
    throw new Error("META_APP_ID/META_APP_SECRET/FB_PAGE_ID are required in the configured .env file");
  }
  if (!userToken) {
    writeState({
      ok: false,
      blocked: "missing_fresh_user_token",
      next: "Add a fresh short-lived Facebook User Access Token to FB_USER_ACCESS_TOKEN or META_USER_ACCESS_TOKEN, then rerun this script.",
    });
    throw new Error("Fresh Facebook User Access Token is required. Set FB_USER_ACCESS_TOKEN or META_USER_ACCESS_TOKEN.");
  }

  const exchanged = await graphGet("oauth/access_token", {
    grant_type: "fb_exchange_token",
    client_id: appId,
    client_secret: appSecret,
    fb_exchange_token: userToken,
  });

  const longLivedUserToken = exchanged.access_token;
  if (!longLivedUserToken) throw new Error("Meta did not return a long-lived user token");

  const accounts = await graphGet("me/accounts", {
    fields: "id,name,access_token,tasks",
    access_token: longLivedUserToken,
    appsecret_proof: appsecretProof(longLivedUserToken, appSecret),
  });

  const page = (accounts.data || []).find((item) => item.id === pageId);
  if (!page?.access_token) {
    writeState({
      ok: false,
      blocked: "page_token_not_found",
      pageId,
      pagesReturned: (accounts.data || []).map((item) => ({ id: item.id, name: item.name })),
    });
    throw new Error(`Could not find page access token for FB_PAGE_ID=${pageId}`);
  }

  let updatedEnv = upsertEnvValue(envText, "FB_USER_ACCESS_TOKEN", longLivedUserToken);
  updatedEnv = upsertEnvValue(updatedEnv, "FB_PAGE_ACCESS_TOKEN", page.access_token);
  fs.writeFileSync(ENV_PATH, updatedEnv);

  writeState({
    ok: true,
    pageId,
    pageName: page.name,
    userTokenType: exchanged.token_type || "bearer",
    userTokenExpiresIn: exchanged.expires_in || null,
    pageTokenUpdated: true,
  });

  console.log(
    JSON.stringify(
      {
        ok: true,
        pageId,
        pageName: page.name,
        userTokenExpiresIn: exchanged.expires_in || null,
        pageTokenUpdated: true,
        statePath: STATE_PATH,
      },
      null,
      2,
    ),
  );
}

main().catch((error) => {
  console.error(JSON.stringify({ ok: false, error: error.message, statePath: STATE_PATH }, null, 2));
  process.exit(1);
});
