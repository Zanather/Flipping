#!/usr/bin/env bash
# Verifies the mod-merging toolkit's dependencies in this (ephemeral) container.
# Runs on SessionStart; stdout becomes context the agent sees before the first turn.
echo "=== mod-merging toolkit: environment check ==="

if command -v python3 >/dev/null 2>&1; then
  has_python3=1
  echo "python3: OK ($(python3 --version 2>&1))"
else
  has_python3=0
  echo "python3: MISSING — conflict_scan.py / param_delta.py won't run"
fi

if command -v witchybnd >/dev/null 2>&1; then
  echo "witchybnd: OK"
else
  echo "witchybnd: not on PATH (Windows tool — run unpack/repack locally)"
fi

# Confirm the scripts themselves are present and parse cleanly (needs python3).
if [ "$has_python3" -eq 1 ]; then
  for s in conflict_scan param_delta; do
    f="mod-merging-toolkit/scripts/${s}.py"
    if python3 -c "import ast,sys; ast.parse(open('$f').read())" 2>/dev/null; then
      echo "${s}.py: OK"
    else
      echo "${s}.py: NOT FOUND or syntax error"
    fi
  done
else
  echo "scripts: skipped (python3 unavailable)"
fi