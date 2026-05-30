#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "../../..");
const ENV_PATH = process.env.OPENCLAW_ENV_FILE || path.join(process.env.HOME || ".", ".openclaw", ".env");
const STATE_PATH =
  process.env.THREADS_TOKEN_STATE_PATH || path.join(ROOT, "threads", "state", "threads-token-state.json");

function parseEnv(text) {
  const env = {};
  for (const line of text.split(/\r?\n/)) {
    if (!line || line.trim().startsWith("#")) continue;
    const match = line.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (match) env[match[1]] = match[2].replace(/^['"]|['"]$/g, "");
  }
  return env;
}

function upsertEnvValue(text, key, value) {
  const escaped = value.replace(/"/g, '\\"');
  const line = `${key}="${escaped}"`;
  const pattern = new RegExp(`^${key}=.*$`, "m");
  return pattern.test(text) ? text.replace(pattern, line) : `${text.trimEnd()}\n${line}\n`;
}

async function callTokenEndpoint(url, params) {
  const endpoint = new URL(url);
  for (const [key, value] of Object.entries(params)) {
    endpoint.searchParams.set(key, value);
  }
  const response = await fetch(endpoint);
  const body = await response.json().catch(() => ({}));
  return { ok: response.ok && !body.error && !!body.access_token, status: response.status, body };
}

async function main() {
  const envText = fs.readFileSync(ENV_PATH, "utf8");
  const env = parseEnv(envText);
  const currentToken = env.THREADS_ACCESS_TOKEN;
  const clientSecret = env.THREADS_APP_SECRET || env.META_APP_SECRET;

  if (!currentToken) {
    throw new Error("THREADS_ACCESS_TOKEN is missing in the configured .env file");
  }

  let result = await callTokenEndpoint("https://graph.threads.net/refresh_access_token", {
    grant_type: "th_refresh_token",
    access_token: currentToken,
  });

  let method = "refresh_access_token";

  if (!result.ok && clientSecret) {
    result = await callTokenEndpoint("https://graph.threads.net/access_token", {
      grant_type: "th_exchange_token",
      client_secret: clientSecret,
      access_token: currentToken,
    });
    method = "exchange_token";
  }

  if (!result.ok) {
    const err = result.body.error || result.body;
    fs.writeFileSync(
      STATE_PATH,
      JSON.stringify(
        {
          refreshedAt: new Date().toISOString(),
          ok: false,
          method,
          status: result.status,
          error: {
            message: err.message,
            code: err.code,
            subcode: err.error_subcode,
            type: err.type,
          },
        },
        null,
        2,
      ) + "\n",
    );
    console.log(
      JSON.stringify(
        {
          ok: false,
          method,
          status: result.status,
          error: {
            message: err.message,
            code: err.code,
            subcode: err.error_subcode,
          },
        },
        null,
        2,
      ),
    );
    process.exit(1);
  }

  const expiresIn = Number(result.body.expires_in || 0);
  const expiresAt = expiresIn ? new Date(Date.now() + expiresIn * 1000).toISOString() : null;
  const updatedEnv = upsertEnvValue(envText, "THREADS_ACCESS_TOKEN", result.body.access_token);
  fs.writeFileSync(ENV_PATH, updatedEnv);
  fs.writeFileSync(
    STATE_PATH,
    JSON.stringify(
      {
        refreshedAt: new Date().toISOString(),
        ok: true,
        method,
        token_type: result.body.token_type || "bearer",
        expires_in: expiresIn || null,
        expires_at: expiresAt,
      },
      null,
      2,
    ) + "\n",
  );

  console.log(
    JSON.stringify(
      {
        ok: true,
        method,
        token_type: result.body.token_type || "bearer",
        expires_in: expiresIn || null,
        expires_at: expiresAt,
      },
      null,
      2,
    ),
  );
}

main().catch((error) => {
  console.error(JSON.stringify({ ok: false, error: error.message }, null, 2));
  process.exit(1);
});
