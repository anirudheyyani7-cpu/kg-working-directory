#!/bin/bash
set -e
cd "$(dirname "$0")/../backend"
echo "Running TMT Knowledge Graph seed..."
python -m app.seed.seed_runner
echo "Done."
