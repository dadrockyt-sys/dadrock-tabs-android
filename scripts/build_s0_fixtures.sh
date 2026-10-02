#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "${ROOT}/astra_backend/evaluation/build_s0_synthetic_mixtures_v1.py"   --source-dir "${ROOT}/s0_sources"   --output-dir "${ROOT}/s0_generated"
echo "Generated S0 fixtures in ${ROOT}/s0_generated"
