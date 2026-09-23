#!/usr/bin/env bash
# Usage: qa/run.sh fast|full   Exit: 0 all pass, 1 QA findings, 2 infrastructure error.
set -u
MODE="${1:-fast}"; cd "$(dirname "$0")/.."
export NODE_PATH="${NODE_PATH:-$(npm root -g)}" QA_BASE_URL="${QA_BASE_URL:-http://127.0.0.1:8102}"
PORT="${QA_BASE_URL##*:}"
[ -d qa/node_modules/axe-core ] || (cd qa && npm install --no-fund --no-audit) || exit 2
mkdir -p qa/out
python3 -m http.server "$PORT" -d docs >/dev/null 2>&1 & SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
for i in $(seq 1 30); do curl -fs "$QA_BASE_URL/" >/dev/null && break; sleep 0.3; done
curl -fs "$QA_BASE_URL/" >/dev/null || { echo "server did not start"; exit 2; }
rc=0
step() { "$@"; c=$?; [ $c -eq 2 ] && exit 2; [ $c -ne 0 ] && rc=1; return 0; }
case "$MODE" in
  fast) QA_WIDTHS=1440,390 QA_SCHEMES=light step node qa/matrix.cjs
        QA_WIDTHS=1440 QA_SCHEMES=light step node qa/a11y.cjs ;;
  full) step node qa/matrix.cjs; step node qa/a11y.cjs; step node qa/perf.cjs ;;
  *) echo "usage: $0 fast|full"; exit 2 ;;
esac
echo "qa $MODE exit=$rc (reports in qa/out/)"; exit $rc
