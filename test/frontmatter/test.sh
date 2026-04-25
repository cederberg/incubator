#!/usr/bin/env bash
# Test suite for bin/frontmatter

set -euo pipefail

FIXTURES="$(cd "$(dirname "$0")" && pwd)/fixtures"
FRONTMATTER="$(cd "$(dirname "$0")/../../bin" && pwd)/frontmatter"

GREEN=$(tput setaf 2 2>/dev/null || echo '')
RED=$(tput setaf 1 2>/dev/null || echo '')
NC=$(tput sgr0 2>/dev/null || echo '')

pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Test 1: Single file with front-matter
output=$("$FRONTMATTER" "$FIXTURES/valid.md")
expected="title: Valid File
author: Test"
if [[ "$output" == "$expected" ]] ; then
    pass "Single file with front-matter"
else
    fail "Single file with front-matter: got '$output', expected '$expected'"
fi

# Test 2: Single file without front-matter (should warn to stderr)
output=$("$FRONTMATTER" "$FIXTURES/no-fm.md" 2>&1 || true)
if [[ "$output" == *"warning: no front-matter found in: $FIXTURES/no-fm.md"* ]] ; then
    pass "Single file without front-matter warns"
else
    fail "Single file without front-matter: got '$output'"
fi

# Test 3: Single file with empty front-matter
output=$("${FRONTMATTER:-bin/frontmatter}" "$FIXTURES/empty-fm.md")
# Empty front-matter should output nothing between the --- delimiters
if [[ -z "$output" ]] ; then
    pass "Single file with empty front-matter"
else
    fail "Single file with empty front-matter: got '$output'"
fi

# Test 4: Directory with valid files
output=$("${FRONTMATTER:-bin/frontmatter}" "$FIXTURES" 2>&1)
if [[ "$output" == *"valid.md"* ]] && [[ "$output" == *"valid.txt"* ]] && [[ "$output" == *"nested.md"* ]] ; then
    pass "Directory finds nested files with front-matter"
else
    fail "Directory search: got '$output'"
fi

# Test 5: Non-existent path (should warn)
output=$("$FRONTMATTER" /tmp/nonexistent_dir_12345 2>&1 || true)
if [[ "$output" == *"warning: not a file or directory: /tmp/nonexistent_dir_12345"* ]] ; then
    pass "Non-existent path warns"
else
    fail "Non-existent path: got '$output'"
fi

# Test 5b: Directory with no matching files (should warn)
output=$("$FRONTMATTER" "$FIXTURES/empty_dir" 2>&1 || true)
if [[ "$output" == *"warning: no front-matter files found in: $FIXTURES/empty_dir"* ]] ; then
    pass "Empty directory warns"
else
    fail "Empty directory: got '$output'"
fi

# Test 5c: Binary file (should warn or be ignored)
output=$("$FRONTMATTER" "$FIXTURES/binary.bin" 2>&1 || true)
if [[ "$output" == *"warning: no front-matter found in: $FIXTURES/binary.bin"* ]] ; then
    pass "Binary file warns"
else
    fail "Binary file: got '$output'"
fi

# Test 6: Multiple files
output=$("${FRONTMATTER:-bin/frontmatter}" "$FIXTURES/valid.md" "$FIXTURES/valid.txt" 2>&1)
if [[ "$output" == *"valid.md"* ]] && [[ "$output" == *"valid.txt"* ]] ; then
    pass "Multiple files mode"
else
    fail "Multiple files: got '$output'"
fi

# Test 7: Directory with subdirectory
output=$("${FRONTMATTER:-bin/frontmatter}" "$FIXTURES" 2>&1)
if [[ "$output" == *"subdir/nested.md"* ]] ; then
    pass "Recursive directory search"
else
    fail "Recursive search: got '$output'"
fi

# Test 8: Non-matching file in directory (should be silently ignored)
output=$("${FRONTMATTER:-bin/frontmatter}" "$FIXTURES" 2>&1)
if [[ "$output" != *"no-fm.md"* ]] ; then
    pass "Non-matching files in directory are silently ignored"
else
    fail "Non-matching files: should be ignored but got '$output'"
fi

# Test 9: Help output
output=$("$FRONTMATTER" -h 2>&1 || true)
if [[ "$output" == *"Prints the front-matter block"* ]] ; then
    pass "Help flag works"
else
    fail "Help flag: got '$output'"
fi

# Test 10: No arguments
output=$("$FRONTMATTER" 2>&1 || true)
if [[ "$output" == *"Prints the front-matter block"* ]] ; then
    pass "No arguments shows usage"
else
    fail "No arguments: got '$output'"
fi

echo -e "\n${GREEN}All tests passed!${NC}"
