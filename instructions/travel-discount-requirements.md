# Travel Discount Comparison Tool - Project Requirements & Outline

## Executive Summary
A comprehensive tool to automatically test and compare hotel rates across multiple discount programs (AARP, AAA, senior, military, corporate codes, etc.) to identify the best available rates. The system will store historical data to analyze discount trends and patterns over time.

## Market Analysis - Existing Competition

### Similar Tools (Partial Solutions)
1. **HotelSlash** - Monitors booked hotel rates for price drops, automated rebooking
   - Focus: Post-booking price tracking
   - Gap: Doesn't compare discount codes upfront

2. **RatePunk Browser Extension** - Real-time hotel price comparison
   - Focus: Comparing prices across OTAs
   - Gap: No discount code testing

3. **trivago/Kayak/Hotels.com** - Price aggregators
   - Focus: Comparing base rates across booking sites
   - Gap: Doesn't test membership discounts

4. **Travel Arrow Chrome Extension** - Reveals hidden deals
   - Focus: Finding unpublished rates
   - Gap: Manual, no systematic discount testing

### Unique Value Proposition
**No existing tool systematically compares membership discount codes across properties.** Users currently must:
- Manually check each hotel website
- Remember to try each discount code
- Compare prices manually
- Repeat process for different dates
- Cannot track which discounts work best over time

---

## Project Requirements

### 1. Functional Requirements

#### 1.1 Core Features
- **Multi-site Scraping Engine**
  - Support major hotel chains (Marriott, Hilton, IHG, Hyatt, Wyndham, Best Western, etc.)
  - Support OTA sites (Booking.com, Expedia, Hotels.com)
  - Concurrent request handling for performance
  - Rate limiting and retry logic
  - Session management and cookie handling

- **Discount Code Testing**
  - AARP membership discount
  - AAA/CAA membership discount
  - Senior/AARP rates (age-based, typically 50+, 55+, 60+, 65+)
  - Military/Veterans discounts
  - Government employee rates
  - Corporate discount codes (user-configurable)
  - Student discounts
  - Custom promotional codes
  - Test with and without membership validation

- **Search Parameters**
  - Date range (check-in/check-out)
  - Location (city, address, coordinates, radius)
  - Number of guests (adults/children)
  - Room type preferences
  - Amenity filters (parking, breakfast, wifi, pet-friendly, etc.)
  - Star rating
  - Price range

- **Results Display**
  - Side-by-side comparison table
  - Sort by: price, discount amount, percentage saved, hotel rating
  - Filter results by discount type
  - Show total cost including taxes and fees
  - Highlight best deal
  - Show which discounts are actually available (some require verification)
  - Display original price vs discounted price
  - Calculate savings per discount type

- **Historical Data & Analytics**
  - Track price changes over time
  - Analyze which discounts offer best value by:
    - Hotel chain
    - Location/region
    - Day of week
    - Season
    - Booking window (how far in advance)
  - Trend visualization (charts/graphs)
  - Discount effectiveness scoring
  - Price prediction based on historical patterns

#### 1.2 User Interface Requirements
- **Dashboard**
  - Quick search interface
  - Recent searches
  - Saved searches
  - Alerts for price drops

- **Search Configuration**
  - Date picker with calendar view
  - Location search with autocomplete
  - Discount code selection (checkboxes)
  - Advanced filters (collapsible)

- **Results Page**
  - Responsive data table
  - Visual indicators for best deals
  - Export to CSV/Excel
  - Share results (URL with parameters)
  - Direct booking links

- **Analytics Dashboard**
  - Interactive charts (line, bar, heatmap)
  - Time range selector
  - Drill-down capabilities
  - Custom report generation

- **Settings**
  - User profile (membership numbers, preferences)
  - Notification preferences
  - API rate limit configuration
  - Database management

#### 1.3 Data Storage Requirements
- **Database Schema**
  - Hotels table (property details, chain affiliation, location)
  - Searches table (search parameters, timestamp, user)
  - Results table (hotel_id, search_id, discount_type, price, taxes, total, timestamp)
  - Discount_codes table (code, type, requirements, hotel_chain)
  - Users table (preferences, membership info)
  - Alerts table (user_id, criteria, active status)

- **Data Retention**
  - Store raw results for minimum 24 months
  - Aggregate older data for trend analysis
  - Configurable purge policies

