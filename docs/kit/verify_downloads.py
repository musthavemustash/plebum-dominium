#!/usr/bin/env python3
"""Run the hash audit inside bip39_dice_converter.py. Stdlib only."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bip39_dice_converter import clean_filename, verify_kit_integrity

target = sys.argv[1] if len(sys.argv) > 1 else "."
verify_kit_integrity(clean_filename(target))
