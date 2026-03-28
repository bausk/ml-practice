#!/usr/bin/env bash
# Regenerate all lecture 8 images.
# Usage: ./generate_images.sh
set -euo pipefail
cd "$(dirname "$0")"
python3 generate_images.py
echo ""
echo "Images are in public/images/"
echo "Run 'npx slidev slides.md' to preview the presentation."
