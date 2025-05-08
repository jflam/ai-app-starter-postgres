#!/usr/bin/env python3
import json
import sys
import argparse
from typing import Dict, Any
from pathlib import Path

# Define supported regions for each service type
SERVICE_REGIONS = {
    "Microsoft.Web/staticSites": [
        "westus2",
        "centralus",
        "eastus2",
        "westeurope",
        "eastasia"
    ],
    # Add other service types as needed
}

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Generate Bicep configuration")
    parser.add_argument("--region", required=True, help="Target Azure region for deployment")
    return parser.parse_args()

def load_config() -> Dict[str, Any]:
    """Load the azure-config.json file"""
    config_path = Path("infra/azure-config.json")
    if not config_path.exists():
        print("Error: azure-config.json not found")
        sys.exit(1)
    
    with open(config_path) as f:
        config = json.load(f)
    return config

def validate_region(config: Dict[str, Any], region: str):
    """Validate that the specified region is allowed and supported by all services"""
    # First check if it's in our allowed regions
    if region not in config["allowed_regions"]:
        print(f"Error: Region '{region}' is not in the allowed regions list:")
        print("Allowed regions:", ", ".join(config["allowed_regions"]))
        sys.exit(1)
    
    # Then check each service's supported regions
    unsupported_services = []
    for service_type, supported_regions in SERVICE_REGIONS.items():
        if region not in supported_regions:
            unsupported_services.append(service_type)
    
    if unsupported_services:
        print(f"\nError: Region '{region}' is not supported by all required services:")
        for service in unsupported_services:
            print(f"\n{service}:")
            print("Supported regions:", ", ".join(SERVICE_REGIONS[service]))
        sys.exit(1)

def generate_bicep_params(config: Dict[str, Any], region: str) -> Dict[str, Any]:
    """Generate Bicep parameters from config"""
    params = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "location": {
                "value": region
            },
            "postgresAdminUser": {
                "value": config["database"]["admin_user"]
            },
            # Note: Password should be set via environment variable
            "postgresAdminPassword": {
                "reference": {
                    "keyVault": {
                        "id": "[parameters('keyVaultId')]"
                    },
                    "secretName": "postgresAdminPassword"
                }
            },
            "postgresDbName": {
                "value": config["database"]["name"]
            },
            "postgresSku": {
                "value": config["required_services"]["postgresql"]["sku"]
            },
            "postgresStorage": {
                "value": {
                    "storageSizeGB": config["required_services"]["postgresql"]["storage_gb"]
                }
            },
            "containerAppsCpu": {
                "value": config["required_services"]["container_apps"]["resources"]["cpu"]
            },
            "containerAppsMemory": {
                "value": config["required_services"]["container_apps"]["resources"]["memory"]
            },
            "tags": {
                "value": config["deployment"]["tags"]
            }
        }
    }
    return params

def update_bicep_template(config: Dict[str, Any], region: str):
    """Update the Bicep template with configuration-driven changes"""
    bicep_path = Path("infra/main.bicep")
    if not bicep_path.exists():
        print("Error: main.bicep not found")
        sys.exit(1)
    
    # Read current template
    with open(bicep_path) as f:
        template = f.read()
    
    # Update parameters section
    params_section = """
param location string
param postgresAdminUser string
@secure()
param postgresAdminPassword string
param postgresDbName string = 'ai_app'
param postgresSku object
param postgresStorage object
param containerAppsCpu string
param containerAppsMemory string
param tags object = {}
"""
    
    # Find the parameters section and replace it
    # This is a simple example - you might need more sophisticated parsing
    if "param location" in template:
        # Replace the parameters section
        template = template.replace(
            "param location string = resourceGroup().location",
            params_section.strip()
        )
    
    # Update the PostgreSQL server resource
    pg_server_section = f"""
resource pgServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {{
  name: uniqueString(resourceGroup().id, 'pg')
  location: location
  tags: tags
  properties: {{
    version: '{config["required_services"]["postgresql"]["version"]}'
    administratorLogin: postgresAdminUser
    administratorLoginPassword: postgresAdminPassword
    storage: postgresStorage
    createMode: 'Create'
    availabilityZone: '1'
    backup: {{
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }}
  }}
  sku: postgresSku
}}
"""
    
    # Find and replace the PostgreSQL server resource
    if "resource pgServer" in template:
        import re
        template = re.sub(
            r"resource pgServer.*?}}",
            pg_server_section.strip(),
            template,
            flags=re.DOTALL
        )
    
    # Write updated template
    with open(bicep_path, "w") as f:
        f.write(template)

def main():
    """Main entry point"""
    args = parse_args()
    config = load_config()
    
    # Validate the target region
    validate_region(config, args.region)
    
    # Generate parameters file
    params = generate_bicep_params(config, args.region)
    with open("infra/main.parameters.json", "w") as f:
        json.dump(params, f, indent=2)
    
    # Update Bicep template
    update_bicep_template(config, args.region)
    
    print(f"Successfully updated Bicep configuration for region: {args.region}")

if __name__ == "__main__":
    main()