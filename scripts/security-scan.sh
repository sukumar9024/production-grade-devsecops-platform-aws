#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports
TRIVY_IMAGE="${TRIVY_IMAGE:-aquasec/trivy:0.74.0}"
SEMGREP_IMAGE="${SEMGREP_IMAGE:-semgrep/semgrep:1.178.0}"
GITLEAKS_IMAGE="${GITLEAKS_IMAGE:-zricethezav/gitleaks:v8.30.1}"
mode="${1:?Usage: security-scan.sh sast|dependencies|iac|filesystem|history|images}"
case "$mode" in
  sast)
    docker run --rm -v "$PWD:/src" -w /src "$SEMGREP_IMAGE" semgrep scan --strict --config security/semgrep.yml --config p/python --config p/typescript --severity ERROR --error --metrics=off --json-output reports/semgrep.json backend/app frontend/src scripts
    ;;
  dependencies)
    backend/.venv/bin/pip-audit -r backend/requirements.txt --format json --output reports/pip-audit.json
    (cd frontend && npm audit --audit-level=high --json > ../reports/npm-audit.json)
    ;;
  iac)
    for target in bootstrap environments/dev environments/staging environments/prod; do
      terraform -chdir="infrastructure/terraform/$target" init -backend=false -input=false
      terraform -chdir="infrastructure/terraform/$target" validate
    done
    terraform -chdir=infrastructure/terraform fmt -check -recursive
    docker run --rm -v "$PWD:/src" -w /src "$TRIVY_IMAGE" config --severity HIGH,CRITICAL --exit-code 1 --format json --output reports/trivy-iac.json infrastructure/terraform
    ;;
  filesystem)
    docker run --rm -v "$PWD:/src" -w /src "$TRIVY_IMAGE" fs --scanners vuln,secret --skip-dirs .git,.tools,backend/.venv,frontend/node_modules,frontend/dist,reports --severity HIGH,CRITICAL --exit-code 1 --format json --output reports/trivy-filesystem.json .
    ;;
  history)
    docker run --rm -v "$PWD:/src" -w /src "$GITLEAKS_IMAGE" git --redact --report-format json --report-path reports/gitleaks.json .
    ;;
  images)
    status=0
    for component in backend frontend; do
      image="${IMAGE_PREFIX:-secureops}-$component:${IMAGE_TAG:?Set immutable Git SHA tag}"
      if ! docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v "$PWD/reports:/reports" "$TRIVY_IMAGE" image --scanners vuln,secret --severity HIGH,CRITICAL --exit-code 1 --format json --output "/reports/trivy-$component.json" "$image"; then
        status=1
      fi
    done
    exit "$status"
    ;;
  *) echo "Unknown scan mode" >&2; exit 2 ;;
esac
