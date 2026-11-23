#!/bin/sh
# One command: check the keystone model on every config and compare each result
# with what it should be.
#
#   sh formal/keystone/run.sh
#
# Needs Java 11 or later and curl. Downloads TLC 1.7.4 (the version pstack's
# /statechart pins) once, checks its sha256, and caches it in
# formal/keystone/.tools/ (git-ignored).
#
# Exit 0 only when every config ends as expected: the pass configs pass, and
# every finding and every break fails on the expected rule by the expected path.
# A break that stops failing means the check lost its ability to fail.
set -eu

here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../.." && pwd)
tools="$here/.tools"
jar="$tools/tla2tools-1.7.4.jar"
sum="936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88"
url="https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar"

mkdir -p "$tools"
if [ ! -f "$jar" ]; then
  curl -sSfL -o "$jar.part" "$url"
  mv "$jar.part" "$jar"
fi
have=$(sha256sum "$jar" | cut -d' ' -f1)
if [ "$have" != "$sum" ]; then
  echo "tla2tools.jar checksum mismatch: $have" >&2
  exit 2
fi

# --- What this run covers ------------------------------------------------
# The model's guards stand for checks in these files. If any changed since the
# sync commit, the model may describe code that is gone: read the changes
# (see .claude/skills/verify-keystone-model/SKILL.md) before trusting a pass.
sync=$(sed -n 's/^sync-commit: *//p' "$here/COVERAGE")
covered=$(sed -n 's/^  - //p' "$here/COVERAGE")
head=$(git -C "$repo" rev-parse HEAD 2>/dev/null || echo unknown)
echo "commit:      $head"
echo "sync commit: $sync"
echo "covers:"
for f in $covered; do echo "  $f"; done
drift=""
if git -C "$repo" cat-file -e "$sync^{commit}" 2>/dev/null; then
  # shellcheck disable=SC2086
  drift=$(git -C "$repo" diff --name-only "$sync" HEAD -- $covered)
else
  drift="(sync commit not in this clone; fetch more history to compare)"
fi
if [ -n "$drift" ]; then
  echo "covered files changed since the sync commit:"
  echo "$drift" | sed 's/^/  /'
fi
echo

# --- Run every config ----------------------------------------------------
# config | expected: pass, or the rule that must break | the moves TLC must
# report on the shortest path (action names, in order)
cases='
pass-branch-b|pass|
pass-branch-a|pass|
limit-stock-sale|NoExcessHolding|GiftStock PlanDateHits PeriodEnds
break-typed-screen|Keystone|Gift Buy
break-undated-plan|AlarmBeforeBreach|GiftStock PeriodEnds
break-lease|Keystone|Gift BuyEquipment LeaseEquipment
break-excess|Keystone|Gift WriteRecord Wage
break-er|NoTaxableGrant|Gift Grant
break-er-keystone|Keystone|Gift Grant GranteeSpends
'
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp "$here/Keystone.tla" "$work/"
bad=0
echo "$cases" | while IFS='|' read -r name want path; do
  [ -n "$name" ] || continue
  out="$work/$name.out"
  (cd "$work" && java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -workers 1 \
     -config "$here/configs/$name.cfg" -metadir "$work/meta-$name" Keystone.tla) \
     >"$out" 2>&1 || true
  if grep -q "Model checking completed. No error has been found." "$out"; then
    got=pass
    gotpath=""
  else
    got=$(sed -n 's/^Error: Invariant \([A-Za-z0-9]*\) is violated.*/\1/p' "$out" | head -1)
    [ -n "$got" ] || got="error"
    gotpath=$(sed -n 's/^State [0-9]*: <\([A-Za-z]*\).*/\1/p' "$out" | grep -v '^Initial$' | tr '\n' ' ' | sed 's/ $//')
  fi
  states=$(sed -n 's/.* \([0-9][0-9,]*\) distinct states found.*/\1/p' "$out" | tail -1)
  if [ "$got" = "$want" ] && [ "$gotpath" = "$path" ]; then
    verdict=ok
  else
    verdict=UNEXPECTED
    echo 1 > "$work/bad"
  fi
  printf '%-22s expected %-16s got %-16s %s states  %s\n' "$name" "$want" "$got" "${states:-?}" "$verdict"
  if [ "$got" != pass ]; then
    printf '    path: %s\n' "$gotpath"
  fi
  if [ "$verdict" = UNEXPECTED ]; then
    echo "    expected path: ${path:-none}"
    tail -30 "$out" | sed 's/^/    | /'
  fi
done
if [ -f "$work/bad" ]; then
  echo
  echo "Some configs did not end as expected. Read the path above before changing anything:"
  echo "a step the code cannot take is a model error; otherwise it is a finding."
  exit 1
fi
echo
echo "All configs ended as expected."
