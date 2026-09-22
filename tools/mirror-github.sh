#!/usr/bin/env bash
# mirror-github.sh — mirror this GitLab repository to GitHub.
#
# Two credential paths, tried in order:
#
#   1. GITHUB_DEPLOY_KEY_B64 — a base64-encoded SSH private key registered as a
#      WRITE deploy key on the GitHub repository. This is the narrow option: the
#      key can write to exactly one repository and nothing else. It is stored
#      base64-encoded because GitLab masked variables must be single-line.
#   2. GITHUB_TOKEN — a personal access token with "repo" scope.
#
# With neither configured the script prints a notice and exits 0, so the job
# stays green on a fork that has no secrets yet.
#
# Usage:
#   GITHUB_REPO=owner/repo GITHUB_DEPLOY_KEY_B64=... tools/mirror-github.sh
#   GITHUB_REPO=owner/repo GITHUB_TOKEN=...          tools/mirror-github.sh
set -euo pipefail

if [ -z "${GITHUB_REPO:-}" ]; then
  echo "GITHUB_REPO not set - skipping mirror"
  exit 0
fi

if [ -n "${GITHUB_DEPLOY_KEY_B64:-}" ]; then
  # --- SSH deploy key -------------------------------------------------------
  KEY_FILE="$(mktemp)"
  KNOWN_HOSTS="$(mktemp)"
  # shellcheck disable=SC2064
  trap "rm -f '$KEY_FILE' '$KNOWN_HOSTS'" EXIT

  printf '%s' "$GITHUB_DEPLOY_KEY_B64" | base64 -d > "$KEY_FILE"
  chmod 600 "$KEY_FILE"

  # Prefer GitHub's published host keys. Fall back to accept-new when the runner
  # cannot reach the metadata endpoint, so the job still works offline-ish.
  if curl -fsSL --max-time 15 https://api.github.com/meta 2>/dev/null \
       | python3 -c 'import json,sys; [print("github.com", k) for k in json.load(sys.stdin)["ssh_keys"]]' \
       > "$KNOWN_HOSTS" 2>/dev/null && [ -s "$KNOWN_HOSTS" ]; then
    echo "pinned GitHub host keys"
  else
    echo "note: could not pin GitHub host keys; using accept-new"
    : > "$KNOWN_HOSTS"
  fi

  export GIT_SSH_COMMAND="ssh -i $KEY_FILE -o IdentitiesOnly=yes -o UserKnownHostsFile=$KNOWN_HOSTS -o StrictHostKeyChecking=accept-new -o BatchMode=yes"

  REMOTE="git@github.com:${GITHUB_REPO}.git"
  echo "mirroring to ${GITHUB_REPO} over SSH (deploy key)"
  git push --prune "$REMOTE" \
    "+refs/heads/*:refs/heads/*" \
    "+refs/tags/*:refs/tags/*"
  echo "mirror complete"
  exit 0
fi

if [ -n "${GITHUB_TOKEN:-}" ]; then
  # --- personal access token ------------------------------------------------
  # x-access-token avoids embedding a username and works for fine-grained PATs.
  REMOTE="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git"
  echo "mirroring to ${GITHUB_REPO} over HTTPS (token)"
  git push --prune "$REMOTE" \
    "+refs/heads/*:refs/heads/*" \
    "+refs/tags/*:refs/tags/*"
  echo "mirror complete"
  exit 0
fi

echo "neither GITHUB_DEPLOY_KEY_B64 nor GITHUB_TOKEN is set - skipping mirror"
exit 0
