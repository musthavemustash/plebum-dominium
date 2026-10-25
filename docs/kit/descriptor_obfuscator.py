#!/usr/bin/env python3
import os
import subprocess
import sys

BANNER = """
====================================================================
           PLEBUM DOMINIUM · WALLET MAP ENCRYPTION TOOL
====================================================================
  AIRGAP NOTICE: Ensure this system is OFFLINE (Tails OS recommended).
  SECURITY NOTICE: The passphrase used here is NOT a seed phrase.
  DO NOT stamp this passphrase on metal plates.
====================================================================
"""

# Iterated-and-salted S2K, pinned so two Tails machines do not pick different
# settings. Count 65011712 is accepted by GnuPG 2.2 (the Tails series). Any
# explicit mode-3 count of 65536 or higher is acceptable; this is the one used.
S2K_COUNT = "65011712"


def check_gpg():
    try:
        subprocess.run(
            ["gpg", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def wipe(secret):
    """Best-effort. CPython strings are immutable, so only the bytearray is cleared."""
    if secret is None:
        return
    for i in range(len(secret)):
        secret[i] = 0


def gpg_run(args, payload, passphrase):
    read_fd, write_fd = os.pipe()
    try:
        os.write(write_fd, bytes(passphrase) + b"\n")
    finally:
        os.close(write_fd)
    try:
        proc = subprocess.Popen(
            ["gpg", *args, "--passphrase-fd", str(read_fd)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            pass_fds=(read_fd,),
        )
        stdout, stderr = proc.communicate(payload)
    finally:
        os.close(read_fd)
    return proc.returncode, stdout, stderr


def encrypt_descriptor(plaintext, passphrase):
    code, stdout, stderr = gpg_run(
        [
            "--symmetric",
            "--cipher-algo",
            "AES256",
            "--s2k-mode",
            "3",
            "--s2k-digest-algo",
            "SHA512",
            "--s2k-count",
            S2K_COUNT,
            "--armor",
            "--batch",
            "--pinentry-mode",
            "loopback",
        ],
        plaintext.encode("utf-8"),
        passphrase,
    )
    if code != 0:
        raise RuntimeError(f"GPG Encryption failed: {stderr.decode('utf-8', 'replace').strip()}")
    return stdout.decode("utf-8").strip()


def decrypt_descriptor(ciphertext, passphrase):
    code, stdout, _stderr = gpg_run(
        ["--decrypt", "--batch", "--pinentry-mode", "loopback"],
        ciphertext.encode("utf-8"),
        passphrase,
    )
    if code != 0:
        raise RuntimeError("GPG Decryption failed. Incorrect passphrase or corrupted data.")
    return stdout.decode("utf-8").strip()


def write_encrypted(text):
    name = input("\nOutput file [map.txt.gpg]: ").strip() or "map.txt.gpg"
    if os.path.exists(name):
        answer = input(f"{name} exists. Overwrite? [y/N]: ").strip().lower()
        if answer not in ("y", "yes"):
            print("[ERROR] Refused to overwrite.")
            sys.exit(1)
    with open(name, "w", encoding="utf-8") as handle:
        handle.write(text + "\n")
    print(f"\n[NOTICE] Encrypted wallet map written to {name}.")
    print("[NOTICE] Delete the plain map. Do not leave either file on an online machine.")


def main():
    print(BANNER)
    if not check_gpg():
        print("[ERROR] GPG (GnuPG) is not installed or not found in system PATH.")
        print("Please run this tool on Tails OS or install GPG.")
        sys.exit(1)

    print("Select Operation:")
    print("  [E]ncrypt Wallet Map (Obfuscate)")
    print("  [D]ecrypt Wallet Map (Restore)")
    print("  [Q]uit")
    choice = input("\nChoice (E/D/Q): ").strip().lower()

    if choice in ["q", "quit", "exit"]:
        sys.exit(0)

    if choice not in ["e", "d", "encrypt", "decrypt"]:
        print("[ERROR] Invalid choice.")
        sys.exit(1)

    is_decrypt = choice in ["d", "decrypt"]

    if is_decrypt:
        print("\nPaste the encrypted descriptor string (armored GPG text, through the END line):")
        lines = []
        while True:
            line = input()
            lines.append(line)
            if line.strip() == "-----END PGP MESSAGE-----":
                break
        target_data = "\n".join(lines).strip()
    else:
        target_data = input("\nEnter raw wallet descriptor: ").strip()

    entered = input("Enter secret map passphrase (shows on screen): ").strip()
    if not target_data or not entered:
        print("[ERROR] Input data and passphrase cannot be empty.")
        sys.exit(1)

    passphrase = bytearray(entered.encode("utf-8"))
    try:
        if is_decrypt:
            result = decrypt_descriptor(target_data, passphrase)
            print("\n" + "=" * 50)
            print(">>> RESTORED WALLET DESCRIPTOR:")
            print("=" * 50)
            print(result)
            print("=" * 50)
            print("\n[NOTICE] Clear this terminal when finished. Type: reset")
            print("[NOTICE] Scrollback keeps the restored map until the terminal is cleared.")
        else:
            result = encrypt_descriptor(target_data, passphrase)
            write_encrypted(result)
    except Exception as exc:
        print(f"\n[ERROR] Operation failed: {exc}")
    finally:
        wipe(passphrase)

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
