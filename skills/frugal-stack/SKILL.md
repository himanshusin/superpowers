---
name: frugal-stack
description: Keep web app infrastructure costs minimal for solo entrepreneurs and indie hackers. Use when building MVPs, side projects, or bootstrapped startups. Covers free tiers, cost-efficient architecture patterns, service comparisons, and scaling strategies. Helps choose hosting, databases, auth, storage, email, and monitoring services that won't break the bank. Think $0-50/month for most apps.
---

# Frugal Stack: Web App Cost Optimization

Build and run web apps on a shoestring budget. This guide helps solopreneurs make smart infrastructure decisions.

## Core Philosophy

```
┌─────────────────────────────────────────────────────────────┐
│  SOLOPRENEUR PRIORITIES                                     │
│                                                             │
│  1. Ship fast → Use managed services, skip DevOps          │
│  2. Start free → Graduate to paid only with revenue        │
│  3. Time = money → Don't over-optimize prematurely         │
│  4. Sleep well → Reliability > saving $5/month             │
│  5. Stay flexible → Avoid deep vendor lock-in              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Decision Framework

### What's your monthly budget?

| Budget | Recommended Stack |
|--------|-------------------|
| **$0** | Vercel/Cloudflare Pages + Supabase + Resend free tier |
| **$5-20** | Railway/Render + PlanetScale + Cloudflare R2 |
| **$20-50** | DigitalOcean App Platform + managed Postgres |
| **$50-100** | Small VPS + self-managed stack (if you have ops skills) |

### What type of app?

| App Type | Best Frugal Stack |
|----------|-------------------|
| **Static site/blog** | Cloudflare Pages (free forever) |
| **SaaS with auth** | Vercel + Supabase + Clerk/Auth.js |
| **API backend** | Railway or Render free tier |
| **Full-stack app** | Vercel + Neon/Supabase |
| **High-traffic site** | Cloudflare Workers + D1 + R2 |

## The $0 Stack (Seriously Free)

For MVPs and validation - run indefinitely at zero cost:

```
Frontend:     Cloudflare Pages or Vercel (unlimited sites)
Backend:      Cloudflare Workers (100k req/day free)
Database:     Supabase (500MB) or Turso (9GB) or Neon (512MB)
Auth:         Supabase Auth or Auth.js (free, self-hosted)
Storage:      Cloudflare R2 (10GB free, no egress fees!)
Email:        Resend (100/day) or Mailgun (1000/month for 3 months)
Analytics:    Plausible Cloud (free for <10k/mo) or Umami (self-host)
Monitoring:   Better Stack free tier or Checkly
Domains:      Cloudflare Registrar (at-cost, ~$9/yr for .com)
```

**Total: $0/month + ~$9/year for domain**

## Service Comparison by Category

### Hosting & Compute

| Service | Free Tier | Paid Starting | Best For |
|---------|-----------|---------------|----------|
| **Cloudflare Pages** | Unlimited | - | Static sites, SPAs |
| **Vercel** | 100GB bandwidth | $20/mo | Next.js, React |
| **Netlify** | 100GB bandwidth | $19/mo | Static + Functions |
| **Railway** | $5 credit/mo | $5/mo | Full-stack apps |
| **Render** | Static only | $7/mo | Docker, APIs |
| **Fly.io** | 3 shared VMs | ~$2/mo | Global edge apps |
| **Cloudflare Workers** | 100k req/day | $5/mo | Edge computing |

**Winner for $0**: Cloudflare Pages + Workers

### Databases

| Service | Free Tier | Paid Starting | Best For |
|---------|-----------|---------------|----------|
| **Supabase** | 500MB, 2 projects | $25/mo | Postgres + realtime |
| **Neon** | 512MB, branching | $19/mo | Serverless Postgres |
| **PlanetScale** | 5GB reads | $29/mo | MySQL, scale |
| **Turso** | 9GB, 500 DBs | $29/mo | SQLite edge |
| **Upstash** | 10k cmd/day | $0.2/100k | Redis, Kafka |
| **MongoDB Atlas** | 512MB | $9/mo | Document DB |

**Winner for $0**: Turso (most generous) or Supabase (best DX)

### Authentication

| Service | Free Tier | Paid Starting | Best For |
|---------|-----------|---------------|----------|
| **Supabase Auth** | Unlimited | included | If using Supabase |
| **Clerk** | 10k MAU | $25/mo | Best DX, components |
| **Auth.js** | Unlimited | free (self-host) | Roll your own |
| **Firebase Auth** | Unlimited | free | Google ecosystem |
| **Lucia** | Unlimited | free (library) | Full control |

**Winner for $0**: Supabase Auth or Auth.js

### File Storage

| Service | Free Tier | Paid Starting | Best For |
|---------|-----------|---------------|----------|
| **Cloudflare R2** | 10GB, no egress | $0.015/GB | Best value overall |
| **Supabase Storage** | 1GB | included | Integrated with DB |
| **Backblaze B2** | 10GB | $0.005/GB | Cheapest per GB |
| **AWS S3** | 5GB (12 mo) | $0.023/GB | Enterprise needs |
| **Uploadthing** | 2GB | $10/mo | Easy file uploads |

**Winner for $0**: Cloudflare R2 (no egress fees is huge)

### Email

| Service | Free Tier | Paid Starting | Best For |
|---------|-----------|---------------|----------|
| **Resend** | 100/day, 3k/mo | $20/mo | Best DX, modern |
| **Postmark** | 100/mo | $15/mo | Transactional |
| **Mailgun** | 1000/mo (3 mo) | $15/mo | High volume |
| **SendGrid** | 100/day | $20/mo | Marketing + Trans |
| **AWS SES** | 62k/mo (from EC2) | $0.10/1k | Cheapest at scale |

**Winner for $0**: Resend (best free tier + DX)

## Architecture Patterns

### Pattern 1: Serverless-First (Best for variable traffic)

```
User → Cloudflare CDN → Vercel Edge → Serverless Functions
                                            ↓
                                    Neon (serverless Postgres)
                                            ↓
                                    Cloudflare R2 (files)
