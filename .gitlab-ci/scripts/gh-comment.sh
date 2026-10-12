#!/bin/bash
set -euo pipefail

TOKEN="${TOKEN:?TOKEN is required}"
REPO="${REPO:?REPO is required (owner/repo)}"
PR_NUMBER="${PR_NUMBER:?PR_NUMBER is required}"
API="https://api.github.com/repos/$REPO/issues/$PR_NUMBER"

main() {
  COMMENT="Test run finished.\n\nArtifacts: ${CI_JOB_URL:+$CI_JOB_URL/artifacts/browse/results/}"

  echo "Pull Request is open. Posting comment..."
  curl -sS -L --fail \
    -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "${API}/comments" \
    -d "{\"body\":\"$COMMENT\"}"
}

main "$@"