### 2. Non-Functional Requirements

#### 2.1 Performance
- Search completion: < 30 seconds for 10 hotels with 5 discount types
- Concurrent searches: Support 10+ simultaneous users
- Database queries: < 2 seconds for analytics
- Page load time: < 3 seconds

#### 2.2 Scalability
- Horizontal scaling for scraping workers
- Database sharding for high-volume data
- Caching layer for frequently accessed data
- Queue system for background jobs

#### 2.3 Reliability
- 99% uptime target
- Graceful handling of failed scraping attempts
- Automatic retry with exponential backoff
- Error logging and monitoring
- Data backup (daily incremental, weekly full)

#### 2.4 Security
- Secure storage of user membership numbers (encryption)
- API rate limiting to prevent abuse
- Input validation and sanitization
- HTTPS for all connections
- Secure credential storage for automated bookings (if implemented)

#### 2.5 Compliance & Legal
- **Critical: Terms of Service Compliance**
  - Many hotel websites prohibit automated scraping
  - Risk of IP blocking or legal action
  - May need to use official APIs where available
  - Consider partnership approach with hotels

- **Data Privacy**
  - GDPR compliance for EU users
  - CCPA compliance for California users
  - Clear privacy policy
  - User data deletion capability

- **Fair Use**
  - Respect robots.txt
  - Reasonable request rates
  - User-agent identification
  - No excessive server load

### 3. Technical Requirements

#### 3.1 Technology Stack (AWS Serverless Architecture)

**Backend (AWS Serverless):**
- **Compute:** AWS Lambda (Python 3.11+ runtime)
- **API Layer:** Amazon API Gateway (REST or HTTP API)
- **Orchestration:** AWS Step Functions (coordinate multi-step scraping workflows)
- **Task Queue:** Amazon SQS (Standard for tasks, FIFO for ordering)
- **Event Management:** Amazon EventBridge (scheduling, triggers)
- **Database:** 
  - Amazon Aurora Serverless v2 (PostgreSQL-compatible) - for relational data
  - OR Amazon DynamoDB (NoSQL) - for high-scale, simpler queries
  - Amazon ElastiCache Serverless (Redis) - for caching
- **Storage:** Amazon S3 (raw scraping results, exports, static assets)
- **Web Scraping:**
  - Playwright in Lambda (using Lambda Layers)
  - AWS Fargate (for scraping tasks >15 min or requiring persistent browser)
  - Selenium Grid on ECS Fargate (for complex scenarios)

**Frontend (AWS Serverless):**
- **Framework:** React 18+ with TypeScript
- **Hosting:** Amazon S3 + CloudFront (CDN)
- **Deployment:** AWS Amplify (optional, includes CI/CD)
- **UI Library:** Tailwind CSS + shadcn/ui
- **Charts:** Recharts or Apache ECharts
- **State Management:** Zustand or TanStack Query
- **Build Tool:** Vite

**Authentication & Security:**
- **Auth:** Amazon Cognito (user pools, identity pools)
- **Secrets:** AWS Secrets Manager (API keys, credentials)
- **Encryption:** AWS KMS (Key Management Service)
- **WAF:** AWS WAF (protect API Gateway from abuse)

**Monitoring & Operations:**
- **Monitoring:** Amazon CloudWatch (metrics, alarms, dashboards)
- **Logging:** CloudWatch Logs + CloudWatch Insights
- **Tracing:** AWS X-Ray (distributed tracing)
- **Alerting:** Amazon SNS (notifications)

**CI/CD & Development:**
- **IaC:** AWS SAM or AWS CDK (Infrastructure as Code)
- **CI/CD:** AWS CodePipeline + CodeBuild
- **Version Control:** AWS CodeCommit or GitHub
- **Testing:** Lambda layers with pytest

**Optional Enhancements:**
- **Proxy Rotation:** AWS PrivateLink + Bright Data/ScraperAPI
- **CAPTCHA Solving:** 2Captcha or Anti-Captcha service
- **Data Lake:** AWS Glue + Amazon Athena (for advanced analytics)
- **Machine Learning:** Amazon SageMaker (price prediction models)

#### 3.2 Architecture (AWS Serverless)

