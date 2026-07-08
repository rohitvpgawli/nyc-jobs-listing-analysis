// Copies the pipeline output into the site source tree before dev/build.
import { copyFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "..", "..", "data", "processed", "atlas.json");
const dest = join(here, "..", "src", "data", "atlas.json");

if (!existsSync(src)) {
  console.error(`Missing ${src} — run the pipeline first (see README).`);
  process.exit(1);
}
mkdirSync(dirname(dest), { recursive: true });
copyFileSync(src, dest);
console.log(`Copied atlas.json -> ${dest}`);
