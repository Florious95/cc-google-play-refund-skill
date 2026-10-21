#!/usr/bin/env bash
# Rebuild the demo exhibit from scratch (fictional data only).
set -euo pipefail
cd "$(dirname "$0")"
S=../scripts
python3 make_sample.py
python3 "$S/grid.py" sample-inbox.png /tmp/sample-inbox.grid.png --step 50   # read coordinates
python3 "$S/redact.py" sample-inbox.png sample-inbox-redacted.png \
  --band 186,240 --band 354,408 --band 410,464 --band 522,576 --band-x 20,1260 --pad 0
python3 "$S/annotate.py" sample-inbox-redacted.png demo-exhibit.png --spec demo-spec.json
