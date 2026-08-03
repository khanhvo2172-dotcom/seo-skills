#!/usr/bin/env node
/*
 * sync-brand.js — single source of truth for TrueProfit brand facts.
 *
 * Edit _brand/trueprofit-brand.md, then run:  node _brand/sync-brand.js
 *
 * For every skill listed in TARGETS, the master content is injected between
 *   <!-- BRAND:START --> ... <!-- BRAND:END -->
 * inside that skill's "## TrueProfit Brand Reference" section. On the first run
 * the hand-written brand section is replaced with the markers; every run after
 * just refreshes the text between them. Skills stay self-contained and portable
 * (the facts live physically in each SKILL.md), so there is no runtime path
 * dependency on this file.
 *
 * To bring a new skill under shared brand context: give it a
 * "## TrueProfit Brand Reference" heading followed by a "---" line (or the
 * BRAND markers directly), then add its folder name to TARGETS and re-run.
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const MASTER_FILE = path.join(__dirname, "trueprofit-brand.md");
const START = "<!-- BRAND:START -->";
const END = "<!-- BRAND:END -->";

const TARGETS = [
  "trueprofit-guest-post",
  "trueprofit-guest-post-full-article",
];

const master = fs.readFileSync(MASTER_FILE, "utf8").trim();
const changed = [];
const skipped = [];

for (const name of TARGETS) {
  const file = path.join(ROOT, name, "SKILL.md");
  if (!fs.existsSync(file)) { skipped.push(`${name} (SKILL.md missing)`); continue; }

  let src = fs.readFileSync(file, "utf8");
  const before = src;

  // Match the file's own line ending so we never create mixed EOLs.
  const eol = src.includes("\r\n") ? "\r\n" : "\n";
  const body = master.split(/\r?\n/).join(eol);
  const block = `${START}${eol}${body}${eol}${END}`;

  if (src.includes(START) && src.includes(END)) {
    // Refresh existing block.
    src = src.replace(new RegExp(START + "[\\s\\S]*?" + END), block);
  } else {
    // First-time wiring: replace "## TrueProfit Brand Reference ... <rule>".
    const section = /## TrueProfit Brand Reference[\s\S]*?\r?\n---\r?\n/;
    if (!section.test(src)) { skipped.push(`${name} (no brand section or markers)`); continue; }
    src = src.replace(section, `## TrueProfit Brand Reference${eol}${eol}${block}${eol}${eol}---${eol}`);
  }

  if (src !== before) { fs.writeFileSync(file, src); changed.push(name); }
}

console.log("Master:", path.relative(ROOT, MASTER_FILE));
console.log(`Updated ${changed.length} skill(s):`, changed.join(", ") || "(none)");
if (skipped.length) console.log("Skipped:", skipped.join("; "));
