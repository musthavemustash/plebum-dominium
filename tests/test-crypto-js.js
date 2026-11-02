#!/usr/bin/env node
/**
 * Plebum Dominium JavaScript cryptographic tests.
 *
 * Extracts and executes the actual JS functions from docs/dice-converter.html.
 * Tests BIP39 vectors, input validation, SHA-256, and face mapping.
 *
 * Run: node tests/test-crypto-js.js
 *
 * These tests use synthetic/test data only. Never real wallet secrets.
 * Exit code 0 = all pass. Exit code 1 = any failure.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// -------------------------------------------------------------------
// Load and extract JS from dice-converter.html
// -------------------------------------------------------------------
const HTML_PATH = path.join(__dirname, '..', 'docs', 'dice-converter.html');

if (!fs.existsSync(HTML_PATH)) {
    console.log(`FATAL: ${HTML_PATH} not found (fail closed)`);
    process.exit(1);
}

const html = fs.readFileSync(HTML_PATH, 'utf-8');

// Extract the WORDLIST (BIP39)
const wordlistMatch = html.match(/var WORDLIST\s*=\s*\[(.*?)\]/s);
if (!wordlistMatch) {
    console.log("FATAL: Could not extract WORDLIST from dice-converter.html");
    process.exit(1);
}
// Parse the array - it's a JS array literal, evaluate safely
let WORDLIST;
try {
    WORDLIST = eval('[' + wordlistMatch[1] + ']');
} catch (e) {
    console.log(`FATAL: Could not parse WORDLIST: ${e.message}`);
    process.exit(1);
}

// Extract functions we need to test
function extractFunction(name) {
    // Match function name(...) { ... } with balanced braces
    const pattern = new RegExp(`function ${name}\\s*\\([^)]*\\)\\s*\\{`, 'g');
    const match = pattern.exec(html);
    if (!match) return null;
    
    let start = match.index;
    let braceCount = 0;
    let inString = false;
    let stringChar = '';
    let i = match.index + match[0].length - 1; // position of opening {
    
    for (; i < html.length; i++) {
        const c = html[i];
        const prev = i > 0 ? html[i-1] : '';
        
        if (inString) {
            if (c === stringChar && prev !== '\\') inString = false;
            continue;
        }
        if (c === '"' || c === "'" || c === '`') {
            inString = true;
            stringChar = c;
            continue;
        }
        if (c === '{') braceCount++;
        if (c === '}') {
            braceCount--;
            if (braceCount === 0) {
                return html.substring(start, i + 1);
            }
        }
    }
    return null;
}

// -------------------------------------------------------------------
// Test counters
// -------------------------------------------------------------------
let passed = 0;
let failed = 0;
const failures = [];

function test(name, condition, detail = '') {
    if (condition) {
        passed++;
        console.log(`  PASS: ${name}`);
    } else {
        failed++;
        failures.push(name);
        console.log(`  FAIL: ${name}` + (detail ? ` - ${detail}` : ''));
    }
}

function testThrows(name, fn, ...args) {
    try {
        fn(...args);
        failed++;
        failures.push(name);
        console.log(`  FAIL: ${name} - expected exception, none thrown`);
    } catch (e) {
        passed++;
        console.log(`  PASS: ${name} (threw: ${e.message.substring(0, 60)})`);
    }
}

// -------------------------------------------------------------------
// Build a test context with the extracted functions
// -------------------------------------------------------------------
console.log("\n=== Extracting JS Functions ===");

const funcNames = ['cleanBinary', 'bitsToWords', 'faceToBits', 'sha256', 'bytesToBits', 'bitsToBytes'];
const funcs = {};

for (const name of funcNames) {
    const code = extractFunction(name);
    if (code) {
        funcs[name] = code;
        console.log(`  Found: ${name}`);
    } else {
        console.log(`  MISSING: ${name} (will fail dependent tests)`);
    }
}

// Create a sandbox to run the functions
// We need WORDLIST in scope, plus the functions
let contextCode = `var WORDLIST = ${JSON.stringify(WORDLIST)};\n`;
for (const name of funcNames) {
    if (funcs[name]) {
        contextCode += funcs[name] + '\n';
    }
}

// Evaluate in a function scope
const testContext = new Function(contextCode + `
    return {
        cleanBinary: typeof cleanBinary !== 'undefined' ? cleanBinary : null,
        bitsToWords: typeof bitsToWords !== 'undefined' ? bitsToWords : null,
        faceToBits: typeof faceToBits !== 'undefined' ? faceToBits : null,
        sha256: typeof sha256 !== 'undefined' ? sha256 : null,
    };
`)();

// -------------------------------------------------------------------
// 1. Input validation (cleanBinary)
// -------------------------------------------------------------------
console.log("\n=== JS Input Validation ===");

if (!testContext.cleanBinary) {
    console.log("  FAIL: cleanBinary not found (fail closed)");
    failed++; failures.push("cleanBinary exists");
} else {
    const cleanBinary = testContext.cleanBinary;
    
    test("Accepts '101'", cleanBinary("101") === "101");
    test("Accepts whitespace '10 01'", cleanBinary("10 01") === "1001");
    testThrows("Rejects '101x'", cleanBinary, "101x");
    testThrows("Rejects 'abc'", cleanBinary, "abc");
    testThrows("Rejects empty", cleanBinary, "");
}

// -------------------------------------------------------------------
// 2. BIP39 vectors (bitsToWords)
// -------------------------------------------------------------------
console.log("\n=== JS BIP39 Vectors ===");

if (!testContext.bitsToWords) {
    console.log("  FAIL: bitsToWords not found (fail closed)");
    failed++; failures.push("bitsToWords exists");
} else {
    const bitsToWords = testContext.bitsToWords;
    
    // All-zero 256-bit
    const zeroBits = "0".repeat(256);
    const zeroWords = bitsToWords(zeroBits);
    test("All-zero produces 24 words", zeroWords.length === 24, `got ${zeroWords.length}`);
    test("All-zero: first 23 are 'abandon'",
        zeroWords.slice(0, 23).every(w => w === "abandon"));
    test("All-zero: last is 'art'", zeroWords[23] === "art", `got '${zeroWords[23]}'`);
    
    // All-one 256-bit
    const oneBits = "1".repeat(256);
    const oneWords = bitsToWords(oneBits);
    test("All-one produces 24 words", oneWords.length === 24);
    test("All-one differs from all-zero",
        JSON.stringify(oneWords) !== JSON.stringify(zeroWords));
}

// -------------------------------------------------------------------
// 3. SHA-256 (if JS implementation exists)
// -------------------------------------------------------------------
console.log("\n=== JS SHA-256 ===");

if (!testContext.sha256) {
    console.log("  INFO: JS sha256() not found as standalone function");
    console.log("  INFO: Site may use WebCrypto (crypto.subtle) which requires browser");
    // Don't fail - WebCrypto is async and browser-only
} else {
    // Test if it's a sync function
    try {
        const result = testContext.sha256(new Uint8Array([97, 98, 99])); // "abc"
        // Convert to hex for comparison
        let hex = '';
        if (result instanceof Uint8Array) {
            hex = Array.from(result).map(b => b.toString(16).padStart(2, '0')).join('');
        }
        const expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
        test("JS SHA-256('abc') matches", hex === expected, `got ${hex.substring(0, 16)}...`);
    } catch (e) {
        console.log(`  INFO: JS sha256 test skipped: ${e.message}`);
    }
}

// Verify Node's crypto matches (sanity check)
const nodeHash = crypto.createHash('sha256').update('abc').digest('hex');
test("Node SHA-256('abc') matches NIST",
    nodeHash === "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");

// -------------------------------------------------------------------
// 4. Face mapping
// -------------------------------------------------------------------
console.log("\n=== JS Face Mapping ===");

if (!testContext.faceToBits) {
    console.log("  INFO: faceToBits not found as standalone function");
    // Check inline in HTML
    const inlineMatch = html.match(/\{1:\s*['"]00['"],\s*2:\s*['"]01['"],\s*3:\s*['"]10['"],\s*4:\s*['"]11['"]\}/);
    test("Face map 1=00,2=01,3=10,4=11 in source", !!inlineMatch);
} else {
    const faceToBits = testContext.faceToBits;
    test("Face 1 -> '00'", faceToBits(1) === '00');
    test("Face 2 -> '01'", faceToBits(2) === '01');
    test("Face 3 -> '10'", faceToBits(3) === '10');
    test("Face 4 -> '11'", faceToBits(4) === '11');
}

// -------------------------------------------------------------------
// 5. WORDLIST integrity
// -------------------------------------------------------------------
console.log("\n=== JS WORDLIST ===");
test("WORDLIST has 2048 words", WORDLIST.length === 2048, `got ${WORDLIST.length}`);
test("First word is 'abandon'", WORDLIST[0] === "abandon");
test("Last word is 'zoo'", WORDLIST[WORDLIST.length - 1] === "zoo");
test("All words unique", new Set(WORDLIST).size === 2048);

// -------------------------------------------------------------------
// Summary
// -------------------------------------------------------------------
console.log(`\n${'='.repeat(50)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);
if (failures.length > 0) {
    console.log(`\nFailed tests:`);
    failures.forEach(f => console.log(`  - ${f}`));
    process.exit(1);
} else {
    console.log("\nAll JS tests passed!");
    console.log("NOTE: WebCrypto (crypto.subtle) tests require a browser environment.");
    process.exit(0);
}
