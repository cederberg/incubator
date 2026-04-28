#!/usr/bin/env bash
# Shell script sample for the outline parser.

# Global variable - excluded from outline
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="1.0.0"

# Simple POSIX-style function
greet() {
    echo "Hello, ${1:-World}!"
}

# Bash keyword syntax without parens
function goodbye {
    echo "Goodbye!"
}

# Bash keyword syntax with parens
function say_hello() {
    local name="${1:-stranger}"
    echo "Hello, ${name}!"
}

# Function with complex body (for loop, if statement)
function process_files() {
    local dir="${1:-.}"
    local count=0
    for f in "${dir}"/*.txt ; do
        if [[ -f "$f" ]] ; then
            echo "Processing: $f"
            count=$((count + 1))
        fi
    done
    echo "Processed ${count} files"
}

# Private-style function
_internal_helper() {
    echo "helper: ${1}"
}

# Multi-line comment block
# spanning multiple lines
documented_function() {
    echo "documented"
}
