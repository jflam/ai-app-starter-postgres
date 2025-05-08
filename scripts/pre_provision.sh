#!/bin/bash
set -e

# Get the target region from environment variable
TARGET_REGION=${AZURE_DEPLOY_REGION:-$(azd env get AZURE_REGION 2>/dev/null || echo "")}

if [ -z "$TARGET_REGION" ]; then
    echo "Error: No target region specified. Please set AZURE_DEPLOY_REGION environment variable"
    echo "Example: export AZURE_DEPLOY_REGION=eastus2"
    exit 1
fi

# Run the Bicep config generator with the target region
python3 scripts/generate_bicep_config.py --region "$TARGET_REGION"

# Continue with normal azd deployment
exit 0