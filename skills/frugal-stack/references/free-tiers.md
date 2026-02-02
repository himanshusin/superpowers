# Free Tier Encyclopedia

Comprehensive list of free tiers for web app infrastructure. Updated for 2024-2025.

## Hosting & Compute

### Static Hosting (All Free Forever)

| Service | Bandwidth | Build Min | Sites | Notes |
|---------|-----------|-----------|-------|-------|
| Cloudflare Pages | Unlimited | 500/mo | Unlimited | Best overall |
| Vercel | 100GB/mo | 6000/mo | Unlimited | Best for Next.js |
| Netlify | 100GB/mo | 300/mo | Unlimited | Good for Jamstack |
| GitHub Pages | 100GB/mo | - | Unlimited | Public repos only |
| Render | 100GB/mo | - | Unlimited | Static only free |
| Surge | Unlimited | - | Unlimited | CLI deploy |

### Serverless Functions

| Service | Requests | Compute | Notes |
|---------|----------|---------|-------|
| Cloudflare Workers | 100k/day | 10ms CPU | Most generous |
| Vercel Functions | 100GB-hrs | 10s timeout | Easy integration |
| Netlify Functions | 125k/mo | 10s timeout | Good free tier |
| AWS Lambda | 1M/mo | 400k GB-s | Complex pricing |
| Deno Deploy | 1M/mo | 50ms CPU | Deno/TS native |

### Containers/Apps

| Service | Free Offer | RAM | Notes |
|---------|------------|-----|-------|
| Railway | $5/mo credit | 512MB | Sleeps after inactivity |
| Render | Web services sleep | 512MB | 15min inactivity sleep |
| Fly.io | 3 shared VMs | 256MB each | Great for global |
| Google Cloud Run | 2M req/mo | 1GB | 180k vCPU-sec |
| Koyeb | 1 nano instance | 256MB | Always on |

## Databases

### Relational (SQL)

| Service | Storage | Connections | Limits |
|---------|---------|-------------|--------|
| **Supabase** | 500MB | 60 direct | 2 free projects, pauses after 1 week inactive |
| **Neon** | 512MB | 100 pooled | Branching included, scales to zero |
| **Turso** | 9GB total | Unlimited | 500 databases, SQLite-based |
| **PlanetScale** | 5GB | 1B row reads | MySQL, no free writes limit |
| **CockroachDB** | 10GB | - | 50M RUs/month |
| **Xata** | 15GB | - | 750 req/sec |

### NoSQL/Document

| Service | Storage | Operations | Notes |
|---------|---------|------------|-------|
| MongoDB Atlas | 512MB | Shared cluster | M0 tier |
| Firebase Firestore | 1GB | 50k reads/day | Google ecosystem |
| FaunaDB | 100MB | 100k reads | GraphQL native |
| Upstash Redis | 10k cmd/day | 256MB | Serverless Redis |

### Edge/Specialized

| Service | Free Tier | Best For |
|---------|-----------|----------|
| Cloudflare D1 | 5GB, 5M reads/day | SQLite at edge |
| Cloudflare KV | 100k reads/day | Key-value cache |
| Upstash Kafka | 10k msg/day | Event streaming |
| Upstash Vector | 10k vectors | AI embeddings |

## Authentication

| Service | MAU Limit | Features | Notes |
|---------|-----------|----------|-------|
| **Supabase Auth** | Unlimited | OAuth, Magic Link, MFA | Best if using Supabase |
| **Clerk** | 10,000 | Components, Org mgmt | Best DX |
| **Auth0** | 7,500 | Full-featured | Enterprise feel |
| **Firebase Auth** | Unlimited | Phone, OAuth | Google ecosystem |
| **WorkOS** | 1M | SSO, SCIM | Enterprise auth |
| **Kinde** | 10,500 | Modern UI | Growing platform |
| **Auth.js** | Unlimited | Self-hosted | Full control |
| **Lucia** | Unlimited | Library only | DIY approach |

## File Storage & CDN

| Service | Storage | Bandwidth | Egress Cost |
|---------|---------|-----------|-------------|
| **Cloudflare R2** | 10GB | Unlimited | FREE (!) |
| **Backblaze B2** | 10GB | 1GB/day | $0.01/GB |
| **Supabase Storage** | 1GB | 2GB | Included |
| **Uploadcare** | 3GB | 10GB | Included |
| **Imagekit** | 20GB | 20GB | Included |
| **Cloudinary** | 25GB | 25GB | Included |

### CDN Only

