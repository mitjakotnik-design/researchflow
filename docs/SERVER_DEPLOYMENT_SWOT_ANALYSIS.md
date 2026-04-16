# 🎯 SWOT ANALIZA - SERVERSKA IMPLEMENTACIJA ResearchFlow
**Datum:** 2026-04-16  
**Trenutno stanje:** Local Python system (v2.0, production-ready)  
**Cilj:** Scalable server deployment z web interface

---

## 📋 MOŽNOSTI ZA DEPLOYMENT

Analizirano **5 strategij** za prehod iz local sistema v server:

1. **Cloud-Native SaaS** (AWS/Azure/GCP)
2. **On-Premise Enterprise** (Self-hosted za institucije)
3. **Hybrid Model** (Cloud + on-premise option)
4. **API-Only Service** (Headless backend)
5. **Open-Source + Commercial** (Community + enterprise tiers)

---

# 1️⃣ CLOUD-NATIVE SaaS (AWS/GCP/Azure)

## 💪 STRENGTHS (Prednosti)

### Technical
- ✅ **Infinite scalability** - Auto-scaling based on demand
- ✅ **Managed services** - RDS, ElastiCache, S3, no ops overhead
- ✅ **High availability** - 99.99% uptime SLA
- ✅ **Global CDN** - Fast figure delivery worldwide
- ✅ **Monitoring built-in** - CloudWatch, Stackdriver
- ✅ **Security** - AWS Shield, WAF, encryption at rest/transit
- ✅ **Fast deployment** - CI/CD with GitHub Actions
- ✅ **Disaster recovery** - Automatic backups, point-in-time recovery

### Business
- ✅ **Time to market** - Launch v1.0 in 3-4 weeks
- ✅ **No hardware costs** - Pay-as-you-go
- ✅ **Easy updates** - Rolling deployments, no downtime
- ✅ **Global reach** - Multi-region from day 1
- ✅ **Startup-friendly** - Free tier for first 12 months (AWS)
- ✅ **Investor appeal** - Cloud-first = modern, scalable

### User Experience
- ✅ **Always accessible** - Web-based, any device
- ✅ **Collaboration** - Real-time multi-user editing
- ✅ **Automatic backups** - Never lose work
- ✅ **Mobile-friendly** - Responsive design

## ⚠️ WEAKNESSES (Slabosti)

### Technical
- ❌ **Vendor lock-in** - Tied to AWS/GCP/Azure ecosystem
- ❌ **Complex pricing** - Unpredictable costs at scale
- ❌ **Network dependency** - Requires internet connection
- ❌ **Cold start latency** - Serverless functions (Lambda) can be slow
- ❌ **ChromaDB challenges** - Vector DB not fully managed on all clouds
- ❌ **Data residency** - EU/US compliance issues (GDPR)

### Business
- ❌ **Ongoing costs** - Monthly bills even with low usage
- ❌ **Cost explosion risk** - LLM API costs can skyrocket
- ❌ **Support dependency** - Must pay for enterprise support
- ❌ **Migration difficulty** - Hard to switch providers later

### User Experience
- ❌ **Subscription fatigue** - Users tired of monthly fees
- ❌ **Privacy concerns** - Data stored in cloud
- ❌ **Academic skepticism** - Universities prefer on-premise

## 🌟 OPPORTUNITIES (Priložnosti)

- 🚀 **Rapid growth** - Target 10,000 users in year 1
- 🚀 **AI integration** - Easy to add new LLM models (Claude, GPT-5)
- 🚀 **Marketplace** - Third-party plugins/templates
- 🚀 **API ecosystem** - Partner integrations (Mendeley, Zotero, WOS)
- 🚀 **International expansion** - Multi-language support
- 🚀 **Freemium model** - Free tier drives adoption
- 🚀 **Team features** - Shared workspaces, commenting
- 🚀 **Analytics** - Usage insights, optimization recommendations

## ⚡ THREATS (Nevarnosti)

