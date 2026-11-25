#!/usr/bin/env python3
"""Worst Superpower entry: copy entry.txt to the output directory.

Stdlib only. Reads entry.txt sitting beside this script, validates it
(single line, 1-140 characters, not only whitespace), writes it to
$MAKEFUN_OUTPUT_DIR/entry.txt (default /output), then verifies with
SHA-256 that the output bytes are identical to the source bytes.
"""

import hashlib
import os
import sys

MAX_CHARS = 140


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, "entry.txt")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    output_path = os.path.join(output_dir, "entry.txt")

    with open(source_path, "rb") as f:
        data = f.read()

    text = data.decode("utf-8")
    if not text.strip():
        print("error: entry.txt is empty or only whitespace", file=sys.stderr)
        return 1
    if len(text) > MAX_CHARS:
        print(
            "error: entry.txt is %d characters, over the 140 limit" % len(text),
            file=sys.stderr,
        )
        return 1
    if "\n" in text or "\r" in text:
        print("error: entry.txt must be a single line", file=sys.stderr)
        return 1

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(data)

    with open(output_path, "rb") as f:
        written = f.read()

    # Extra check: the output file must be exactly as long as the source,
    # so a truncated or padded write cannot slip past the hash comparison.
    if len(written) != len(data):
        print(
            "error: size mismatch: source %d bytes != output %d bytes"
            % (len(data), len(written)),
            file=sys.stderr,
        )
        return 1

    source_hash = sha256_hex(data)
    written_hash = sha256_hex(written)
    if source_hash != written_hash:
        print(
            "error: SHA-256 mismatch: source %s != output %s"
            % (source_hash, written_hash),
            file=sys.stderr,
        )
        return 1

    print("wrote %s (%d chars, sha256 %s)" % (output_path, len(text), written_hash))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
