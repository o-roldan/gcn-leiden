#!/usr/bin/env bash
# Launch one GCE instance per dataset shard; each runs the full sweep for
# its dataset, uploads results to a GCS bucket, and self-deletes.
#
# Usage:
#   PROJECT=my-project BUCKET=gs://my-bucket REPO=https://github.com/<user>/gcn-leiden.git \
#     ./deploy/launch_shards.sh [shard ...]        # default: all shards
#
# Notes:
#   * GPU shards use the Deep Learning VM image so NVIDIA drivers install
#     automatically. Check quota: 4 concurrent L4 GPUs in the chosen zone.
#   * Monitor: gcloud compute ssh gcnl-<shard> -- tail -f /var/log/syslog
#   * Collect: gsutil ls $BUCKET/results/

set -euo pipefail
: "${PROJECT:?set PROJECT}" "${BUCKET:?set BUCKET}" "${REPO:?set REPO}"
ZONE=${ZONE:-us-central1-a}
SEEDS=${SEEDS:-0,1,2,3,4}

# shard -> "machine_type;gpu(0/1);datasets;eval_every"
declare -A SHARDS=(
  [cora]="e2-standard-8;0;cora;2"
  [citeseer]="e2-standard-8;0;citeseer;2"
  [amap]="e2-standard-8;0;amap;2"
  [film]="e2-standard-8;0;film;2"
  [wikics]="e2-standard-8;0;wikics;5"
  [sbm]="e2-standard-8;0;sbm_1000_5 sbm_5000_10 sbm_10000_20;5"
  [amac]="g2-standard-8;1;amac;5"
  [pubmed]="g2-standard-8;1;pubmed;10"
  [cocs]="g2-standard-8;1;cocs;10"
  [cophysics]="g2-standard-16;1;cophysics;10"
)

make_startup() {
  local datasets=$1 device=$2 eval_every=$3 shard=$4
  cat <<EOF
#!/bin/bash
set -x
export HOME=/root
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH=\$HOME/.local/bin:\$PATH
git clone ${REPO} /opt/gcn-leiden
cd /opt/gcn-leiden
uv sync
for DS in ${datasets}; do
  uv run python run_all.py --dataset \$DS --seeds ${SEEDS} \\
    --device ${device} --eval-every ${eval_every} || true
done
gsutil cp results/runs_*.csv ${BUCKET}/results/ || true
gsutil cp -r results/history_* ${BUCKET}/results/history/ || true
gcloud compute instances delete ${shard} --zone=${ZONE} --quiet
EOF
}

launch() {
  local shard=$1 spec=${SHARDS[$1]}
  IFS=';' read -r machine gpu datasets eval_every <<<"$spec"
  local name="gcnl-${shard}" device="cpu" image_flags

  if [[ $gpu == 1 ]]; then
    device="cuda"
    image_flags="--image-family=common-gpu-debian-11 \
      --image-project=deeplearning-platform-release \
      --maintenance-policy=TERMINATE \
      --metadata=install-nvidia-driver=True"
  else
    image_flags="--image-family=debian-12 --image-project=debian-cloud"
  fi

  echo ">>> launching $name ($machine, device=$device): $datasets"
  gcloud compute instances create "$name" \
    --project="$PROJECT" --zone="$ZONE" --machine-type="$machine" \
    $image_flags \
    --boot-disk-size=100GB \
    --scopes=storage-rw,compute-rw \
    --metadata-from-file=startup-script=<(make_startup "$datasets" "$device" "$eval_every" "$name")
}

shards=("$@")
[[ ${#shards[@]} -eq 0 ]] && shards=("${!SHARDS[@]}")
for shard in "${shards[@]}"; do
  launch "$shard"
done
echo "launched ${#shards[@]} shards; results will land in ${BUCKET}/results/"
