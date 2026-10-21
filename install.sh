#!/usr/bin/env bash
# Install the google-play-refund skill for coding agents.
#
#   ./install.sh --project          ./.agents/skills/google-play-refund   (Codex, Cursor, GitHub Copilot, Gemini CLI ... in this repo)
#   ./install.sh --global           ~/.agents/skills/google-play-refund   (Codex, Cursor: all projects on this machine)
#   ./install.sh --claude           ~/.claude/skills/google-play-refund   (Claude Code personal; Cursor also reads it)
#   ./install.sh --claude --project ./.claude/skills/google-play-refund   (Claude Code, this project only)
#   ./install.sh --dir PATH         PATH/google-play-refund               (any other skills directory)
#
# Several targets can be combined, e.g. --global --claude.
# Remote one-liner:
#   curl -fsSL https://raw.githubusercontent.com/Florious95/google-play-refund-skill/main/install.sh | bash -s -- --claude
set -euo pipefail

NAME="google-play-refund"
REPO_URL="${GPRS_REPO_URL:-https://github.com/Florious95/google-play-refund-skill.git}"
FILES=(SKILL.md scripts examples)

usage() {
  cat <<'USAGE'
Usage: install.sh [--project] [--global] [--claude] [--dir PATH] [--force]
  --project           ./.agents/skills/google-play-refund  (Codex, Cursor, Copilot, Gemini CLI ...)
  --global            ~/.agents/skills/google-play-refund  (Codex, Cursor; every project)
  --claude            ~/.claude/skills/google-play-refund  (Claude Code personal; Cursor reads it too)
  --claude --project  ./.claude/skills/google-play-refund  (Claude Code, this project)
  --dir PATH          PATH/google-play-refund
  --force             replace an existing install
USAGE
  exit "${1:-0}"
}

project=0; global=0; claude=0; force=0; dirs=()
while [ $# -gt 0 ]; do
  case "$1" in
    --project) project=1 ;;
    --global)  global=1 ;;
    --claude)  claude=1 ;;
    --dir)     shift; [ $# -gt 0 ] || usage 1; dirs+=("$1") ;;
    --force|-f) force=1 ;;
    -h|--help) usage 0 ;;
    *) echo "unknown option: $1" >&2; usage 1 ;;
  esac
  shift
done

targets=()
if [ $claude -eq 1 ]; then
  if [ $project -eq 1 ]; then targets+=("$PWD/.claude/skills"); else targets+=("$HOME/.claude/skills"); fi
  [ $global -eq 1 ] && targets+=("$HOME/.agents/skills")
else
  [ $project -eq 1 ] && targets+=("$PWD/.agents/skills")
  [ $global -eq 1 ] && targets+=("$HOME/.agents/skills")
fi
for d in "${dirs[@]+"${dirs[@]}"}"; do targets+=("$d"); done
[ ${#targets[@]} -gt 0 ] || { echo "choose at least one of --project, --global, --claude, --dir" >&2; usage 1; }

# Source: the directory this script lives in, or a fresh shallow clone.
src=""
here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -n "$here" ] && grep -q "^name: $NAME\$" "$here/SKILL.md" 2>/dev/null; then
  src="$here"
else
  command -v git >/dev/null || { echo "git is required for a remote install" >&2; exit 1; }
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  git clone --depth 1 --quiet "$REPO_URL" "$tmp/repo"
  src="$tmp/repo"
fi

for base in "${targets[@]}"; do
  dest="$base/$NAME"
  if [ -e "$dest" ]; then
    if [ $force -eq 1 ]; then rm -rf "$dest"; else
      echo "exists: $dest (use --force to replace)" >&2; continue; fi
  fi
  mkdir -p "$dest"
  for f in "${FILES[@]}"; do cp -R "$src/$f" "$dest/"; done
  chmod +x "$dest"/scripts/*.py 2>/dev/null || true
  echo "installed: $dest"
done

python3 -c "import PIL" 2>/dev/null || echo "note: Pillow not found; run: python3 -m pip install --user Pillow"
