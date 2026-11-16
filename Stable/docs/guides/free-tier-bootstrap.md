# Free-Tier Developer Bootstrap Guide

Curated zero-cost infrastructure and tools based on [`ripienaar/free-for-dev`](https://github.com/ripienaar/free-for-dev) for bootstrapping, initial project development, and launch phases without upfront capital.

---

## 1. Hosting & Edge Deployment (Free Tiers)

| Service | Free Tier Allocation | Ideal Use Case |
| :--- | :--- | :--- |
| **Cloudflare Pages / Workers** | Unlimited static requests, 100k free worker requests/day | Static frontends, edge API gateways, fast global DNS |
| **Vercel** | 100 GB bandwidth/month, unlimited serverless functions | Next.js, React, documentation sites |
| **Netlify** | 100 GB bandwidth/month, 300 build minutes | Static sites, single-page web applications |
| **Render** | Free web services (spins down after inactivity), free static sites | Background workers, lightweight Python/Node APIs |

---

## 2. Databases & Managed Storage (Free Tiers)

| Service | Free Tier Allocation | Ideal Use Case |
| :--- | :--- | :--- |
| **Supabase** | 500 MB Postgres database, 1 GB file storage, 50k monthly active users | Relational database, Postgres functions, Auth |
| **Neon** | Serverless Postgres with 0.5 GB storage, branchable DB | Branching test databases for `Dev/` environments |
| **Upstash** | 10,000 commands/day serverless Redis & Kafka | Low-latency caching, rate limiting, agent message queues |
| **Cloudflare R2** | 10 GB storage/month, zero egress fees | Asset, image, and artifact storage |

---

## 3. CI/CD & Code Security (Free Tiers)

| Service | Free Tier Allocation | Ideal Use Case |
| :--- | :--- | :--- |
| **GitHub Actions** | 2,000 free runner minutes/month for private repos, unlimited for public | Automated secret scanning, test suites, and build scripts |
| **Snyk** | 200 free tests/month | Automated dependency CVE vulnerability auditing |
| **GitGuardian** | Free for individual developers & small teams | Automated pre-commit API key & secret leak detection |

---

## 4. Email & Notifications (Free Tiers)

| Service | Free Tier Allocation | Ideal Use Case |
| :--- | :--- | :--- |
| **Resend** | 3,000 emails/month (100/day limit) | Modern developer transactional emails & alerts |
| **Brevo (Sendinblue)** | 300 emails/day | Transactional email & contact management |

---

## 5. Domain, DNS & SSL

- **Cloudflare DNS**: Free DDoS protection, free universal SSL/TLS certificates, free analytics.
- **Let's Encrypt**: Free automated SSL/TLS certificates for custom domains.

