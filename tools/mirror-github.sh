#!/usr/bin/env bash
# mirror-github.sh — mirror this GitLab repository to GitHub.
#
# Skips silently when GITHUB_TOKEN or GITHUB_REPO is not configured, so the CI
# job stays green on a fresh fork that has no secrets yet.
#
# Usage:
#   GITHUB_TOKEN=... GITHUB_REPO=owner/repo tools/mirror-github.sh
set -euo pipefail

if [ -z "${GITHUB_TOKEN:-}" ] || [ -z "${GITHUB_REPO:-}" ]; then
  echo "GITHUB_TOKEN or GITHUB_REPO not set - skipping mirror"
  exit 0
fi

# x-access-token avoids embedding a username and works for fine-grained PATs.
REMOTE="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git"

echo "mirroring to ${GITHUB_REPO}"
git push --prune "$REMOTE" \
  "+refs/heads/*:refs/heads/*" \
  "+refs/tags/*:refs/tags/*"
echo "mirror complete"