```
┌─────────────────────────────────────────────────────────┐
│                      USER LAYER                         │
│  Web Browser → CloudFront (CDN) → S3 (Static Website)  │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   API LAYER                             │
│  API Gateway (REST API) + AWS WAF (Protection)         │
│  └─ Cognito Authorizer (JWT tokens)                    │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│ Search API   │ │ Results API  │ │Analytics API│ │ User API     │
│ (Lambda)     │ │ (Lambda)     │ │ (Lambda)    │ │ (Lambda)     │
└──────┬───────┘ └──────────────┘ └─────────────┘ └──────────────┘
       │
       │ Trigger Step Function
       ▼
┌─────────────────────────────────────────────────────────┐
│           AWS STEP FUNCTIONS (Orchestration)            │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 1. Validate Search → 2. Fan-out Hotels →        │   │
│  │ 3. Parallel Scraping → 4. Aggregate Results →   │   │
│  │ 5. Store Data → 6. Return Response              │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Scraper      │ │ Scraper      │ │ Scraper      │ │ Scraper      │
│ Lambda 1     │ │ Lambda 2     │ │ Lambda N     │ │ Fargate Task │
│ (Marriott)   │ │ (Hilton)     │ │ (IHG)        │ │ (Complex)    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │                │
       └────────────────┴────────────────┴────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
        ┌──────────────────┐          ┌────────────────┐
        │ Aurora Serverless│          │ ElastiCache    │
        │ (PostgreSQL)     │          │ Serverless     │
        │ - Hotels         │          │ (Redis)        │
        │ - Searches       │          │ - Session data │
        │ - Results        │          │ - Rate limits  │
        │ - Users          │          │ - Cache        │
        └──────────────────┘          └────────────────┘
                │
                ▼
        ┌──────────────────┐
        │  Amazon S3       │
        │ - Raw results    │
        │ - Exports (CSV)  │
        │ - Backups        │
        └──────────────────┘
                │
                ▼
        ┌──────────────────┐
        │ CloudWatch       │
        │ - Logs           │
        │ - Metrics        │
        │ - Alarms         │
        │ - Dashboards     │
        └──────────────────┘
```

**Data Flow:**
1. User makes search request → CloudFront → API Gateway
2. API Gateway authenticates via Cognito → routes to Search Lambda
3. Search Lambda validates input → triggers Step Function workflow
4. Step Function orchestrates parallel scraping via multiple Lambdas
5. Each scraper Lambda fetches hotel prices with different discount codes
6. Results aggregated → stored in Aurora Serverless + cached in ElastiCache
7. Raw data backed up to S3
8. Response returned to user via API Gateway
9. Frontend updates with results

**Key Benefits of Serverless Architecture:**
- **Auto-scaling:** Handles 1 or 1000 concurrent searches automatically
- **Cost-efficient:** Pay only for actual compute time (no idle servers)
- **High availability:** Built-in redundancy across AWS Availability Zones
- **Maintenance-free:** AWS manages infrastructure, patching, scaling
- **Fast deployment:** Update functions in seconds
- **Resilient:** Automatic retries and error handling

### 4. Development Phases (AWS Serverless)

#### Phase 1: MVP (Minimum Viable Product) - 4-6 weeks
**Scope:**
- AWS account setup + IAM configuration
- Infrastructure as Code (AWS SAM or CDK)
- Basic scraping for 3-5 major hotel chains
- Support for AARP, AAA, and senior discounts
- Simple search interface (React + S3/CloudFront)
- API Gateway + Lambda functions
- DynamoDB for data storage (easier to start than Aurora)
- Manual search only (no automation)

**AWS Services Used:**
- Lambda (API + scrapers)
- API Gateway
- DynamoDB
- S3 + CloudFront
- Cognito (basic auth)
- CloudWatch (monitoring)

**Deliverables:**
- Working proof of concept
- Basic frontend UI deployed to S3/CloudFront
- Core scraping Lambda functions (3-5 hotel chains)
- Simple database schema in DynamoDB
- Infrastructure as Code templates
- Basic monitoring dashboards

**Key Milestones:**
- Week 1-2: AWS setup, IaC templates, basic Lambda + API Gateway
- Week 3-4: Scraper development for 3 hotel chains
- Week 5: Frontend development and integration
- Week 6: Testing, monitoring, documentation

