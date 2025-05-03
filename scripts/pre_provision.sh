#!/bin/bash
set -e

# Run the Bicep config generator
python3 scripts/generate_bicep_config.py

# Continue with normal azd deployment
exit 0