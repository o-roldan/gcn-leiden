#!/usr/bin/env bash
# Pull sweep results down from the GCS bucket the cloud shards uploaded to
# (see deploy/launch_shards.sh, which runs `gsutil cp ... ${BUCKET}/results/`).
#
# Usage:
#   BUCKET=gs://my-bucket ./experiments/fetch_results.sh [dest_dir]   # default dest: results
set -euo pipefail
: "${BUCKET:?set BUCKET, e.g. gs://my-bucket}"
DEST=${1:-results}
mkdir -p "$DEST"
gsutil -m rsync -r "${BUCKET}/results/" "$DEST/"
echo "synced ${BUCKET}/results/ -> $DEST/"