#### Phase 2: Enhanced Features - 5-7 weeks
**Scope:**
- Step Functions for workflow orchestration
- Expand to 15+ hotel chains
- Add OTA support (Booking.com, Expedia)
- More discount types (military, corporate)
- Historical data tracking in DynamoDB or Aurora
- ElastiCache Serverless for caching
- Basic analytics (CloudWatch + simple charts)
- User accounts with Cognito
- EventBridge for scheduled scraping
- Fargate for complex/long-running scrapes

**AWS Services Added:**
- Step Functions
- EventBridge
- ElastiCache Serverless (or DynamoDB caching)
- Fargate (ECS)
- Aurora Serverless v2 (optional, if DynamoDB limits reached)
- SNS (notifications)

**Deliverables:**
- Production-ready application
- Enhanced UI with filtering
- Historical data visualization
- User authentication & profiles
- Automated scheduled searches
- Email notifications

**Key Milestones:**
- Week 1-2: Step Functions workflows, expand scrapers
- Week 3-4: Historical tracking, caching layer
- Week 5-6: User management, notifications
- Week 7: Integration testing, performance optimization

#### Phase 3: Advanced Analytics - 3-5 weeks
**Scope:**
- Advanced trend analysis (Athena + Glue for data lake)
- Price prediction models (SageMaker or Lambda)
- Discount effectiveness scoring
- Custom alerts and notifications
- Export functionality (S3 pre-signed URLs)
- API documentation (API Gateway OpenAPI)
- Public API with usage plans and API keys

**AWS Services Added:**
- Athena (query S3 data)
- Glue (data catalog)
- SageMaker (optional, for ML models)
- EventBridge rules (complex alerts)
- SQS (notification queue)

**Deliverables:**
- Comprehensive analytics dashboard
- Automated reporting
- Advanced alert system
- Public API with documentation
- Data export features

**Key Milestones:**
- Week 1-2: Data lake setup, analytics queries
- Week 3-4: Prediction models, alert system
- Week 5: API documentation, public API

#### Phase 4: Scale & Optimize - 3-5 weeks
**Scope:**
- Performance optimization (Lambda memory/timeout tuning)
- WAF rules for security
- Proxy rotation for scraping (VPC + NAT Gateway or 3rd party)
- CAPTCHA handling (Lambda layers)
- Mobile-responsive design improvements
- Cost optimization (reserved capacity, caching)
- Advanced monitoring (X-Ray tracing)
- CI/CD pipeline (CodePipeline + CodeBuild)
- Multi-region deployment (optional)

**AWS Services Added:**
- WAF
- X-Ray
- VPC + NAT Gateway (for proxy)
- CodePipeline + CodeBuild + CodeDeploy
- CloudFormation StackSets (multi-region)
- Cost Explorer (cost optimization)

**Deliverables:**
- Scalable infrastructure (tested to 10K+ searches/day)
- Monitoring dashboards with alarms
- Automated CI/CD pipeline
- Production-ready deployment
- Operations runbook
- Cost optimization report

**Key Milestones:**
- Week 1: Performance testing and optimization
- Week 2: Security hardening (WAF, encryption)
- Week 3-4: CI/CD setup, advanced monitoring
- Week 5: Load testing, documentation

**Total Timeline:**
- **Solo developer:** 15-23 weeks (faster than traditional due to no infrastructure management)
- **Small team (2-3):** 10-14 weeks
- **Advantage:** 20-30% faster than traditional infrastructure approach

### 5. Risk Assessment

#### High Risk
1. **Legal/ToS Violations**
   - Mitigation: Use official APIs where available, implement rate limiting, consider partnership model
   
2. **IP Blocking**
   - Mitigation: Proxy rotation, reasonable request rates, random delays
   
3. **Website Structure Changes**
   - Mitigation: Modular scraper design, automated testing, quick update process

4. **CAPTCHA Challenges**
   - Mitigation: CAPTCHA solving services, reduce bot-like behavior, manual fallback

#### Medium Risk
1. **Performance Issues**
   - Mitigation: Async processing, caching, horizontal scaling
   
2. **Data Accuracy**
   - Mitigation: Multiple verification checks, user feedback system
   
3. **Cost Overruns**
   - Mitigation: Start with free/cheap options, scale gradually

#### Low Risk
1. **User Adoption**
   - Mitigation: Clear value proposition, free tier, user education
   
2. **Competition**
   - Mitigation: Unique feature set, superior UX

### 6. Success Metrics

**User Metrics:**
- Number of active users
- Searches per user per month
- User retention rate
- Feature adoption rate

