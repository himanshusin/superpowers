#!/usr/bin/env python3
"""
Frugal Stack Cost Estimator
Interactive tool to estimate monthly infrastructure costs for web apps.

Usage:
    python cost_estimator.py                    # Interactive mode
    python cost_estimator.py --users 1000       # Quick estimate
    python cost_estimator.py --json config.json # From config file
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AppMetrics:
    """Application usage metrics."""
    users: int = 1000
    page_views_per_user: int = 30
    api_calls_per_page: int = 5
    storage_per_user_mb: float = 10
    emails_per_user: float = 1
    file_uploads_per_user_mb: float = 5


@dataclass 
class ServiceCost:
    """Individual service cost breakdown."""
    name: str
    tier: str
    base_cost: float
    usage_cost: float
    total: float
    notes: str = ""
    
    def __str__(self):
        if self.notes:
            return f"{self.name} ({self.tier}): ${self.total:.2f} - {self.notes}"
        return f"{self.name} ({self.tier}): ${self.total:.2f}"


class CostEstimator:
    """Estimate infrastructure costs for various stacks."""
    
    def __init__(self, metrics: AppMetrics):
        self.metrics = metrics
        self._calculate_derived()
    
    def _calculate_derived(self):
        """Calculate derived metrics."""
        m = self.metrics
        self.total_page_views = m.users * m.page_views_per_user
        self.total_api_calls = self.total_page_views * m.api_calls_per_page
        self.total_storage_gb = (m.users * m.storage_per_user_mb) / 1024
        self.total_emails = int(m.users * m.emails_per_user)
        self.total_file_storage_gb = (m.users * m.file_uploads_per_user_mb) / 1024
    
    def estimate_vercel(self) -> ServiceCost:
        """Estimate Vercel hosting costs."""
        # Free tier: 100GB bandwidth, 6000 build minutes
        bandwidth_gb = self.total_page_views * 0.5 / 1024  # ~0.5MB per page
        
        if bandwidth_gb <= 100:
            return ServiceCost("Vercel", "Free", 0, 0, 0, "Within free tier")
        
        # Pro tier
        base = 20
        overage = max(0, bandwidth_gb - 1000) * 0.15
        return ServiceCost("Vercel", "Pro", base, overage, base + overage)
    
    def estimate_cloudflare_pages(self) -> ServiceCost:
        """Estimate Cloudflare Pages costs."""
        # Unlimited bandwidth, 500 builds/month
        return ServiceCost("Cloudflare Pages", "Free", 0, 0, 0, "Unlimited bandwidth")
    
    def estimate_supabase(self) -> ServiceCost:
        """Estimate Supabase costs (DB + Auth + Storage)."""
        storage_gb = self.total_storage_gb
        
        if storage_gb <= 0.5:
            return ServiceCost("Supabase", "Free", 0, 0, 0, "Within 500MB limit")
        
        # Pro tier
        base = 25  # Includes 8GB
        overage = max(0, storage_gb - 8) * 0.125
        return ServiceCost("Supabase", "Pro", base, overage, base + overage)
    
    def estimate_neon(self) -> ServiceCost:
        """Estimate Neon Postgres costs."""
        storage_gb = self.total_storage_gb
        
        if storage_gb <= 0.5:
            return ServiceCost("Neon", "Free", 0, 0, 0, "Within 512MB limit")
        
        # Launch tier
        base = 19
        return ServiceCost("Neon", "Launch", base, 0, base, "10GB included")
    
    def estimate_turso(self) -> ServiceCost:
        """Estimate Turso (SQLite) costs."""
        storage_gb = self.total_storage_gb
        
        if storage_gb <= 9:
            return ServiceCost("Turso", "Free", 0, 0, 0, "Within 9GB limit")
        
        base = 29
        return ServiceCost("Turso", "Scaler", base, 0, base)
    
    def estimate_cloudflare_r2(self) -> ServiceCost:
        """Estimate Cloudflare R2 storage costs."""
        storage_gb = self.total_file_storage_gb
        
        if storage_gb <= 10:
            return ServiceCost("Cloudflare R2", "Free", 0, 0, 0, "10GB free, no egress")
        
        # Storage only, egress is free
        storage_cost = (storage_gb - 10) * 0.015
        return ServiceCost("Cloudflare R2", "Paid", 0, storage_cost, storage_cost, "No egress fees")
    
    def estimate_resend(self) -> ServiceCost:
        """Estimate Resend email costs."""
        emails = self.total_emails
        
        if emails <= 3000:
            return ServiceCost("Resend", "Free", 0, 0, 0, "3k/month free")
        
        if emails <= 50000:
            return ServiceCost("Resend", "Pro", 20, 0, 20, "50k included")
        
        # Business
        base = 80
        overage = max(0, emails - 100000) * 0.0004
        return ServiceCost("Resend", "Business", base, overage, base + overage)
    
    def estimate_clerk(self) -> ServiceCost:
        """Estimate Clerk auth costs."""
        mau = self.metrics.users
        
        if mau <= 10000:
            return ServiceCost("Clerk", "Free", 0, 0, 0, "10k MAU free")
        
        # Pro tier
        base = 25
        overage = max(0, mau - 10000) * 0.02
        return ServiceCost("Clerk", "Pro", base, overage, base + overage)
    
    def estimate_railway(self) -> ServiceCost:
        """Estimate Railway hosting costs."""
        # $5 credit covers small apps
        if self.total_api_calls < 100000:
            return ServiceCost("Railway", "Free", 0, 0, 0, "$5 credit covers usage")
        
        # Estimate based on usage
        estimated = 5 + (self.total_api_calls / 1000000) * 2
        return ServiceCost("Railway", "Paid", 5, estimated - 5, estimated)
    
    def get_frugal_stack(self) -> dict:
        """Get the most cost-effective stack."""
        services = [
            self.estimate_cloudflare_pages(),
            self.estimate_supabase(),
            self.estimate_cloudflare_r2(),
            self.estimate_resend(),
        ]
        
        total = sum(s.total for s in services)
        
        return {
            "name": "Frugal Stack (Cloudflare + Supabase)",
            "services": services,
            "total": total,
            "notes": "Best for $0-$50/month budgets"
        }
    
    def get_vercel_stack(self) -> dict:
        """Get Vercel-based stack."""
        services = [
            self.estimate_vercel(),
            self.estimate_neon(),
            self.estimate_cloudflare_r2(),
            self.estimate_resend(),
            self.estimate_clerk(),
        ]
        
        total = sum(s.total for s in services)
        
        return {
            "name": "Vercel Stack (Best DX)",
            "services": services,
            "total": total,
            "notes": "Best developer experience"
        }
    
    def get_all_estimates(self) -> list[dict]:
        """Get estimates for all stack options."""
        return [
            self.get_frugal_stack(),
            self.get_vercel_stack(),
        ]
    
    def print_report(self):
        """Print a formatted cost report."""
        print("\n" + "="*60)
        print("FRUGAL STACK COST ESTIMATOR")
        print("="*60)
        
        print(f"\n📊 INPUT METRICS")
        print(f"   Users: {self.metrics.users:,}")
        print(f"   Page views/user/month: {self.metrics.page_views_per_user}")
        print(f"   API calls/page: {self.metrics.api_calls_per_page}")
        print(f"   Storage/user: {self.metrics.storage_per_user_mb}MB")
        print(f"   Emails/user/month: {self.metrics.emails_per_user}")
        
        print(f"\n📈 DERIVED METRICS")
        print(f"   Total page views: {self.total_page_views:,}/month")
        print(f"   Total API calls: {self.total_api_calls:,}/month")
        print(f"   Total DB storage: {self.total_storage_gb:.2f}GB")
        print(f"   Total file storage: {self.total_file_storage_gb:.2f}GB")
        print(f"   Total emails: {self.total_emails:,}/month")
        
        for stack in self.get_all_estimates():
            print(f"\n{'─'*60}")
            print(f"💰 {stack['name']}")
            print(f"   {stack['notes']}")
            print(f"{'─'*60}")
            
            for service in stack['services']:
                status = "✅" if service.total == 0 else "💵"
                print(f"   {status} {service}")
            
            print(f"\n   📊 TOTAL: ${stack['total']:.2f}/month")
            
            if stack['total'] == 0:
                print("   🎉 Completely FREE!")
            elif stack['total'] < 25:
                print("   ✨ Very affordable!")
            elif stack['total'] < 100:
                print("   👍 Reasonable for a growing app")
        
        print(f"\n{'='*60}")
        print("💡 RECOMMENDATIONS")
        print("="*60)
        
        if self.metrics.users <= 1000:
            print("   • Stay on free tiers - you have room to grow!")
            print("   • Focus on product, not infrastructure")
        elif self.metrics.users <= 10000:
            print("   • Consider upgrading database first")
            print("   • Set up billing alerts on all services")
        else:
            print("   • Review architecture for efficiency")
            print("   • Consider reserved/committed pricing")
            print("   • May be time to hire DevOps help")


def interactive_mode():
    """Run interactive cost estimation."""
    print("\n🚀 Frugal Stack Cost Estimator")
    print("Answer a few questions to estimate your costs.\n")
    
    try:
        users = int(input("Expected monthly active users [1000]: ") or "1000")
        page_views = int(input("Page views per user per month [30]: ") or "30")
        api_calls = int(input("API calls per page view [5]: ") or "5")
        storage = float(input("Database storage per user (MB) [10]: ") or "10")
        emails = float(input("Emails per user per month [1]: ") or "1")
        files = float(input("File uploads per user (MB) [5]: ") or "5")
    except ValueError:
        print("Invalid input. Using defaults.")
        users, page_views, api_calls, storage, emails, files = 1000, 30, 5, 10, 1, 5
    
    metrics = AppMetrics(
        users=users,
        page_views_per_user=page_views,
        api_calls_per_page=api_calls,
        storage_per_user_mb=storage,
        emails_per_user=emails,
        file_uploads_per_user_mb=files
    )
    
    estimator = CostEstimator(metrics)
    estimator.print_report()


def quick_estimate(users: int):
    """Quick estimate with just user count."""
    metrics = AppMetrics(users=users)
    estimator = CostEstimator(metrics)
    estimator.print_report()


def from_json(config_path: str):
    """Load metrics from JSON file."""
    with open(config_path) as f:
        config = json.load(f)
    
    metrics = AppMetrics(**config)
    estimator = CostEstimator(metrics)
    estimator.print_report()


def main():
    parser = argparse.ArgumentParser(
        description="Estimate web app infrastructure costs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python cost_estimator.py                     # Interactive mode
    python cost_estimator.py --users 5000        # Quick estimate
    python cost_estimator.py --json metrics.json # From config file

Config JSON format:
{
    "users": 5000,
    "page_views_per_user": 30,
    "api_calls_per_page": 5,
    "storage_per_user_mb": 10,
    "emails_per_user": 1,
    "file_uploads_per_user_mb": 5
}
        """
    )
    parser.add_argument("--users", type=int, help="Quick estimate with user count")
    parser.add_argument("--json", type=str, help="Load metrics from JSON file")
    
    args = parser.parse_args()
    
    if args.json:
        from_json(args.json)
    elif args.users:
        quick_estimate(args.users)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