- ⚠️ **Competition** - Elsevier, Overleaf may launch similar tools
- ⚠️ **LLM cost volatility** - Google/OpenAI price changes
- ⚠️ **Regulatory** - EU AI Act, data protection laws
- ⚠️ **API deprecation** - Gemini SDK breaking changes
- ⚠️ **Service outages** - AWS downtime = our downtime
- ⚠️ **Security breach** - Reputational damage if hacked
- ⚠️ **Academic resistance** - "AI-generated = cheating" perception

---

# 2️⃣ ON-PREMISE ENTERPRISE (Self-Hosted)

## 💪 STRENGTHS

### Technical
- ✅ **Full control** - Complete infrastructure ownership
- ✅ **Data sovereignty** - All data stays on university servers
- ✅ **Custom integration** - Integrate with existing LDAP/SSO
- ✅ **No network dependency** - Works on internal network
- ✅ **ChromaDB optimization** - Tune for local hardware
- ✅ **Compliance** - Meet strict institutional requirements
- ✅ **No API limits** - Self-hosted LLM option (LLaMA, Mistral)

### Business
- ✅ **One-time license** - Perpetual license model
- ✅ **Predictable costs** - No surprise cloud bills
- ✅ **Academic appeal** - Universities prefer this model
- ✅ **High margin** - Charge $50K-$200K per institution
- ✅ **Enterprise contracts** - Multi-year agreements

### User Experience
- ✅ **Privacy** - Sensitive research data never leaves campus
- ✅ **Performance** - Low latency on local network
- ✅ **Offline capable** - Works without internet

## ⚠️ WEAKNESSES

### Technical
- ❌ **Complex deployment** - Docker/Kubernetes required
- ❌ **Update burden** - Manual upgrades, version conflicts
- ❌ **Hardware requirements** - Must provision servers
- ❌ **No auto-scaling** - Over-provision or face slowdowns
- ❌ **Maintenance overhead** - Customer IT teams need training
- ❌ **Backup responsibility** - Customer must implement
- ❌ **Multi-tenancy** - Each institution = separate deployment

### Business
- ❌ **Slow sales cycle** - 6-12 months procurement
- ❌ **High support costs** - Must support diverse environments
- ❌ **Limited reach** - Only enterprise customers
- ❌ **Revenue delay** - Annual billing, not monthly
- ❌ **Piracy risk** - License keys can be shared

### User Experience
- ❌ **Setup friction** - IT department must install
- ❌ **Version fragmentation** - Users on different versions
- ❌ **No collaboration** - Isolated installations

## 🌟 OPPORTUNITIES

- 🚀 **University market** - 5,000+ institutions globally
- 🚀 **Government contracts** - Research agencies (NSF, NIH)
- 🚀 **Pharma/healthcare** - HIPAA-compliant on-premise
- 🚀 **Consulting revenue** - Implementation services
- 🚀 **Certification programs** - Train administrators
- 🚀 **Whitelabel** - Rebrand for large customers

## ⚡ THREATS

- ⚠️ **Cloud preference** - IT departments moving to cloud
- ⚠️ **Open-source alternative** - Free fork emerges
- ⚠️ **Support burden** - Overwhelmed support team
- ⚠️ **Version debt** - Stuck maintaining old versions
- ⚠️ **Competitor entry** - SPSS, NVivo add scoping review

---

# 3️⃣ HYBRID MODEL (Cloud + On-Premise Option)

## 💪 STRENGTHS

### Technical
- ✅ **Best of both worlds** - Flexibility for customers
- ✅ **Code reuse** - Same codebase, different deployment
- ✅ **Migration path** - Start on-premise, move to cloud
- ✅ **Data sync** - Optional cloud backup for on-premise

### Business
- ✅ **Market coverage** - Serve both SMBs and enterprises
- ✅ **Revenue streams** - SaaS + licenses + support
- ✅ **Upsell path** - Free → Cloud → On-premise enterprise
- ✅ **Risk mitigation** - Not dependent on single model

