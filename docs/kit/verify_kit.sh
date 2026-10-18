#!/usr/bin/env bash

# Check if running inside a visible terminal window
if [ ! -t 0 ]; then
    # Force Tails OS to open a GNOME terminal to run the Python script
    gnome-terminal -- bash "$0" "$@"
    exit $?
fi

# Switch to the directory where this launcher file lives
cd "$(dirname "$0")"

# Audit the downloads. Dice entry stays python3 bip39_dice_converter.py with no flag.
python3 bip39_dice_converter.py --verify

# Keep window open for user evaluation
echo ""
read -p "Press [ENTER] to close this window..."
