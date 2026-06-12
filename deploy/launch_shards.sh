#!/usr/bin/env bash
# Launch one GCE instance per dataset shard; each runs the full sweep for
# its dataset, uploads results to a GCS bucket, and self-deletes.
#
# Usage:
#   PROJECT=my-project BUCKET=gs://my-bucket REPO=https://github.com/<user>/gcn-leiden.git \
#     ./deploy/launch_shards.sh [shard ...]        # default: all of ALL_SHARDS
#
# Notes:
#   * CPU shards use n2-standard-8 (E2 quota is 24 vCPUs on fresh projects;
#     N2 quota is 200, so six shards fit concurrently).
#   * The default "gpu" shard runs all four GPU datasets sequentially on ONE
#     g2-standard-16 (regional NVIDIA_L4_GPUS quota is 1 on fresh projects).
#     With quota >= 4, launch the split shards instead:
#       ./deploy/launch_shards.sh amac pubmed cocs cophysics
#   * GPU shards use the Deep Learning VM image so NVIDIA drivers install
#     automatically.
#   * Monitor: gcloud compute instances get-serial-port-output gcnl-<shard> --zone=$ZONE
#   * Collect: gcloud storage ls $BUCKET/results/
#
# Compatible with macOS bash 3.2 (no associative arrays).

set -euo pipefail
: "${PROJECT:?set PROJECT}" "${BUCKET:?set BUCKET}" "${REPO:?set REPO}"
ZONE=${ZONE:-us-central1-a}
SEEDS=${SEEDS:-0,1,2,3,4}
# CPU machine type; override when a zone runs out of stock
# (quota note: N2_CPUS=200, C2D_CPUS=100, E2_CPUS=24 on this project)
CPU_MACHINE=${CPU_MACHINE:-n2-standard-8}

ALL_SHARDS="cora citeseer amap film wikics sbm gpu"

# shard -> "machine_type;gpu(0/1);driver;dataset:eval_every ..."
spec_for() {
  case $1 in
    cora)      echo "${CPU_MACHINE};0;run_all.py;cora:2" ;;
    citeseer)  echo "${CPU_MACHINE};0;run_all.py;citeseer:2" ;;
    amap)      echo "${CPU_MACHINE};0;run_all.py;amap:2" ;;
    film)      echo "${CPU_MACHINE};0;run_all.py;film:2" ;;
    wikics)    echo "${CPU_MACHINE};0;run_all.py;wikics:5" ;;
    sbm)       echo "${CPU_MACHINE};0;run_all.py;sbm_1000_5:5 sbm_5000_10:5 sbm_10000_20:5" ;;
    # single-GPU shard: all CUDA datasets sequentially on one L4
    gpu)       echo "g2-standard-16;1;run_all.py;amac:5 pubmed:10 cocs:10 cophysics:10" ;;
    # split GPU shards: need GPUS_ALL_REGIONS + regional L4 quota >= 4
    amac)      echo "g2-standard-8;1;run_all.py;amac:5" ;;
    pubmed)    echo "g2-standard-8;1;run_all.py;pubmed:10" ;;
    cocs)      echo "g2-standard-8;1;run_all.py;cocs:10" ;;
    cophysics) echo "g2-standard-16;1;run_all.py;cophysics:10" ;;
    # recalibration sweep (Objetivo 2): beta x gamma grid via run_recal.py
    recal-cite)  echo "${CPU_MACHINE};0;run_recal.py;cora:2 citeseer:2" ;;
    recal-film)  echo "${CPU_MACHINE};0;run_recal.py;film:2" ;;
    recal-sbm1k) echo "${CPU_MACHINE};0;run_recal.py;sbm_1000_5:5" ;;
    recal-sbm5k) echo "${CPU_MACHINE};0;run_recal.py;sbm_5000_10:5" ;;
    recal-sbm10k) echo "${CPU_MACHINE};0;run_recal.py;sbm_10000_20:10" ;;
    *)         return 1 ;;
  esac
}

make_startup() {
  local datasets=$1 device=$2 shard=$3 driver=$4
  cat <<EOF
#!/bin/bash
set -x
export HOME=/root
for attempt in 1 2 3; do
  apt-get update -qq && apt-get install -y -qq git curl && break
  sleep 20
done
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH=\$HOME/.local/bin:\$PATH
git clone ${REPO} /opt/gcn-leiden
cd /opt/gcn-leiden
uv sync
for PAIR in ${datasets}; do
  DS=\${PAIR%%:*}; EV=\${PAIR##*:}
  uv run python ${driver} --dataset \$DS --seeds ${SEEDS} \\
    --device ${device} --eval-every \$EV || true
done
gsutil cp results/runs_*.csv ${BUCKET}/results/ || true
gsutil cp -r results/history_* ${BUCKET}/results/history/ || true
gcloud compute instances delete ${shard} --zone=${ZONE} --quiet
EOF
}

launch() {
  local shard=$1 spec
  spec=$(spec_for "$shard") || { echo "unknown shard: $shard" >&2; exit 1; }
  IFS=';' read -r machine gpu driver datasets <<<"$spec"
  local name="gcnl-${shard}" device="cpu" image_flags

  if [[ $gpu == 1 ]]; then
    device="cuda"
    image_flags="--image-family=common-cu129-ubuntu-2204-nvidia-580 \
      --image-project=deeplearning-platform-release \
      --maintenance-policy=TERMINATE"
  else
    image_flags="--image-family=debian-12 --image-project=debian-cloud"
  fi

  echo ">>> launching $name ($machine, device=$device): $datasets"
  gcloud compute instances create "$name" \
    --project="$PROJECT" --zone="$ZONE" --machine-type="$machine" \
    $image_flags \
    --boot-disk-size=100GB \
    --scopes=storage-rw,compute-rw \
    --metadata-from-file=startup-script=<(make_startup "$datasets" "$device" "$name" "$driver")
}

shards=("$@")
[[ ${#shards[@]} -eq 0 ]] && shards=($ALL_SHARDS)
for shard in "${shards[@]}"; do
  launch "$shard"
done
echo "launched ${#shards[@]} shards; results will land in ${BUCKET}/results/"