### User Experience
- ✅ **Choice** - Users pick deployment that fits needs
- ✅ **Consistency** - Same UI/UX regardless of deployment

## ⚠️ WEAKNESSES

### Technical
- ❌ **Complexity** - Must maintain 2 deployment paths
- ❌ **Feature parity** - Hard to keep versions in sync
- ❌ **Testing burden** - Must test both environments
- ❌ **Docker + Cloud** - Two sets of tooling

### Business
- ❌ **Resource split** - Engineering team divided
- ❌ **Support complexity** - Two support workflows
- ❌ **Positioning confusion** - Unclear value proposition

### User Experience
- ❌ **Decision paralysis** - Users unsure which to pick
- ❌ **Migration friction** - Moving between deployments

## 🌟 OPPORTUNITIES

- 🚀 **Hedge strategy** - Win in both markets
- 🚀 **Platform play** - Become industry standard
- 🚀 **Data analytics** - Cloud customers provide usage insights

## ⚡ THREATS

- ⚠️ **Feature divergence** - Versions become incompatible
- ⚠️ **Cannibalization** - On-premise sales hurt cloud revenue

---

# 4️⃣ API-ONLY SERVICE (Headless Backend)

## 💪 STRENGTHS

### Technical
- ✅ **Focus** - Pure backend, no UI maintenance
- ✅ **Integration** - Embed in existing tools (RStudio, VS Code)
- ✅ **Flexibility** - Customers build custom frontends
- ✅ **Developer-friendly** - OpenAPI spec, SDKs
- ✅ **Scalability** - API easier to scale than full app

### Business
- ✅ **B2B focus** - Sell to tool vendors (Mendeley, Overleaf)
- ✅ **Volume pricing** - Per-API-call model
- ✅ **Low support** - Developers read docs, not tickets
- ✅ **Fast MVP** - Ship API in 2-3 weeks

### User Experience
- ✅ **Familiar tools** - Users stay in Zotero/Mendeley
- ✅ **Customization** - Users build exactly what they need

## ⚠️ WEAKNESSES

### Technical
- ❌ **No UI** - Limits adoption to technical users
- ❌ **Rate limiting** - Must prevent abuse
- ❌ **Versioning** - Breaking changes = angry developers

### Business
- ❌ **Commodity risk** - APIs easy to replicate
- ❌ **Low margin** - Price competition with OpenAI/Anthropic
- ❌ **Dependency** - Success tied to partner adoption
- ❌ **No branding** - Backend invisible to end users

### User Experience
- ❌ **Barrier to entry** - Non-coders excluded
- ❌ **Fragmented UX** - Inconsistent across integrations

## 🌟 OPPORTUNITIES

- 🚀 **Platform ecosystem** - 100+ integrations
- 🚀 **White-label** - Power other SaaS tools
- 🚀 **Academic partnerships** - Bundle with university systems

## ⚡ THREATS

- ⚠️ **Disintermediation** - Partners build own AI
- ⚠️ **LLM providers** - Google/OpenAI compete directly

---

# 5️⃣ OPEN-SOURCE + COMMERCIAL (Hybrid Licensing)

## 💪 STRENGTHS

### Technical
- ✅ **Community contributions** - Free R&D from users
- ✅ **Transparency** - Build trust through open code
- ✅ **Bug fixes** - Crowd-sourced testing
- ✅ **Extensibility** - Plugin ecosystem
- ✅ **Academic credibility** - Citable, peer-reviewed

### Business
- ✅ **Freemium funnel** - Free version drives awareness
- ✅ **Enterprise upsell** - Commercial license for features
- ✅ **Consulting** - Implementation + training revenue
- ✅ **Dual licensing** - GPL for community, proprietary for biz
- ✅ **Low CAC** - Word-of-mouth growth

### User Experience
- ✅ **Free forever** - Community edition always free
- ✅ **No lock-in** - Can fork if we disappear
- ✅ **Trust** - Transparent development

## ⚠️ WEAKNESSES

