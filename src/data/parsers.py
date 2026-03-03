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


def parse_transaction_file(raw_path: str, N_max: int) -> list:
    """Flatten a transaction file into a single item stream.

    Each line is a space-separated sequence of integer item IDs representing
    one transaction.  All transactions are concatenated in order.  Truncation
    is applied after flattening: the stream is limited to the first N_max items.

    Parameters
    ----------
    raw_path:
        Absolute or project-relative path to the raw .dat file.  May be plain
        text or gzip-compressed.
    N_max:
        Maximum number of items to return.

    Returns
    -------
    list
        List of at most N_max integer item IDs.

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

    stream = []
    with _open_dat(raw_path) as fh:
        for line in fh:
            tokens = line.strip().split()
            for token in tokens:
                if not token:
                    continue
                stream.append(int(token))
                if len(stream) >= N_max:
                    return stream
    return stream


def parse_and_save(
    raw_path: str,
    output_path: str,
    N_max: int,
) -> list:
    """Parse a transaction file, truncate, and write processed stream to disk.

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
    list
        The parsed (and possibly truncated) stream of integer item IDs.
    """
    stream = parse_transaction_file(raw_path, N_max)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        for item in stream:
            fh.write(f"{item}\n")

    print(
        f"  Wrote {len(stream):,} items → {output_path}",
        file=sys.stderr,
    )
    return stream