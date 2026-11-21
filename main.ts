/**
 * VELMORA — The Poster for a Place That Isn't There.
 *
 * Writes the travel poster to /output/entry.png. Node 22, stdlib only.
 * The poster itself is drawn by compose.py (Pillow, deterministic);
 * this program validates it and copies it to the required output path.
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1048576;
const EXPECTED_WIDTH = 1024;
const EXPECTED_HEIGHT = 1024;

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = "/output";
const target = join(outDir, "entry.png");

const png = readFileSync(source);

if (png.length > MAX_BYTES) {
  throw new Error(`entry.png is ${png.length} bytes, over the ${MAX_BYTES} limit`);
}
if (!png.subarray(0, 8).equals(PNG_SIGNATURE)) {
  throw new Error("entry.png is not a PNG file");
}
if (png.readUInt32BE(16) !== EXPECTED_WIDTH || png.readUInt32BE(20) !== EXPECTED_HEIGHT) {
  throw new Error(
    `entry.png is ${png.readUInt32BE(16)}x${png.readUInt32BE(20)}, expected 1024x1024`,
  );
}

// IHDR bit depth must be 8 and colour type 2 (truecolour RGB).
const bitDepth = png[24];
const colourType = png[25];
if (bitDepth !== 8 || colourType !== 2) {
  throw new Error(
    `unexpected IHDR: bit depth ${bitDepth}, colour type ${colourType} (expected 8 / 2)`,
  );
}

// Walk the PNG chunk chain: reject truncation, require at least one IDAT
// chunk, and require a proper empty IEND terminator as the final chunk.
let offset = 8;
let idatCount = 0;
let lastType = "";
for (;;) {
  if (offset + 8 > png.length) {
    throw new Error("truncated PNG: chunk header runs past the end of the file");
  }
  const length = png.readUInt32BE(offset);
  const type = png.toString("latin1", offset + 4, offset + 8);
  if (offset + 12 + length > png.length) {
    throw new Error(`truncated PNG: ${type} chunk overruns the file`);
  }
  if (type === "IDAT") idatCount += 1;
  lastType = type;
  offset += 12 + length;
  if (type === "IEND") {
    if (length !== 0) throw new Error("IEND chunk must be empty");
    break;
  }
}
if (idatCount < 1) throw new Error("PNG has no IDAT chunk");
if (lastType !== "IEND") throw new Error("PNG does not end with IEND");

mkdirSync(outDir, { recursive: true });
writeFileSync(target, png);

// Byte-compare readback: what we wrote must be exactly what we read.
const back = readFileSync(target);
if (!back.equals(png)) {
  throw new Error("readback mismatch: /output/entry.png differs from entry.png");
}

console.log(`wrote ${target}: ${png.length} bytes, 1024x1024 PNG`);