### Technical
- ❌ **Code exposure** - Competitors can copy
- ❌ **IP risk** - Contributors retain rights
- ❌ **Support burden** - Free users demand help
- ❌ **Feature withholding** - Hard to justify paid-only features

### Business
- ❌ **Slow revenue** - Most users stay on free tier
- ❌ **Competitor forks** - AWS may launch managed version
- ❌ **Conversion struggle** - 3-5% free-to-paid conversion typical
- ❌ **License complexity** - Legal overhead

### User Experience
- ❌ **Second-class free** - Free tier may feel limited
- ❌ **Upgrade pressure** - Annoying paywalls

## 🌟 OPPORTUNITIES

- 🚀 **GitHub stars** - Viral growth (10K+ stars)
- 🚀 **Academic adoption** - Default tool for researchers
- 🚀 **Contributor network** - Global developer community
- 🚀 **Standards body** - Define PRISMA-ScR automation standard
- 🚀 **Grant funding** - NSF, EU Horizon grants for open tools

## ⚡ THREATS

- ⚠️ **Free rider problem** - All use free, none pay
- ⚠️ **Hostile fork** - Competitor forks and out-competes
- ⚠️ **License trolls** - Legal challenges over GPL compliance
- ⚠️ **Burnout** - Maintaining free project drains resources

---

# 📊 COMPARATIVE MATRIX

| Criteria | Cloud SaaS | On-Premise | Hybrid | API-Only | Open-Source |
|----------|------------|------------|--------|----------|-------------|
| **Time to Market** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Initial Cost** | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Revenue Potential (Y1)** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Revenue Potential (Y3)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Academic Appeal** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Data Privacy** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Maintenance Burden** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **User Experience** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Competitive Moat** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Funding Appeal** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Global Reach** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Risk Level** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **TOTAL SCORE** | **47/60** | **34/60** | **42/60** | **40/60** | **41/60** |

---

# 🏆 RECOMMENDATION: HYBRID OPEN-SOURCE + CLOUD SaaS

## 🎯 Optimal Strategy

**Phase 1 (Months 1-3): Open-Source Foundation**
- Release core as MIT license on GitHub
- Community edition = full local functionality
- Build credibility + GitHub stars
- Target: 1,000 GitHub stars, 100 active users

**Phase 2 (Months 4-6): Cloud SaaS Launch**
- Launch managed cloud version
- Added features: collaboration, real-time sync, mobile app
- Freemium: 1 article/month free, unlimited for $19/month
- Target: 500 paying users, $9,500 MRR

**Phase 3 (Months 7-12): Enterprise Tier**
- On-premise option for universities
- SSO, LDAP, custom integration
- Price: $50K/year per institution + implementation
- Target: 5 enterprise customers, $250K ARR

**Phase 4 (Year 2): API + Marketplace**
- Public API for integrations
- Plugin marketplace (take 30% cut)
- White-label option for publishers
- Target: $500K ARR total

---

## 💰 FINANCIAL PROJECTION (3 YEARS)

### Year 1
| Revenue Stream | MRR | ARR |
|----------------|-----|-----|
| Cloud SaaS (500 users @ $19) | $9,500 | $114,000 |
| Enterprise (5 × $50K) | – | $250,000 |
| Consulting (10 projects @ $10K) | – | $100,000 |
| **TOTAL** | **$9,500** | **$464,000** |

**Costs:** $200K (2 developers, infra, marketing)  
**Profit:** $264K

### Year 2
| Revenue Stream | MRR | ARR |
|----------------|-----|-----|
| Cloud SaaS (2,500 users @ $19) | $47,500 | $570,000 |
| Enterprise (20 × $50K) | – | $1,000,000 |
| API usage | $5,000 | $60,000 |
| Marketplace (30% of $200K) | – | $60,000 |
| **TOTAL** | **$52,500** | **$1,690,000** |

**Costs:** $500K (5 employees, scaling)  
**Profit:** $1,190K