**Technical Metrics:**
- Scraping success rate (target: >95%)
- Average search completion time
- System uptime
- Error rate

**Business Metrics:**
- Average savings per search
- User satisfaction score
- Revenue (if monetized)
- Cost per search

### 7. Budget Estimates (AWS Serverless - Monthly Operating Costs)

**AWS Services (estimates based on moderate usage):**

**Compute & API:**
- AWS Lambda: $0-50/month (generous free tier, then ~$0.20/1M requests)
- API Gateway: $0-20/month (1M free requests first year, then $3.50/1M)
- Step Functions: $0-10/month ($0.025/1K state transitions, 4K free/month)
- Fargate (long scrapes): $20-100/month (~$0.012/hour per task)

**Database & Caching:**
- Aurora Serverless v2: $45-150/month (scales with usage, 0.5-2 ACUs)
  - OR DynamoDB: $10-50/month (on-demand, pay per request)
- ElastiCache Serverless: $90-200/month (Redis caching)
  - OR use Lambda + S3 for caching: $5-20/month

**Storage & CDN:**
- S3: $5-25/month (data storage + requests)
- CloudFront: $10-50/month (CDN, 1TB free first year)

**Security & Monitoring:**
- Cognito: $0-5/month (50K MAUs free, then $0.0055/MAU)
- Secrets Manager: $0.40 per secret per month (~$5/month)
- CloudWatch: $5-30/month (logs, metrics, alarms)
- WAF: $5-20/month (web ACL + rules)

**Third-Party Services:**
- Proxy service (for scraping): $50-500/month (based on usage)
- CAPTCHA solving: $20-200/month (based on volume)

**Total Estimated Monthly Costs:**
- **Minimal usage (testing/MVP):** $50-200/month
- **Moderate usage (100-500 searches/day):** $200-600/month
- **High usage (1000+ searches/day):** $500-1,500/month

**Cost Optimization Strategies:**
1. **Use DynamoDB instead of Aurora** for 40-60% database cost savings
2. **Aggressive caching** reduces Lambda invocations
3. **Reserved Capacity** for predictable workloads (20-50% savings)
4. **S3 Intelligent-Tiering** for automatic storage optimization
5. **Limit scraping frequency** with smart deduplication
6. **Batch processing** during off-peak hours
7. **AWS Free Tier** provides substantial savings first 12 months

**First-Year AWS Free Tier Benefits:**
- Lambda: 1M requests/month forever
- DynamoDB: 25 GB + 25 WCU/RCU forever
- CloudWatch: 10 custom metrics, 5 GB logs forever
- S3: 5 GB storage first year
- CloudFront: 1 TB data transfer first year
- Cognito: 50K MAUs forever
- **Estimated first-year savings: $500-1,000**

**Development Costs (No Infrastructure to Manage):**
- Solo developer: 16-20 weeks (25% faster without infra management)
- Small team (2-3): 10-14 weeks
- Estimated: $12,000-40,000 (consulting/freelance)

**Comparison to Traditional Infrastructure:**
- **Traditional:** $160-1,200/month + infrastructure management time
- **Serverless:** $50-600/month + zero infrastructure management
- **Savings:** 40-70% on costs + 100% reduction in DevOps overhead

### 8. Future Enhancements

- Mobile app (iOS/Android)
- Browser extension
- Airline ticket discount comparison
- Car rental discount comparison
- Vacation package comparisons
- AI-powered price prediction
- Automatic rebooking when prices drop
- Integration with travel planning tools
- Social features (share deals with friends)
- Loyalty point value calculator

---

## Next Steps

1. **Review and confirm requirements** - Adjust scope based on priorities
2. **Choose technology stack** - Based on team expertise
3. **Set up development environment** - Tools, repos, infrastructure
4. **Create detailed implementation plan** - Break down into sprints/tasks
5. **Build MVP** - Start with core functionality
6. **Test and iterate** - Gather feedback, improve

## Legal Disclaimer

**Important:** This project involves web scraping, which may violate website Terms of Service. Before implementation:
- Consult with a lawyer specializing in technology/internet law
- Review each target website's robots.txt and ToS
- Consider using official APIs where available
- Implement respectful scraping practices
- Be prepared for potential legal challenges or cease-and-desist orders

The safest approach is to partner with hotels or use official APIs, though this may limit functionality.