# data/raw/ — Raw Dataset Files

This directory contains raw transaction datasets used in the experiment.
The files are **not committed to git** (see `.gitignore`) because they are
large and have stable, public download sources.

## Datasets

### Kosarak (`kosarak.dat`)

- **Source:** http://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/kosarak.dat
- **Format:** gzip-compressed plain text; one transaction per line;
  space-separated integer item IDs.
- **Description:** Click-stream data from a Hungarian online news portal.
  ~990 K transactions, ~41 K distinct items.
- **Download:**
  ```
  wget http://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/kosarak.dat \
       -O data/raw/kosarak.dat
  ```

### Retail (`retail.dat`)

- **Source:** http://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.dat
- **Format:** gzip-compressed plain text; one transaction per line;
  space-separated integer item IDs.
- **Description:** Market-basket data from a Belgian retail store.
  ~88 K transactions, ~17 K distinct items.
- **Download:**
  ```
  wget http://www.cs.rpi.edu/~zaki/Workshops/FIMI/data/retail.dat \
       -O data/raw/retail.dat
  ```

## Notes

- After downloading, place files at `data/raw/kosarak.dat` and
  `data/raw/retail.dat` relative to the project root.
- The parsers in `src/data/parsers.py` handle gzip decompression
  automatically.
- Processed streams (one integer item per line, truncated to N_max=1,000,000)
  are written to `data/processed/` and **are** committed to git.