### Year 3
| Revenue Stream | MRR | ARR |
|----------------|-----|-----|
| Cloud SaaS (10,000 users @ $19) | $190,000 | $2,280,000 |
| Enterprise (50 × $50K) | – | $2,500,000 |
| API + marketplace | $20,000 | $240,000 |
| White-label (3 × $100K) | – | $300,000 |
| **TOTAL** | **$210,000** | **$5,320,000** |

**Costs:** $1,500K (15 employees, global expansion)  
**Profit:** $3,820K

---

## 🛠️ TECHNICAL ARCHITECTURE (Recommended)

### Stack
```
Frontend: React + TypeScript + TailwindCSS
Backend: FastAPI (Python) + Celery (task queue)
Database: PostgreSQL (metadata) + ChromaDB (vectors) + Redis (cache)
Storage: S3/R2 (PDFs, figures)
Deployment: Docker + Kubernetes (AWS EKS / GCP GKE)
Monitoring: Prometheus + Grafana + Sentry
Auth: Auth0 / Supabase Auth
LLM: Gemini 2.5 Pro (with fallback to OpenAI GPT-4)
CI/CD: GitHub Actions
Search: Algolia (article search) + ChromaDB (semantic)
```

### Infrastructure
```
Production: 3 environments (dev, staging, prod)
Regions: US-East, EU-West, Asia-Pacific
Auto-scaling: 2-20 pods based on load
Database: Multi-AZ PostgreSQL RDS
CDN: CloudFlare for global delivery
Backups: Daily snapshots + WAL archiving
Monitoring: 24/7 alerting, 99.9% uptime SLA
```

---

## 🎬 12-MONTH ROADMAP

### Q1 2026 (Apr-Jun): Foundation
- ✅ Week 1-2: Open-source repo setup, MIT license
- ✅ Week 3-4: Docker containerization
- ✅ Week 5-8: FastAPI backend scaffold
- ✅ Week 9-12: React frontend MVP

**Milestone:** 100 GitHub stars, 50 users testing locally

### Q2 2026 (Jul-Sep): Cloud Launch
- ✅ Week 13-16: Auth, user management, billing (Stripe)
- ✅ Week 17-20: Cloud deployment (AWS)
- ✅ Week 21-24: Marketing push, Product Hunt launch

**Milestone:** 500 cloud users, $9.5K MRR

### Q3 2026 (Oct-Dec): Enterprise
- ✅ Week 25-28: SSO/LDAP integration
- ✅ Week 29-32: On-premise deployment toolkit
- ✅ Week 33-36: First enterprise customer onboarding

**Milestone:** 5 enterprise deals, $250K ARR

### Q4 2026 (Jan-Mar 2027): Scale
- ✅ Week 37-40: API v1.0 launch
- ✅ Week 41-44: Marketplace alpha
- ✅ Week 45-48: International expansion (EU compliance)

**Milestone:** 2,000 total users, $464K ARR

---

## ✅ DECISION FRAMEWORK

### Choose This Strategy If:
- ✅ You want maximum market coverage (free → paid → enterprise)
- ✅ You value community growth + credibility
- ✅ You're willing to support open-source + cloud simultaneously
- ✅ You have 2-3 developers to start
- ✅ You can invest $50K-$100K in Year 1
- ✅ You're targeting 3-5 year exit (acquisition by Elsevier/SAGE/Springer)

### Red Flags (Don't Choose If):
- ❌ Solo developer (need minimum 2 people)
- ❌ No funding (need runway for 12 months)
- ❌ Unwilling to open-source (kills credibility)
- ❌ Need profitability in Month 1 (takes 6-9 months)

---

## 🎯 SUCCESS METRICS (KPIs)

### Product Metrics
- GitHub stars: 100 (M3) → 1,000 (M6) → 5,000 (M12)
- Active users: 50 (M3) → 500 (M6) → 2,500 (M12)
- Articles generated: 200 (M3) → 5,000 (M6) → 25,000 (M12)
- Average quality score: 75+ → 80+ → 85+