```

**Cost model**: Pay only for what you use. Great for 0-1000 users.

### Pattern 2: Edge-Everything (Best for global, static-heavy)

```
User → Cloudflare Workers → D1 (SQLite at edge)
              ↓
         R2 (storage)
              ↓
         KV (cache)
```

**Cost model**: Extremely cheap at scale. 10M requests = ~$5.

### Pattern 3: Single VPS (Best for predictable workloads)

```
User → Cloudflare (proxy/CDN) → $5 VPS (Docker)
                                    ├── App
                                    ├── Postgres
                                    └── Redis
```

**Cost model**: Fixed $5-10/mo regardless of traffic. Requires ops knowledge.

## Cost Estimation Guide

### Typical Cost Breakdown

```
┌────────────────────────────────────────────┐
│  WHERE MONEY GOES (typical SaaS)           │
│                                            │
│  Compute/Hosting     35%  ████████░░░░░░░░│
│  Database            25%  ██████░░░░░░░░░░│
│  File Storage        15%  ████░░░░░░░░░░░░│
│  Email/Comms         10%  ███░░░░░░░░░░░░░│
│  Third-party APIs    10%  ███░░░░░░░░░░░░░│
│  Monitoring/Tools     5%  █░░░░░░░░░░░░░░░│
└────────────────────────────────────────────┘
```

### Cost Per User Benchmarks

| Users | Well-Optimized | Typical | Over-Engineered |
|-------|----------------|---------|-----------------|
| 100 | $0 | $10 | $50 |
| 1,000 | $5 | $30 | $150 |
| 10,000 | $30 | $150 | $500 |
| 100,000 | $200 | $800 | $3,000 |

**Target**: <$0.01/user/month for first 10k users

## Red Flags: Costs That Sneak Up

⚠️ **Bandwidth/Egress** - AWS, GCP charge heavily. Use Cloudflare R2.

⚠️ **Database connections** - Serverless = many connections. Use pooling.

⚠️ **Serverless cold starts** - Can hit free tier limits. Monitor usage.

⚠️ **Log storage** - Disable verbose logging in production.

⚠️ **Preview deployments** - Vercel/Netlify charge for build minutes.

⚠️ **Seats/MAU pricing** - Auth and analytics can spike with users.

## Cost Monitoring Setup

### Essential (Free) Monitoring

1. **Set billing alerts** on every service (even free ones)
2. **Track these metrics weekly**:
   - Database size and connections
   - Bandwidth usage
   - Serverless invocations
   - Storage growth rate

### Recommended Tools

```bash
# Infracost - estimate Terraform costs
brew install infracost

# AWS Cost Explorer CLI
aws ce get-cost-and-usage --time-period Start=2024-01-01,End=2024-01-31

# Vercel usage
vercel billing
```

## Scaling Without Breaking the Bank

### Stage 1: Free Tier (0-1000 users)
- Stay entirely on free tiers
- Focus on product, not infrastructure
- Acceptable: occasional slow responses

### Stage 2: Minimal Paid ($20-50/mo, 1k-10k users)
- Upgrade database first (biggest pain point)
- Add proper error monitoring (Sentry free tier)
- Keep compute serverless

### Stage 3: Growth ($50-200/mo, 10k-100k users)
- Consider dedicated compute
- Add caching layer (Redis/Upstash)
- Implement CDN for assets
- Review architecture for efficiency

### When to NOT optimize costs

- You're pre-product-market-fit
- Your time is worth more than $50/month savings
- Reliability would suffer
- You'd introduce technical debt

## Further Reading

- See `references/free-tiers.md` for comprehensive free tier limits
- See `references/cost-calculator.md` for estimation templates
- Run `scripts/cost_estimator.py` to estimate your stack costs
