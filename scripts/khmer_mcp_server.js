#!/usr/bin/env node
/**
 * khmer_mcp_server.js - Model Context Protocol (MCP) Server for Khmer Localization (Node.js)
 *
 * Provides high-efficiency, zero-hallucination MCP tools for AI coding agents
 * (Claude Code, Cursor, Antigravity, Windsurf, Copilot, etc.) over JSON-RPC stdio.
 *
 * Zero external dependencies. Uses Node.js built-in standard library.
 */

"use strict";

const readline = require("readline");
const path = require("path");
const utils = require("./khmer_utils.js");

const SERVER_NAME = "khmer-localization-node";
const SERVER_VERSION = "2.1.0";

const TOOLS = [
  {
    name: "khmer_lookup_term",
    description: "Look up standardized Khmer UI terms from the 100+ vetted catalog to avoid hallucinations and inconsistent translations.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term in English, Khmer, or key (e.g. 'Settings', 'Save', 'Log Out', 'auth.sign_in')",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "khmer_normalize_phone",
    description: "Normalize a Cambodian phone number into ITU-T E.164 (+855) and domestic trunk formats with operator/type detection.",
    inputSchema: {
      type: "object",
      properties: {
        phone: {
          type: "string",
          description: "Raw Cambodian phone string (e.g. '012 345 678', '+855 23 210 022', '0971234567')",
        },
      },
      required: ["phone"],
    },
  },
  {
    name: "khmer_format_currency",
    description: "Format currency amounts following Cambodian banking rules (whole-riel integers for KHR, 2 decimals for USD).",
    inputSchema: {
      type: "object",
      properties: {
        amount: { type: "number", description: "Numeric amount to format" },
        currency: { type: "string", enum: ["KHR", "USD"], default: "KHR", description: "Currency code" },
      },
      required: ["amount"],
    },
  },
  {
    name: "khmer_spellout_words",
    description: "Convert an integer or monetary amount into formal Khmer spelled-out words for official receipts, invoices, and GDT tax compliance.",
    inputSchema: {
      type: "object",
      properties: {
        amount: { type: "number", description: "Amount or integer to spell out" },
        currency: { type: "string", enum: ["KHR", "USD", "NONE"], default: "KHR", description: "Currency suffix" },
      },
      required: ["amount"],
    },
  },
  {
    name: "khmer_khqr_crc",
    description: "Compute or verify EMVCo CRC16 checksum for NBC Bakong KHQR payment payloads.",
    inputSchema: {
      type: "object",
      properties: {
        payload: {
          type: "string",
          description: "KHQR payload (either ending with '6304' to compute CRC, or full string to verify)",
        },
      },
      required: ["payload"],
    },
  },
  {
    name: "khmer_lint_text",
    description: "Fast static linting of Khmer text for Unicode corruption, dotted circles (U+25CC), trailing Coeng, royal register words, and decimal KHR bugs.",
    inputSchema: {
      type: "object",
      properties: {
        text: { type: "string", description: "Khmer string to lint" },
      },
      required: ["text"],
    },
  },
  {
    name: "khmer_sort_words",
    description: "Sort a list of Khmer words according to the official Chuon Nath dictionary order.",
    inputSchema: {
      type: "object",
      properties: {
        words: {
          type: "array",
          items: { type: "string" },
          description: "List of Khmer words to sort",
        },
      },
      required: ["words"],
    },
  },
];

function handleToolCall(name, args = {}) {
  switch (name) {
    case "khmer_lookup_term": {
      const q = args.query || "";
      return utils.lookupUiTerm(q);
    }
    case "khmer_normalize_phone": {
      const phone = args.phone || "";
      return utils.normalizeCambodianPhone(phone);
    }
    case "khmer_format_currency": {
      const amount = Number(args.amount || 0);
      const curr = (args.currency || "KHR").toUpperCase();
      if (curr === "KHR") {
        return { formatted: utils.formatKHR(amount), currency: "KHR", amount };
      }
      return { formatted: utils.formatUSD(amount), currency: "USD", amount };
    }
    case "khmer_spellout_words": {
      const amount = Number(args.amount || 0);
      const curr = (args.currency || "KHR").toUpperCase();
      if (curr === "NONE") {
        return { words: utils.integerToKhmerWords(Math.floor(amount)), amount };
      }
      return { words: utils.formatCurrencyKhmerWords(amount, curr), currency: curr, amount };
    }
    case "khmer_khqr_crc": {
      const payload = args.payload || "";
      if (payload.endsWith("6304")) {
        const crc = utils.calculateKhqrCrc16(payload);
        return { computed_crc: crc, full_khqr: payload + crc };
      }
      const isValid = utils.verifyKhqr(payload);
      return { is_valid: isValid, payload };
    }
    case "khmer_lint_text": {
      const text = args.text || "";
      return utils.lintKhmerText(text);
    }
    case "khmer_sort_words": {
      const words = Array.isArray(args.words) ? args.words : [];
      return { sorted: utils.sortKhmerWords(words) };
    }
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

function sendResponse(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false,
});

rl.on("line", (line) => {
  const trimmed = line.trim();
  if (!trimmed) return;

  let req;
  try {
    req = JSON.parse(trimmed);
  } catch (err) {
    return;
  }

  const reqId = req.id;
  const method = req.method;
  const params = req.params || {};

  if (method === "initialize") {
    sendResponse({
      jsonrpc: "2.0",
      id: reqId,
      result: {
        protocolVersion: "2024-11-05",
        serverInfo: { name: SERVER_NAME, version: SERVER_VERSION },
        capabilities: { tools: {} },
      },
    });
  } else if (method === "notifications/initialized") {
    // Ack
  } else if (method === "tools/list") {
    sendResponse({
      jsonrpc: "2.0",
      id: reqId,
      result: { tools: TOOLS },
    });
  } else if (method === "tools/call") {
    const toolName = params.name;
    const toolArgs = params.arguments || {};
    try {
      const resultData = handleToolCall(toolName, toolArgs);
      sendResponse({
        jsonrpc: "2.0",
        id: reqId,
        result: {
          content: [
            {
              type: "text",
              text: JSON.stringify(resultData, null, 2),
            },
          ],
        },
      });
    } catch (e) {
      sendResponse({
        jsonrpc: "2.0",
        id: reqId,
        error: { code: -32000, message: e.message },
      });
    }
  } else if (method === "ping") {
    sendResponse({ jsonrpc: "2.0", id: reqId, result: {} });
  } else {
    if (reqId !== undefined) {
      sendResponse({
        jsonrpc: "2.0",
        id: reqId,
        error: { code: -32601, message: `Method not found: ${method}` },
      });
    }
  }
});
