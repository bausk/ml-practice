#!/usr/bin/env bash
# Re-generate all slide images from this directory
set -e
cd "$(dirname "$0")"
for f in gen_0*.py; do
  echo "Running $f..."
  python3 "$f"
done
echo "All images generated in ../img/"
