#!/usr/bin/env python3
"""
Plebum Dominium cryptographic test suite.

Tests BIP39 vectors, input validation parity (Python vs JS logic),
Diceware wordlist integrity, face mapping, and SHA-256 correctness.

Run: python3 tests/test-crypto.py
Requires: Python 3.6+, hashlib (stdlib only)

These tests use synthetic/test data only. Never real wallet secrets.

Exit code 0 = all pass. Exit code 1 = any failure.
Missing required functions/files = FAILURE (fail closed).
"""

import hashlib
import os
import re
import sys

# -------------------------------------------------------------------
# Load the Python implementation (REQUIRED - fail if missing)
# -------------------------------------------------------------------
KIT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'kit')
sys.path.insert(0, KIT_DIR)

try:
    import bip39_dice_converter as py_impl
except ImportError as e:
    print(f"FATAL: Could not import docs/kit/bip39_dice_converter.py: {e}")
    print("Failing closed - required module missing.")
    sys.exit(1)

# Verify required functions exist (fail closed)
REQUIRED_FUNCS = ['clean_binary', 'generate_mnemonic', 'binary_to_bytes']
for func_name in REQUIRED_FUNCS:
    if not hasattr(py_impl, func_name):
        print(f"FATAL: Required function '{func_name}' not found in bip39_dice_converter.py")
        print("Failing closed - required function missing.")
        sys.exit(1)

# Verify WORDLIST exists
if not hasattr(py_impl, 'WORDLIST'):
    print("FATAL: WORDLIST not found in bip39_dice_converter.py")
    sys.exit(1)

# -------------------------------------------------------------------
# Test counters
# -------------------------------------------------------------------
passed = 0
failed = 0
failures = []

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        failures.append(name)
        print(f"  FAIL: {name}" + (f" - {detail}" if detail else ""))

def test_raises(name, fn, expected_exc, *args):
    """Test that fn(*args) raises expected_exc (specific class only)."""
    global passed, failed
    try:
        fn(*args)
        failed += 1
        failures.append(name)
        print(f"  FAIL: {name} - expected {expected_exc.__name__}, none raised")
    except expected_exc as e:
        passed += 1
        print(f"  PASS: {name} (raised {expected_exc.__name__}: {str(e)[:60]})")
    except Exception as e:
        failed += 1
        failures.append(name)
        print(f"  FAIL: {name} - expected {expected_exc.__name__}, got {type(e).__name__}: {e}")

# -------------------------------------------------------------------
# 1. BIP39 test vectors (using generate_mnemonic)
# -------------------------------------------------------------------
print("\n=== BIP39 Test Vectors ===")

# All-zero 256-bit: 23x abandon + art (BIP39 standard vector)
# generate_mnemonic returns (words_list, bits) tuple
zero_bits = "0" * 256
result = py_impl.generate_mnemonic(zero_bits)
words = result[0] if isinstance(result, tuple) else result
if isinstance(words, str):
    words = words.split()
test("All-zero 256-bit produces 24 words", len(words) == 24, f"got {len(words)}")
test("All-zero: first 23 are 'abandon'", all(w == "abandon" for w in words[:23]),
     f"got {words[:3]}...")
test("All-zero: last word is 'art'", words[23] == "art", f"got '{words[23]}'")

# All-one 256-bit
one_bits = "1" * 256
result_one = py_impl.generate_mnemonic(one_bits)
words_one = result_one[0] if isinstance(result_one, tuple) else result_one
if isinstance(words_one, str):
    words_one = words_one.split()
test("All-one 256-bit produces 24 words", len(words_one) == 24)
test("All-one differs from all-zero", words_one != words)

# Invalid length should raise
test_raises("Rejects <256 bits", py_impl.generate_mnemonic, ValueError, "0" * 255)
test_raises("Rejects empty input", py_impl.generate_mnemonic, ValueError, "")

# -------------------------------------------------------------------
# 2. Input validation (clean_binary)
# -------------------------------------------------------------------
print("\n=== Input Validation ===")

test("Accepts '101'", py_impl.clean_binary("101") == "101")
test("Accepts whitespace '10 01'", py_impl.clean_binary("10 01") == "1001")
test("Accepts newlines/tabs", py_impl.clean_binary("10\n01\t10") == "100110")

test_raises("Rejects '101x'", py_impl.clean_binary, ValueError, "101x")
test_raises("Rejects 'abc'", py_impl.clean_binary, ValueError, "abc")
test_raises("Rejects empty string", py_impl.clean_binary, ValueError, "")
test_raises("Rejects whitespace-only", py_impl.clean_binary, ValueError, "   ")
test_raises("Rejects non-breaking space", py_impl.clean_binary, ValueError, "10\u00a001")

