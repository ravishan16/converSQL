#!/usr/bin/env bash
# cleanup_unused_files.sh — safely remove deprecated/unused modules
# Usage:
#   bash scripts/cleanup_unused_files.sh           # Dry run (default)
#   bash scripts/cleanup_unused_files.sh --apply   # Actually delete
#
# What it does:
# - Checks a curated list of legacy/unnecessary files
# - Verifies they are not referenced in app/src/tests/conversql before deleting
# - Updates setup.cfg coverage omit list when files are removed
# - Uses git rm if the repo is tracked by git, else rm

# Be strict but avoid nounset (-u) to prevent failures on regex/expansions on some shells
set -Eeo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$ROOT_DIR"

APPLY=false
if [[ "${1:-}" == "--apply" ]]; then
  APPLY=true
fi

# Candidate files known to be legacy/unused in this repo
CANDIDATES=(
  "src/visualizations.py"      # legacy heavy UI (replaced by src/visualization.py)
  "src/ui/sidebar.py"          # legacy sidebar stub
  "src/auth_components.py"     # deprecated in favor of simple_auth_components
  "src/styles.py"              # unused CSS helper
  "src/auth_service.py"        # legacy duplicate of simple_auth; not imported
)

# Paths to scan for usages (exclude docs and setup files to avoid false positives)
SCAN_PATHS=("app.py" "src" "tests" "conversql")

# Choose sed in-place syntax for macOS vs GNU
SED_INPLACE=("-i")
if [[ "$(uname)" == "Darwin" ]]; then
  SED_INPLACE=("-i" "")
fi

has_git() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1
}

print_header() {
  echo "🧹 converSQL cleanup — $(date)"
  echo "Root: $ROOT_DIR"
  echo "Mode: $([[ "$APPLY" == true ]] && echo APPLY || echo DRY-RUN)"
  echo
}

check_usage() {
  local f="$1"
  local hits=0
  for p in "${SCAN_PATHS[@]}"; do
    if [[ -e "$p" ]]; then
      # search for filename (without leading src/) and import-style references
      local base
      base="$(basename "$f")"
      local name_no_ext
      name_no_ext="${base%.*}"
      # ripgrep if available for speed, else grep
      if command -v rg >/dev/null 2>&1; then
        # Count occurrences, excluding the file itself to avoid self-references
        local out c1 c2
  out=$(rg --no-heading --line-number --fixed-strings "${base}" "$p" --glob "!$f" 2>/dev/null || true)
  if [[ -z "$out" ]]; then c1=0; else c1=$(printf '%s' "$out" | wc -l | tr -d ' '); fi
  out=$(rg --no-heading --line-number --regexp "from +src\.[^ ]+ +import +${name_no_ext}|import +src\.[^.]+\.${name_no_ext}" "$p" --glob "!$f" 2>/dev/null || true)
  if [[ -z "$out" ]]; then c2=0; else c2=$(printf '%s' "$out" | wc -l | tr -d ' '); fi
        hits=$((hits + c1 + c2))
      else
        local out c1 c2
  out=$(grep -RIn --exclude="$f" -- "${base}" "$p" 2>/dev/null || true)
  if [[ -z "$out" ]]; then c1=0; else c1=$(printf '%s' "$out" | wc -l | tr -d ' '); fi
  out=$(grep -RInE --exclude="$f" -- "from +src\.[^ ]+ +import +${name_no_ext}|import +src\.[^.]+\.${name_no_ext}" "$p" 2>/dev/null || true)
  if [[ -z "$out" ]]; then c2=0; else c2=$(printf '%s' "$out" | wc -l | tr -d ' '); fi
        hits=$((hits + c1 + c2))
      fi
    fi
  done
  echo "$hits"
}

remove_from_setup_cfg() {
  local f="$1"
  local cfg="setup.cfg"
  if [[ -f "$cfg" ]]; then
    # Remove any line that references the file path
    if grep -q "$f" "$cfg"; then
      # Remove any line containing the literal path (escape safely for sed)
      esc_path=$(printf '%s' "$f" | sed 's/[.[\*^$]/\\&/g')
      sed "${SED_INPLACE[@]}" "/${esc_path}/d" "$cfg"
      echo "  ↳ updated setup.cfg omit list for $f"
    fi
  fi
}

delete_file() {
  local f="$1"
  if [[ ! -e "$f" ]]; then
    echo "  • $f (already removed)"
    return
  fi
  if [[ "$APPLY" == true ]]; then
    if has_git && git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
      git rm -q "$f"
    else
      rm -f "$f"
    fi
    echo "  ✔ removed $f"
    remove_from_setup_cfg "$f"
  else
    echo "  ◦ would remove $f"
  fi
}

main() {
  print_header
  local to_remove=()
  for f in "${CANDIDATES[@]}"; do
    if [[ -e "$f" ]]; then
      local hits
      hits=$(check_usage "$f")
      if [[ "$hits" -eq 0 ]]; then
        to_remove+=("$f")
      else
        echo "⚠️  Skipping $f — found $hits reference(s) in source/tests."
      fi
    fi
  done

  if [[ "${#to_remove[@]}" -eq 0 ]]; then
    echo "No safe deletions found."
    exit 0
  fi

  echo "Files deemed safe to remove:" 
  for f in "${to_remove[@]}"; do
    echo "  - $f"
  done
  echo

  for f in "${to_remove[@]}"; do
    delete_file "$f"
  done

  if [[ "$APPLY" == false ]]; then
    echo
    echo "Dry run complete. Re-run with --apply to perform deletions."
  fi
}

main "$@"
