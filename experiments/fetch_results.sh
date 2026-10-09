#!/usr/bin/env bash
# Pull sweep results down from the GCS bucket the cloud shards uploaded to
# (see deploy/launch_shards.sh: each shard writes $BUCKET/results/<batch>/<shard>/).
# The bucket layout is mirrored under dest_dir; --no-clobber means files that
# already exist locally are never overwritten, so re-fetching is always safe.
#
# Usage:
#   BUCKET=gs://my-bucket ./experiments/fetch_results.sh [dest_dir]   # default dest: results
set -euo pipefail
: "${BUCKET:?set BUCKET, e.g. gs://my-bucket}"
DEST=${1:-results}
mkdir -p "$DEST"
gcloud storage rsync -r --no-clobber "${BUCKET}/results/" "$DEST/"
echo "synced ${BUCKET}/results/ -> $DEST/ (existing local files kept)"
