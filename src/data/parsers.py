"""Dataset parsers for real-world datasets.

Parses raw transaction files (space-separated integers, one transaction per
line, optionally gzip-compressed) and flattens them into a single item stream.
Output is written to data/processed/<name>.txt, one integer item per line.

Supported datasets:
  - Kosarak (data/raw/kosarak.dat)
  - Retail  (data/raw/retail.dat)

Download source: http://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/
"""

import gzip
import os
import sys


def _open_dat(path: str):
    """Open a .dat file that may be plain text or gzip-compressed."""
    with open(path, "rb") as probe:
        magic = probe.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, "r", encoding="utf-8", errors="replace")


def _stream_from_file(path: str):
    """Generator — yields one integer item at a time from a processed file."""
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield int(line)


def parse_transaction_file(raw_path: str, N_max: int):
    """Generator — flattens a transaction file into a single item stream.

    Each line is a space-separated sequence of integer item IDs representing
    one transaction. All transactions are concatenated in order. Truncation
    is applied after flattening: yields at most N_max items.

    Parameters
    ----------
    raw_path:
        Absolute or project-relative path to the raw .dat file. May be plain
        text or gzip-compressed.
    N_max:
        Maximum number of items to yield.

    Raises
    ------
    FileNotFoundError
        If raw_path does not exist.
    ValueError
        If N_max is not positive.
    """
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw dataset file not found: {raw_path}")
    if N_max <= 0:
        raise ValueError(f"N_max must be positive, got {N_max}")
    count = 0
    with _open_dat(raw_path) as fh:
        for line in fh:
            for token in line.strip().split():
                if not token:
                    continue
                if count >= N_max:
                    return
                yield int(token)
                count += 1


def parse_and_save(raw_path: str, output_path: str, N_max: int):
    """Parse a transaction file, write processed stream to disk, return generator.

    Parameters
    ----------
    raw_path:
        Path to the raw .dat file.
    output_path:
        Path to write the processed stream (one item per line).
    N_max:
        Truncation limit.

    Returns
    -------
    generator
        Fresh generator over the written processed file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    count = 0
    with _open_dat(raw_path) as fh_in, open(output_path, "w", encoding="utf-8") as fh_out:
        for line in fh_in:
            for token in line.strip().split():
                if not token:
                    continue
                if count >= N_max:
                    break
                fh_out.write(f"{token}\n")
                count += 1

    print(
        f"  Wrote {count:,} items → {output_path}",
        file=sys.stderr,
    )
    return _stream_from_file(output_path)