#!/usr/bin/env bash
# Uploads a scan report to DefectDojo via the reimport-scan API.
#
# reimport-scan (with auto_create_context) creates the product/engagement/test
# on the first call and merges findings into the same test on every later
# call, so re-running CI against the "CI" engagement tracks new vs. resolved
# findings over time instead of piling up a fresh test per run.
#
# Requires DEFECTDOJO_URL and DEFECTDOJO_API_KEY in the environment. Skips
# (without failing the build) if they're unset, e.g. on PRs from forks that
# don't have access to repo secrets.
#
# Usage: defectdojo-upload.sh <scan_type> <file> <product_name> <test_title>
set -euo pipefail

scan_type="$1"
file="$2"
product_name="$3"
test_title="$4"

if [ -z "${DEFECTDOJO_URL:-}" ] || [ -z "${DEFECTDOJO_API_KEY:-}" ]; then
  echo "DEFECTDOJO_URL/DEFECTDOJO_API_KEY not set, skipping DefectDojo upload for '${test_title}'."
  exit 0
fi

if [ ! -f "$file" ]; then
  echo "Report file '${file}' not found, skipping DefectDojo upload for '${test_title}'."
  exit 0
fi

curl -sS --fail-with-body \
  "${DEFECTDOJO_URL%/}/api/v2/reimport-scan/" \
  -H "Authorization: Token ${DEFECTDOJO_API_KEY}" \
  -F "scan_type=${scan_type}" \
  -F "file=@${file}" \
  -F "product_type_name=${DEFECTDOJO_PRODUCT_TYPE:-Research and Development}" \
  -F "product_name=${product_name}" \
  -F "engagement_name=CI" \
  -F "test_title=${test_title}" \
  -F "auto_create_context=true" \
  -F "close_old_findings=true"