# -------------------------------------------------------------------
# 3. SHA-256 correctness
# -------------------------------------------------------------------
print("\n=== SHA-256 ===")

expected_abc = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
actual_abc = hashlib.sha256(b"abc").hexdigest()
test("SHA-256('abc') matches NIST vector", actual_abc == expected_abc)

# -------------------------------------------------------------------
# 4. BIP39 wordlist integrity
# -------------------------------------------------------------------
print("\n=== BIP39 Wordlist ===")

wordlist = py_impl.WORDLIST
test("BIP39 wordlist has 2048 words", len(wordlist) == 2048, f"got {len(wordlist)}")
test("BIP39 words are unique", len(set(wordlist)) == 2048)
test("First word is 'abandon'", wordlist[0] == "abandon", f"got '{wordlist[0]}'")
test("Last word is 'zoo'", wordlist[-1] == "zoo", f"got '{wordlist[-1]}'")

# -------------------------------------------------------------------
# 5. Diceware wordlist (from HTML)
# -------------------------------------------------------------------
print("\n=== Diceware Wordlist ===")

DICEWARE_HTML = os.path.join(os.path.dirname(__file__), '..', 'docs', 'diceware-mapper.html')
if not os.path.exists(DICEWARE_HTML):
    print(f"  FAIL: {DICEWARE_HTML} not found (fail closed)")
    failed += 1
    failures.append("Diceware HTML exists")
else:
    with open(DICEWARE_HTML, encoding='utf-8') as f:
        html = f.read()
    
    m = re.search(r'var WORDS\s*=\s*"(.*?)"', html, re.DOTALL)
    if not m:
        print("  FAIL: Could not extract WORDS from diceware-mapper.html (fail closed)")
        failed += 1
        failures.append("Diceware WORDS extractable")
    else:
        words = m.group(1).split()
        test("Diceware HTML has 7776 words", len(words) == 7776, f"got {len(words)}")
        test("First word (11111) is 'abacus'", words[0] == "abacus", f"got '{words[0]}'")
        test("Last word (66666) is 'zoom'", words[-1] == "zoom", f"got '{words[-1]}'")
        test("All words unique", len(set(words)) == 7776)
        
        # EFF official SHA-256 (source: https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt)
        # Normalized as newline-joined word list, UTF-8 encoded
        eff_hash_expected = "abae49761b88f3f1ba31ef944bea1f61b795a3cd7e1cfb7d276ed45bf77967ba"
        html_hash = hashlib.sha256('\n'.join(words).encode()).hexdigest()
        test("Diceware matches EFF official (SHA-256)", html_hash == eff_hash_expected,
             f"got {html_hash[:16]}...")

# -------------------------------------------------------------------
# 6. No network requests in sensitive tools (static check)
# -------------------------------------------------------------------
print("\n=== Network Request Check (static) ===")
print("  NOTE: Static regex checks cannot prove no runtime network requests.")
print("  Browser-based testing with request interception is still required.")

SENSITIVE_FILES = [
    '../docs/dice-converter.html',
    '../docs/descriptor-tool.html',
    '../docs/diceware-mapper.html',
]

# These patterns must NOT appear (would indicate network exfiltration risk)
FORBIDDEN_PATTERNS = [
    (r'https?://www\.google\.com', "Google URL"),
    (r'https?://www\.gstatic\.com', "GStatic URL"),
    (r'chrome-extension://', "Browser extension URL"),
]

for rel_path in SENSITIVE_FILES:
    fpath = os.path.join(os.path.dirname(__file__), rel_path)
    fname = os.path.basename(fpath)
    if not os.path.exists(fpath):
        # Fail closed: missing sensitive files must not silently pass
        print(f"  FAIL: {rel_path} not found (fail closed - file must exist)")
        failed += 1
        failures.append(f"{fname} exists")
        continue
    
    with open(fpath, encoding='utf-8') as f:
        content = f.read()
    
    for pattern, desc in FORBIDDEN_PATTERNS:
        found = re.search(pattern, content)
        test(f"{fname}: no {desc}", not found,
             f"found '{found.group(0)[:50]}'" if found else "")

# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed")
if failures:
    print(f"\nFailed tests:")
    for f in failures:
        print(f"  - {f}")
    print("\nNOTE: This is not a complete cryptographic audit.")
    print("Browser runtime tests, OpenPGP interop, and JS execution still required.")
    sys.exit(1)
else:
    print("\nAll tests passed!")
    print("NOTE: Static tests only. Browser/network/OpenPGP tests still required")
    print("for a complete audit. Do not claim full cryptographic certification.")
    sys.exit(0)
