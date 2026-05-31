#!/usr/bin/env bash
# Verifies the mod-merging toolkit's dependencies in this (ephemeral) container.
# Runs on SessionStart; stdout becomes context the agent sees before the first turn.
echo "=== mod-merging toolkit: environment check ==="

if command -v python3 >/dev/null 2>&1; then
  echo "python3: OK ($(python3 --version 2>&1))"
else
  echo "python3: MISSING — conflict_scan.py / param_delta.py won't run"
fi

if command -v witchybnd >/dev/null 2>&1; then
  echo "witchybnd: OK"
else
  echo "witchybnd: not on PATH (Windows tool — run unpack/repack locally)"
fi

# Confirm the scripts themselves are present and parse cleanly.
for s in conflict_scan param_delta; do
  f="mod-merging-toolkit/scripts/${s}.py"
  if python3 -c "import ast,sys; ast.parse(open('$f').read())" 2>/dev/null; then
    echo "${s}.py: OK"
  else
    echo "${s}.py: NOT FOUND or syntax error"
  fi
done