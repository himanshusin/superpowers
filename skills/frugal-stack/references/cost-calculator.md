# Cost Calculator & Estimation Guide

Templates and formulas for estimating web app infrastructure costs.

## Quick Estimation Formula

```
Monthly Cost = Compute + Database + Storage + Bandwidth + Services

Where:
  Compute   = (requests/mo × avg_duration_ms × price_per_ms) or fixed_price
  Database  = base_price + (storage_GB × price_per_GB) + (connections × price)
  Storage   = (GB_stored × price_per_GB) + (GB_egress × egress_price)
  Bandwidth = GB_transferred × price_per_GB (often $0 with Cloudflare)
  Services  = auth_MAU_cost + email_volume_cost + other_saas
```

## Cost Estimation Templates

### Template 1: Simple SaaS App

```yaml
# Assumptions
users: 1000
page_views_per_user_per_month: 50
api_calls_per_page_view: 5
avg_storage_per_user_mb: 10

# Calculations
total_page_views: 50,000
total_api_calls: 250,000
total_storage_gb: 10

# Estimated Costs (using frugal stack)
hosting_vercel: $0 (within free tier)
database_supabase: $0 (within 500MB)
storage_r2: $0 (within 10GB)
auth_supabase: $0 (unlimited)
email_resend: $0 (within 3k/mo)

TOTAL: $0/month
```

### Template 2: Growing SaaS (10k users)

```yaml
# Assumptions
users: 10,000
page_views_per_user_per_month: 30
api_calls_per_page_view: 5
avg_storage_per_user_mb: 50
emails_per_user_per_month: 2

# Calculations
total_page_views: 300,000
total_api_calls: 1,500,000
total_storage_gb: 500
total_emails: 20,000

# Estimated Costs
hosting_vercel_pro: $20
database_supabase_pro: $25
storage_r2: $7.35 ((500-10) × $0.015)
auth_clerk: $0 (within 10k MAU)
email_resend_pro: $20

TOTAL: ~$72/month
```

### Template 3: High-Traffic App (100k users)

```yaml
# Assumptions
users: 100,000
page_views_per_user_per_month: 20
api_calls_per_page_view: 10
avg_storage_per_user_mb: 100
emails_per_user_per_month: 1

# Calculations
total_page_views: 2,000,000
total_api_calls: 20,000,000
total_storage_gb: 10,000
total_emails: 100,000

# Estimated Costs
hosting_railway: $50
database_supabase_team: $599 or self-host ~$100
storage_r2: $150 ((10000-10) × $0.015)
auth_clerk_pro: $99
email_aws_ses: $10

TOTAL: ~$310-$900/month depending on choices
```

## Per-Service Cost Formulas

### Vercel

```python
# Free tier
if bandwidth_gb <= 100 and build_minutes <= 6000:
    cost = 0

# Pro tier
cost = 20  # base
cost += max(0, bandwidth_gb - 1000) * 0.15  # overage
cost += max(0, build_minutes - 6000) * 0.01  # overage
```

### Supabase

```python
# Free tier
if storage_gb <= 0.5 and projects <= 2:
    cost = 0

# Pro tier
cost = 25  # base, includes 8GB storage
cost += max(0, storage_gb - 8) * 0.125  # overage
```

### Cloudflare Workers

```python
# Free tier
if requests_per_day <= 100000:
    cost = 0

# Paid tier
cost = 5  # base, includes 10M requests
cost += max(0, (requests_per_month - 10000000) / 1000000) * 0.50
```

### Cloudflare R2

```python
# Storage (per month)
storage_cost = max(0, storage_gb - 10) * 0.015

# Operations
class_a_cost = max(0, class_a_ops - 1000000) / 1000000 * 4.50  # writes
class_b_cost = max(0, class_b_ops - 10000000) / 1000000 * 0.36  # reads

# Egress is FREE
egress_cost = 0

total = storage_cost + class_a_cost + class_b_cost
```

### AWS Lambda

```python
# Free tier (first 12 months + always)
free_requests = 1000000
free_compute_gb_seconds = 400000

# Calculations
request_cost = max(0, requests - free_requests) * 0.0000002
compute_gb_seconds = (memory_mb / 1024) * duration_ms / 1000 * invocations
compute_cost = max(0, compute_gb_seconds - free_compute_gb_seconds) * 0.0000166667

total = request_cost + compute_cost
```

## Comparison Calculator

### Scenario: 1M API requests/month, 5GB database, 50GB storage

| Stack | Monthly Cost |
|-------|-------------|
| **Cloudflare (Workers + D1 + R2)** | ~$5 |
| **Vercel + Neon + R2** | ~$25 |
| **Railway + Supabase + R2** | ~$30 |
| **AWS (Lambda + RDS + S3)** | ~$80 |
| **DigitalOcean VPS** | ~$12 (requires ops) |

## Cost Optimization Checklist

### Before Launch
- [ ] Verify all services are on free tier
- [ ] Set up billing alerts at $1, $5, $20 thresholds
- [ ] Configure auto-scaling limits
- [ ] Enable caching where possible

### Monthly Review
- [ ] Check each service's usage dashboard
- [ ] Identify unused resources
- [ ] Review database query efficiency
- [ ] Check for bandwidth anomalies
- [ ] Evaluate if current tier is right-sized

### Scaling Triggers
- [ ] >80% of free tier → Plan upgrade path
- [ ] >$50/month → Review architecture efficiency
- [ ] >$200/month → Consider reserved/committed pricing
- [ ] >$500/month → Hire someone to optimize

## Unit Economics Target

For sustainable SaaS, aim for:

```
Customer Acquisition Cost (CAC) < 3x Monthly Revenue
Infrastructure Cost < 10% of Revenue
Infrastructure Cost per User < $0.01/month for first 10k users
```

### Example Calculation

```
Revenue per user: $10/month
Target infra cost: $1/user/month (10%)

At 1,000 users:
  Revenue: $10,000/month
  Max infra budget: $1,000/month
  
At 100 users (early stage):
  Revenue: $1,000/month
  Max infra budget: $100/month
  Reality: Likely $0-20 on free tiers
```

## Red Zone Costs (Avoid These)

| Trap | Why It's Expensive | Alternative |
|------|-------------------|-------------|
| AWS NAT Gateway | $0.045/hr + data | Use VPC endpoints |
| RDS Multi-AZ | 2x cost | Single AZ for non-critical |
| Elastic IPs | $0.005/hr if unused | Release unused |
| CloudWatch Logs | Storage adds up | Use external logging |
| Data Transfer (AWS/GCP) | $0.09/GB | Use Cloudflare |
| Vercel ISR | Revalidations cost | Static when possible |