### Business Metrics
- MRR: $0 (M3) → $9.5K (M6) → $50K (M12)
- ARR: $0 (M6) → $464K (M12)
- CAC: < $50 (organic) → < $100 (paid)
- LTV: $500 (2+ years retention)
- LTV/CAC: 5:1 target

### Technical Metrics
- Uptime: 99.9%+
- API latency: p95 < 500ms
- Article generation time: < 2 hours
- Error rate: < 0.1%
- ChromaDB query time: < 100ms

---

## 🚧 RISKS & MITIGATION

### Risk 1: LLM Cost Explosion
**Mitigation:**
- Use Gemini 2.5 Flash ($0.075/M tokens vs GPT-4 $10/M)
- Implement caching (ChromaDB stores previous generations)
- User-pays model for enterprise (pass through costs)
- Monthly cap per user (prevent abuse)

### Risk 2: Open-Source Fork Competing
**Mitigation:**
- Strong brand + community
- Cloud features = competitive moat (collaboration, sync)
- Enterprise support = revenue not easily replicated
- CLA (Contributor License Agreement) to prevent hostile forks

### Risk 3: Academic Resistance ("AI = Cheating")
**Mitigation:**
- Transparency: Show all sources, citations
- Human-in-the-loop: Require manual review
- Marketing: Position as "research assistant" not "author"
- Collaborate with journals: Get editorial board endorsement

### Risk 4: Scalability Challenges
**Mitigation:**
- Start with proven stack (FastAPI, Postgres, K8s)
- Horizontal scaling from day 1
- Queue system for long-running tasks (Celery)
- Load testing before launch (Locust, k6)

---

## 📞 NEXT STEPS

### Immediate (This Week)
1. ✅ **Decision:** Approve hybrid open-source + cloud strategy
2. ⏳ **Legal:** Set up company entity (LLC/Corp)
3. ⏳ **Branding:** Register domain (researchflow.ai?)
4. ⏳ **GitHub:** Create public repo, add MIT license
5. ⏳ **Team:** Recruit 1 frontend developer

### Short-term (Next Month)
1. ⏳ **Architecture:** Finalize tech stack
2. ⏳ **Design:** UI/UX mockups (Figma)
3. ⏳ **Infrastructure:** AWS account, CI/CD pipeline
4. ⏳ **MVP:** Ship open-source v0.1
5. ⏳ **Community:** Reddit/Twitter launch, get feedback

### Medium-term (3 Months)
1. ⏳ **Cloud:** Launch SaaS beta
2. ⏳ **Pricing:** Finalize freemium model
3. ⏳ **Marketing:** Content marketing (blog, SEO)
4. ⏳ **Pilots:** 5 beta enterprise customers
5. ⏳ **Funding:** Seek angel/seed round ($500K-$1M)

---

# 📌 FINAL RECOMMENDATION

## **Choose: Hybrid Open-Source (MIT) + Cloud SaaS**

### Why This Wins:
1. **Lowest risk** - Open-source builds trust, cloud generates revenue
2. **Fastest growth** - Viral GitHub + paid conversions
3. **Highest credibility** - Academic community respects open source
4. **Best economics** - Freemium funnel > enterprise upsell
5. **Exit potential** - Attractive to acquirers (Elsevier, SAGE, Springer)

### Success Probability: **75%**
- 90% chance of 1,000 GitHub stars (open-source appeal)
- 70% chance of hitting $500K ARR in Year 1 (competitive market)
- 60% chance of profitable enterprise sales (long sales cycles)

### Capital Required: **$200K Year 1** (bootstrappable if 2 co-founders)

---

**Priporočam, da začnemo z implementacijo te strategije. Želiš, da začnem z:**

1. **GitHub repo setup** + MIT LICENSE + README?
2. **FastAPI backend scaffold** (users, auth, articles)?
3. **React frontend mockups** (Figma wireframes)?
4. **Docker containerization** (local development)?
5. **AWS infrastructure plan** (Terraform/CloudFormation)?

Povej mi, kam naj se lotim! 🚀
