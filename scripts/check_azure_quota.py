#!/usr/bin/env python3
import os
import json
import sys
from typing import Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import aiohttp
from rich.console import Console
from rich.table import Table
from rich import print as rprint

app = FastAPI()
console = Console()

class QuotaCheck(BaseModel):
    region: str
    current_value: int
    limit: int
    available: int

class RegionQuota(BaseModel):
    region: str
    quotas: Dict[str, QuotaCheck]
    has_sufficient_quota: bool

async def get_azure_token() -> Optional[str]:
    """Get Azure access token using Azure CLI"""
    try:
        import subprocess
        result = subprocess.run(
            ['az', 'account', 'get-access-token', '--query', 'accessToken', '-o', 'tsv'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        console.print(f"[red]Error getting Azure token: {e}[/red]")
        console.print("[yellow]Please run 'az login' first[/yellow]")
    return None

async def check_postgres_quota(
    session: aiohttp.ClientSession,
    subscription_id: str,
    region: str,
    token: str
) -> Dict[str, QuotaCheck]:
    """Check PostgreSQL Flexible Server quota for a specific region"""
    api_version = "2024-11-01-preview"
    url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.DBforPostgreSQL/locations/{region}/resourceType/flexibleServers/usages?api-version={api_version}"
    
    try:
        async with session.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            if response.status != 200:
                return {}
            
            data = await response.json()
            quotas = {}
            
            for quota in data.get("value", []):
                name = quota["name"]["value"]
                current = quota["currentValue"]
                limit = quota["limit"]
                available = limit - current
                
                quotas[name] = QuotaCheck(
                    region=region,
                    current_value=current,
                    limit=limit,
                    available=available
                )
            
            return quotas
    except Exception as e:
        console.print(f"[red]Error checking PostgreSQL quota for {region}: {e}[/red]")
        return {}

async def check_container_apps_quota(
    session: aiohttp.ClientSession,
    subscription_id: str,
    region: str,
    token: str
) -> Dict[str, QuotaCheck]:
    """Check Container Apps quota for a specific region"""
    api_version = "2023-05-01"
    url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.App/locations/{region}/usages?api-version={api_version}"
    
    try:
        async with session.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            if response.status != 200:
                return {}
            
            data = await response.json()
            quotas = {}
            
            for quota in data.get("value", []):
                name = quota["name"]["value"]
                current = quota.get("currentValue", 0)
                limit = quota.get("limit", 0)
                available = limit - current
                
                quotas[f"ContainerApps_{name}"] = QuotaCheck(
                    region=region,
                    current_value=current,
                    limit=limit,
                    available=available
                )
            
            return quotas
    except Exception as e:
        console.print(f"[red]Error checking Container Apps quota for {region}: {e}[/red]")
        return {}

async def check_region_quota(
    session: aiohttp.ClientSession,
    subscription_id: str,
    region: str,
    token: str
) -> Optional[RegionQuota]:
    """Check all quotas for a specific region"""
    # Load configuration
    with open("infra/azure-config.json") as f:
        config = json.load(f)
    
    # Get quotas for different services
    postgres_quotas = await check_postgres_quota(session, subscription_id, region, token)
    container_quotas = await check_container_apps_quota(session, subscription_id, region, token)
    
    # Combine all quotas
    all_quotas = {**postgres_quotas, **container_quotas}
    
    if not all_quotas:
        return None
    
    # Check if we have sufficient quota
    has_sufficient_quota = True
    
    # Check PostgreSQL vCores
    required_vcores = config["required_services"]["postgresql"]["min_vcores"]
    if "BurstableVCores" in all_quotas:
        if all_quotas["BurstableVCores"].available < required_vcores:
            has_sufficient_quota = False
    
    # Check Container Apps requirements
    required_cpu = config["required_services"]["container_apps"]["resources"]["cpu"]
    if "ContainerApps_CpuCore" in all_quotas:
        if all_quotas["ContainerApps_CpuCore"].available < required_cpu:
            has_sufficient_quota = False
    
    return RegionQuota(
        region=region,
        quotas=all_quotas,
        has_sufficient_quota=has_sufficient_quota
    )

async def check_all_regions(subscription_id: str, token: str) -> List[RegionQuota]:
    """Check quotas for all configured regions"""
    with open("infra/azure-config.json") as f:
        config = json.load(f)
    
    regions = config["allowed_regions"]
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            check_region_quota(session, subscription_id, region, token)
            for region in regions
        ]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

def display_quota_results(quotas: List[RegionQuota]):
    """Display quota information in a formatted table"""
    table = Table(title="Azure Service Quotas by Region")
    
    table.add_column("Region", style="cyan")
    table.add_column("Service", style="magenta")
    table.add_column("Available/Limit", style="green")
    table.add_column("Status", style="yellow")
    
    for quota in quotas:
        region = quota.region
        for service_name, service_quota in quota.quotas.items():
            status = "[green]SUFFICIENT" if quota.has_sufficient_quota else "[red]INSUFFICIENT"
            table.add_row(
                region,
                service_name,
                f"{service_quota.available}/{service_quota.limit}",
                status
            )
    
    console.print(table)

@app.get("/check-quota")
async def check_quota():
    """API endpoint to check Azure quotas"""
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        raise HTTPException(status_code=400, detail="AZURE_SUBSCRIPTION_ID environment variable not set")
    
    token = await get_azure_token()
    if not token:
        raise HTTPException(status_code=401, detail="Could not get Azure token")
    
    quotas = await check_all_regions(subscription_id, token)
    return {"regions": quotas}

def main():
    """CLI entry point"""
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        console.print("[red]Error: AZURE_SUBSCRIPTION_ID environment variable not set[/red]")
        sys.exit(1)
    
    token = asyncio.run(get_azure_token())
    if not token:
        sys.exit(1)
    
    quotas = asyncio.run(check_all_regions(subscription_id, token))
    
    display_quota_results(quotas)
    
    # Filter regions with sufficient quota
    available_regions = [q.region for q in quotas if q.has_sufficient_quota]
    
    if not available_regions:
        console.print("\n[red]No regions have sufficient quota for deployment![/red]")
        console.print("\nTo request a quota increase:")
        console.print("1. Go to Azure Portal > Help + support > Create a support request")
        console.print("2. Select 'Quota' and choose the service that needs more capacity")
        console.print("3. Specify the required capacity increase")
        sys.exit(1)
    
    console.print("\n[green]Regions available for deployment:[/green]")
    for region in available_regions:
        console.print(f"• {region}")

if __name__ == "__main__":
    if "--server" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        main()