| Service | Free Tier | Notes |
|---------|-----------|-------|
| Cloudflare | Unlimited | Industry standard |
| Bunny CDN | 14-day trial | Cheapest paid |
| jsDelivr | Unlimited | Open source files |
| unpkg | Unlimited | npm packages |

## Email Services

### Transactional Email

| Service | Free/Month | Notes |
|---------|------------|-------|
| **Resend** | 3,000 (100/day) | Modern, great DX |
| **Postmark** | 100 | Best deliverability |
| **Mailgun** | 1,000 (3 months) | Then paid |
| **SendGrid** | 100/day | Marketing + transactional |
| **Mailjet** | 6,000 (200/day) | Good free tier |
| **Brevo** | 300/day | Formerly Sendinblue |
| **AWS SES** | 62k (from EC2) | Cheapest at scale |

### Email APIs for Receiving

| Service | Free Tier |
|---------|-----------|
| Mailgun Routes | Included |
| Postmark Inbound | 100/mo |
| SendGrid Inbound | 100/day |

## Analytics & Monitoring

### Web Analytics

| Service | Free Tier | Privacy |
|---------|-----------|---------|
| **Plausible** | 10k views/mo | Privacy-first |
| **Umami** | Self-host unlimited | Open source |
| **Fathom** | None (30-day trial) | Privacy-first |
| **Pirsch** | 10k views/mo | Privacy-first |
| **Google Analytics** | Unlimited | Privacy concerns |
| **Vercel Analytics** | Included | For Vercel users |
| **PostHog** | 1M events/mo | Product analytics |

### Error Tracking

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **Sentry** | 5k errors/mo | Industry standard |
| **LogRocket** | 1k sessions | Session replay |
| **Bugsnag** | 7.5k events | Good for mobile |
| **Highlight** | 500 sessions | Open source |

### Uptime Monitoring

| Service | Free Checks | Interval |
|---------|-------------|----------|
| **Better Stack** | 10 monitors | 3 min |
| **Checkly** | 5 checks | 10 min |
| **UptimeRobot** | 50 monitors | 5 min |
| **Pingdom** | 1 monitor | 1 min |
| **Freshping** | 50 checks | 1 min |

### Logging

| Service | Free Tier | Retention |
|---------|-----------|-----------|
| **Better Stack Logs** | 1GB/mo | 3 days |
| **Papertrail** | 50MB/mo | 7 days |
| **Logtail** | 1GB/mo | 3 days |
| **Axiom** | 500GB/mo | 30 days |

## CI/CD & DevOps

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **GitHub Actions** | 2000 min/mo | Public repos unlimited |
| **GitLab CI** | 400 min/mo | Good free tier |
| **Bitbucket Pipelines** | 50 min/mo | Limited |
| **CircleCI** | 6000 min/mo | Generous |
| **Render** | Auto-deploy | For Render apps |

## Domain & DNS

| Service | Pricing | Notes |
|---------|---------|-------|
| **Cloudflare Registrar** | At-cost (~$9/yr) | Best value |
| **Porkbun** | Competitive | Good alternative |
| **Namecheap** | Sales often | Watch for renewal prices |
| **Google Domains** | Sold to Squarespace | |

### Free Subdomains

- `*.vercel.app` - Vercel
- `*.pages.dev` - Cloudflare
- `*.netlify.app` - Netlify
- `*.railway.app` - Railway
- `*.fly.dev` - Fly.io

## Payments

| Service | Free Tier | Fees |
|---------|-----------|------|
| **Stripe** | No monthly | 2.9% + $0.30 |
| **Paddle** | No monthly | 5% + $0.50 |
| **LemonSqueezy** | No monthly | 5% + $0.50 |
| **Gumroad** | No monthly | 10% |

## AI/ML Services

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **OpenAI** | $5 credit | GPT-4, embeddings |
| **Anthropic** | $5 credit | Claude |
| **Hugging Face** | Inference API | Rate limited |
| **Replicate** | Some free models | Pay per second |
| **Together AI** | $25 credit | Open models |

## Miscellaneous

### Feature Flags
- **PostHog**: 1M events
- **LaunchDarkly**: 1k MAU
- **Flagsmith**: 50k requests

### Cron Jobs
- **Cron-job.org**: 50 jobs free
- **EasyCron**: 200 jobs free
- **Vercel Cron**: Included

### SMS/Push
- **Twilio**: $15 credit
- **Firebase Cloud Messaging**: Free unlimited
- **OneSignal**: 10k subscribers

### Search
- **Algolia**: 10k requests/mo
- **Typesense Cloud**: 100k docs
- **Meilisearch Cloud**: 100k docs
