#!/bin/bash
# Byte-compiles the application. One file is expected to fail and is asserted as
# such: menu_TUI.py has an unterminated triple-quoted block that swallows the rest
# of the file. It was handed in like that and is not patched, so the check states
# it instead of hiding it.
set -u

root="$(cd "$(dirname "$0")/.." && pwd)"
broken="src/publicaciones/menu_TUI.py"
failed=0

while IFS= read -r file; do
  rel="${file#"$root"/}"
  [ "$rel" = "$broken" ] && continue
  if python3 -m py_compile "$file" 2> /tmp/compile.err; then
    echo "ok    $rel"
  else
    echo "FAIL  $rel"
    sed 's/^/      /' /tmp/compile.err
    failed=1
  fi
done < <(find "$root/src" -name '*.py' | sort)

if python3 -m py_compile "$root/$broken" 2>/dev/null; then
  echo "FAIL  $broken now compiles; update the README"
  failed=1
else
  echo "known $broken does not compile, as documented"
fi

find "$root" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null

if [ "$failed" -ne 0 ]; then
  echo "some files did not compile"
  exit 1
fi
echo "all files compile, except the known one"
