# Travel Discount Comparison Tool - Project Context Document

**Last Updated:** September 30, 2025
**Project Status:** Implementation Planning Complete
**Current Phase:** Ready to Begin Development

**Documentation Status:**
- ✅ Requirements defined and approved
- ✅ AWS Serverless architecture designed
- ✅ Phase 1 (MVP) implementation plan complete with code examples
- ✅ Phase 2 (Enhanced) implementation plan complete
- ✅ Phase 3 (Analytics) implementation plan complete
- ✅ Phase 4 (Scale) implementation plan complete
- ⏳ Ready to begin development

---

## Project Overview

### Core Concept
An automated tool that compares hotel rates across multiple discount programs (AARP, AAA, senior, military, etc.) to identify the best available rates. Stores historical data for trend analysis over time.

### Problem Statement
- Travelers with multiple memberships (AARP, AAA, etc.) must manually check each hotel website with each discount code
- No existing tool systematically compares membership discounts
- Impossible to track which discounts perform best over time
- Time-consuming process prevents optimal deal discovery

### Solution
Web-based application that:
1. Automatically tests multiple discount codes across hotel websites
2. Presents side-by-side comparison in a clear interface
3. Stores historical pricing data
4. Visualizes discount trends and patterns
5. Alerts users to price drops

---

## Conversation History

### Initial Request (User)
*"I want to build a tool that can go out to different hotel and travel websites, and attempt to create a booking with selecting different options for discounts like AARP, AAA etc. The tool should provide a simple interface to display the results and findings. It should allow user to adjust the parameters of dates etc. for the comparison. The data should be stored in a database such that trends over time can be visualized."*

**Key Requirements Identified:**
- Multi-site scraping capability
- Discount code testing (AARP, AAA, etc.)
- Simple user interface
- Adjustable search parameters
- Database storage
- Trend visualization

### Research Conducted
**Competition Analysis:**
- HotelSlash - post-booking price tracking
- RatePunk - browser extension for OTA comparison
- trivago/Kayak - price aggregators
- Travel Arrow - Chrome extension for deals

**Finding:** No existing tool systematically compares membership discount codes upfront across properties.

### Artifacts Created
1. **Requirements & Outline Document** - Comprehensive project requirements including:
   - Market analysis
   - Functional requirements
   - Non-functional requirements
   - Technology stack recommendations
   - Architecture design
   - 4-phase development plan
   - Risk assessment
   - Budget estimates
   - Success metrics

2. **This Context Document** - For conversation continuity

---

## Key Decisions & Considerations

### Technology Stack (Recommended)
**Backend:**
- Python 3.11+ with FastAPI
- Selenium/Playwright for browser automation
- Celery + Redis for task queuing
- PostgreSQL for primary database
- Redis for caching

**Frontend:**
- React 18+ with TypeScript
- Material-UI or Tailwind CSS
- Recharts for data visualization
- Vite for building

**Infrastructure:**
- Docker containerization
- Nginx reverse proxy
- Prometheus + Grafana monitoring

### Critical Legal Considerations
⚠️ **IMPORTANT:** Web scraping may violate website Terms of Service
- Consult legal counsel before implementation
- Review each target site's robots.txt and ToS
- Consider official APIs where available
- Implement respectful scraping practices
- Proxy rotation to avoid IP bans
- Rate limiting and random delays

### Architectural Approach
- Microservices architecture
- Async task processing with worker pools
- API-first design
- Separation of scraping logic from business logic
- Modular scrapers (one per hotel chain)

---

## Project Scope & Phases (AWS Serverless)

### Phase 1: MVP (4-6 weeks)
**Target:**
- AWS account setup + IAM
- Infrastructure as Code (SAM/CDK)
- 3-5 major hotel chains
- AARP, AAA, senior discounts
- React frontend on S3/CloudFront
- API Gateway + Lambda
- DynamoDB database
- Manual searches only

**Technologies:**
- Lambda + API Gateway
- DynamoDB
- S3 + CloudFront
- Cognito (basic auth)
- CloudWatch

### Phase 2: Enhanced Features (5-7 weeks)
**Target:**
- Step Functions orchestration
- 15+ hotel chains
- OTA support (Booking.com, Expedia)
- Additional discount types
- Historical tracking
- ElastiCache or caching strategy
- Basic analytics
- User accounts
- EventBridge scheduling
- Fargate for long scrapes

### Phase 3: Advanced Analytics (3-5 weeks)
**Target:**
- Data lake (Athena + Glue)
- Trend analysis
- Price prediction
- Alert system
- Export functionality
- Public API

### Phase 4: Scale & Optimize (3-5 weeks)
**Target:**
- Performance optimization
- WAF security
- Proxy rotation
- CAPTCHA handling
- CI/CD pipeline
- Advanced monitoring (X-Ray)
- Multi-region (optional)

**Total Timeline:**
- Solo: 15-23 weeks (20-30% faster than traditional)
- Team: 10-14 weeks

---

## Technical Architecture Summary (AWS Serverless)

```
CloudFront (CDN) → S3 (Static React App)
         ↓
   API Gateway (REST)
         ↓
   ┌────┴────┬──────────┬───────────┐
   ↓         ↓          ↓           ↓
Search   Results   Analytics   User Mgmt
Lambda   Lambda    Lambda      Lambda
         ↓
   Step Functions
   (Orchestration)
         ↓
   Parallel Scraper Lambdas (1...N)
   + Fargate (for long tasks)
         ↓
   Aurora Serverless / DynamoDB
   + ElastiCache (Redis)
         ↓
   S3 (Raw data backup)
```

**Key Components:**
- **Frontend:** React SPA on S3/CloudFront
- **API:** API Gateway + Lambda functions
- **Orchestration:** Step Functions for complex workflows
- **Compute:** Lambda (fast tasks) + Fargate (long tasks)
- **Database:** Aurora Serverless v2 or DynamoDB
- **Caching:** ElastiCache Serverless (Redis)
- **Storage:** S3 for backups and exports
- **Auth:** Cognito user pools
- **Monitoring:** CloudWatch + X-Ray

---

## Outstanding Questions & Next Steps

### Questions Resolved ✅
1. **Technology preference?** ✅ AWS Serverless (Lambda, API Gateway, Step Functions, DynamoDB)
2. **Architecture approach?** ✅ Fully managed AWS services, no infrastructure management

### Questions to Resolve
1. **Budget constraints?** For proxies, CAPTCHA solving, infrastructure?
2. **Timeline?** When does the MVP need to be ready?
3. **Legal counsel?** Do you have access to legal advice for ToS compliance?
4. **Target audience?** Personal use, friends/family, public service, commercial?
5. **Monetization?** Free tool, freemium model, subscription?
6. **Development resources?** Solo developer, hiring developers, or using a team?
7. **AWS account?** Do you have an existing AWS account or need to create one?

### Planning Status ✅
- ✅ Requirements document complete
- ✅ Technology stack confirmed (AWS Serverless)
- ✅ Phase 1 (MVP) implementation plan complete
- ✅ Phase 2 (Enhanced) implementation plan complete
- ✅ Phase 3 (Analytics) implementation plan complete
- ✅ Phase 4 (Scale) implementation plan complete
- ✅ All code examples and templates provided

### Ready to Start Development

**Next Actions:**
1. **Set up AWS account** (if not already done)
2. **Configure development environment**
   - Install AWS CLI
   - Install AWS SAM CLI
   - Set up Python 3.11+ environment
   - Set up Node.js 18+ for frontend
3. **Initialize project repository**
   - Create Git repository
   - Set up project structure
   - Copy SAM templates from implementation plan
4. **Begin Phase 1 - Week 1**
   - AWS account setup
   - IAM configuration
   - Deploy initial infrastructure
5. **Follow implementation plan step-by-step**

### How to Begin
Choose one of these approaches:

**Approach 1: Start from scratch**
- Follow Phase 1 implementation plan exactly
- Build week by week
- Deploy to AWS incrementally

**Approach 2: Need help with specific component**
- Ask for detailed implementation of specific scraper
- Get help with specific Lambda function
- Troubleshoot specific AWS service

**Approach 3: Want to modify the plan**
- Adjust timeline or scope
- Change technology choices
- Add/remove features

---

## Database Schema (AWS Serverless Options)

### Option 1: DynamoDB (Recommended for MVP)
**Advantages:** Simpler, cheaper, scales automatically, perfect for key-value access
**Use when:** MVP/early stage, budget-conscious, simple queries

**Table Structure:**

**Hotels** (Primary Key: hotel_id)
```
hotel_id (PK)
name
chain
address
city, state, country
coordinates (lat/lon)
star_rating
amenities (Map)
gsi_chain_city (GSI on chain + city)
```

**Searches** (Primary Key: search_id, Sort Key: created_at)
```
search_id (PK)
created_at (SK)
user_id (GSI)
location
check_in_date
check_out_date
guests
filters (Map)
status
```

**Results** (Primary Key: result_id, Sort Key: scraped_at)
```
result_id (PK)
scraped_at (SK)
search_id (GSI)
hotel_id (GSI)
discount_type
original_price
discounted_price
taxes
fees
total_price
currency
available (Boolean)
raw_data (Map)
```

**Users** (Primary Key: user_id)
```
user_id (PK - from Cognito)
email
memberships (Map)
preferences (Map)
created_at
```

### Option 2: Aurora Serverless v2 (PostgreSQL)
**Advantages:** Complex queries, joins, analytics, SQL familiarity
**Use when:** Need complex analytics, many relationships, SQL required

**Table Structure:**

```sql
CREATE TABLE hotels (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    chain VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    star_rating DECIMAL(2, 1),
    amenities JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE searches (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255), -- Cognito user ID
    location VARCHAR(255),
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    guests INTEGER,
    filters JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE results (
    id UUID PRIMARY KEY,
    search_id UUID REFERENCES searches(id),
    hotel_id UUID REFERENCES hotels(id),
    discount_type VARCHAR(50),
    original_price DECIMAL(10, 2),
    discounted_price DECIMAL(10, 2),
    taxes DECIMAL(10, 2),
    fees DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    currency VARCHAR(3),
    available BOOLEAN,
    raw_data JSONB,
    scraped_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE discount_codes (
    id UUID PRIMARY KEY,
    code VARCHAR(100),
    type VARCHAR(50),
    hotel_chain VARCHAR(100),
    requirements TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY, -- Cognito user ID
    email VARCHAR(255) UNIQUE,
    memberships JSONB,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_results_search ON results(search_id);
CREATE INDEX idx_results_hotel ON results(hotel_id);
CREATE INDEX idx_results_scraped ON results(scraped_at DESC);
CREATE INDEX idx_hotels_chain_city ON hotels(chain, city);
CREATE INDEX idx_searches_user ON searches(user_id);
```

### Recommendation: Start with DynamoDB
- Lower cost for MVP ($10-50/month vs $45-150/month)
- Simpler to get started
- Scales automatically
- Perfect for key-value lookups
- Migrate to Aurora later if complex analytics needed

---

## Resources & References

### AWS Documentation
- AWS Lambda: https://docs.aws.amazon.com/lambda/
- API Gateway: https://docs.aws.amazon.com/apigateway/
- Step Functions: https://docs.aws.amazon.com/step-functions/
- DynamoDB: https://docs.aws.amazon.com/dynamodb/
- Aurora Serverless: https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html
- ElastiCache Serverless: https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/serverless.html
- AWS SAM: https://docs.aws.amazon.com/serverless-application-model/
- AWS CDK: https://docs.aws.amazon.com/cdk/
- Cognito: https://docs.aws.amazon.com/cognito/

### Frontend & Scraping
- React: https://react.dev/
- Playwright: https://playwright.dev/python/
- Tailwind CSS: https://tailwindcss.com/

### AWS Best Practices
- Serverless Application Lens: https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/
- Lambda Best Practices: https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html
- DynamoDB Best Practices: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html

### Infrastructure as Code
- SAM Examples: https://github.com/aws/aws-sam-cli-app-templates
- CDK Patterns: https://cdkpatterns.com/
- Serverless Patterns: https://serverlessland.com/patterns

### Scraping Best Practices
- Respect robots.txt
- Use user-agent headers
- Implement delays between requests
- Rotate IP addresses
- Handle CAPTCHAs gracefully
- Cache responses when appropriate

### Discount Programs to Support
1. AARP (American Association of Retired Persons)
2. AAA/CAA (Auto clubs)
3. Senior rates (various age tiers: 50+, 55+, 60+, 65+)
4. Military/Veterans
5. Government employees
6. Corporate codes
7. Student discounts
8. Promotional codes

---

## Risks & Mitigation Strategies

### High Risk Items
1. **Legal issues with scraping**
   - Mitigation: Legal review, API-first approach, partnerships
   
2. **IP blocking**
   - Mitigation: Proxy services, rate limiting, random delays

3. **Website changes breaking scrapers**
   - Mitigation: Modular design, automated tests, monitoring

### Medium Risk Items
1. **Performance at scale**
   - Mitigation: Horizontal scaling, caching, async processing

2. **Data accuracy**
   - Mitigation: Validation checks, user feedback

### Low Risk Items
1. **User adoption**
   - Mitigation: Clear value proposition, marketing

---

## Budget Summary (AWS Serverless)

### Development Costs
- Solo developer: 15-23 weeks total (25% faster vs traditional)
- Small team (2-3): 10-14 weeks total
- Estimated: $12,000-40,000 (consulting/freelance)
- **Savings:** 20-30% faster development = lower cost

### Monthly Operating Costs (AWS Serverless)
**Minimal usage (MVP/testing):**
- Lambda: $0-10
- API Gateway: $0-5
- DynamoDB: $10-20
- S3 + CloudFront: $5-15
- CloudWatch: $5-10
- **Total: $50-200/month**

**Moderate usage (100-500 searches/day):**
- Lambda: $20-50
- API Gateway: $10-20
- Step Functions: $5-10
- DynamoDB or Aurora: $50-150
- ElastiCache: $90-200 (or cache in Lambda/S3 for $5-20)
- S3 + CloudFront: $15-50
- Fargate: $20-100
- CloudWatch + other: $20-50
- Proxy services: $50-500
- **Total: $200-600/month**

**High usage (1000+ searches/day):**
- All services scaled up
- **Total: $500-1,500/month**

**First-Year Benefits:**
- AWS Free Tier: ~$500-1,000 savings
- No infrastructure management time
- Auto-scaling (no over-provisioning)

**Comparison:**
- Traditional infrastructure: $160-1,200/month + DevOps time
- Serverless: $50-600/month + zero infrastructure management
- **Savings: 40-70% on costs + 100% reduction in DevOps**

---

## Success Metrics

### KPIs to Track
- Scraping success rate (target: >95%)
- Average search completion time (<30 seconds)
- System uptime (>99%)
- Active users
- Searches per user per month
- Average savings per search
- User retention rate

---

## Prompt Templates for Continuing

### Starting a New Chat
*"I'm continuing work on the Travel Discount Comparison Tool project. Please read the 'Project Context & Continuation Guide' artifact which contains all requirements, decisions, and history. I'd like to [continue with implementation plan / work on database schema / build the MVP / etc.]"*

### Requesting Implementation Plan
*"Based on the approved requirements in the context document, please create a detailed implementation plan for Phase 1 (MVP). Break down tasks by week, include specific deliverables, and identify dependencies."*

### Technical Deep-Dive
*"I need detailed technical specifications for [component name] from the Travel Discount Comparison Tool project. Reference the requirements document and provide implementation details including code structure, API endpoints, and error handling."*

---

## Version History

### v1.0 - September 30, 2025
- Initial requirements document created
- Market research completed
- Architecture designed (traditional)
- 4-phase plan outlined
- Risk assessment completed
- Budget estimated

### v2.0 - September 30, 2025 (Current)
- Architecture pivoted to AWS Serverless
- Technology stack updated (Lambda, API Gateway, Step Functions, DynamoDB, etc.)
- Phase 1 MVP implementation plan created (4-6 weeks)
  - Week-by-week breakdown with code examples
  - SAM template specifications
  - Lambda function implementations
  - React frontend components
  - Testing and deployment procedures
- Phase 2 Enhanced Features plan created (5-7 weeks)
  - Step Functions orchestration
  - 15+ hotel chains
  - OTA support
  - User authentication
  - Historical tracking
  - Scheduled searches
- Phase 3 Advanced Analytics plan created (3-5 weeks)
  - Data lake setup (Athena + Glue)
  - ML price prediction models
  - Discount effectiveness scoring
  - Custom alerts and exports
- Phase 4 Scale & Optimize plan created (3-5 weeks)
  - Performance optimization
  - Security hardening (WAF, encryption)
  - CI/CD pipeline
  - Advanced monitoring (X-Ray)
  - Load testing

**Total Implementation Plans:** 15-23 weeks (solo) or 10-14 weeks (team)
**All artifacts complete and ready for development**

---

## Notes for Future Development

### Priority Features (Post-MVP)
- Email/SMS alerts for price drops
- Browser extension for quick lookups
- Mobile app
- Airline and car rental expansion
- AI price prediction
- Automatic rebooking

### Technologies to Explore
- Machine learning for price prediction (scikit-learn, TensorFlow)
- Natural language processing for parsing hotel descriptions
- Graph database for relationship mapping (Neo4j)
- Real-time updates with WebSockets
- Progressive Web App (PWA) capabilities

### Partnership Opportunities
- Hotel chains (official API access)
- Travel agencies
- Membership organizations (AARP, AAA)
- Credit card companies (travel benefits)

---

## Contact & Collaboration

### Repository Structure (AWS Serverless)
```
travel-discount-tool/
├── infrastructure/           # Infrastructure as Code
│   ├── sam-template.yaml    # AWS SAM template (or)
│   ├── cdk/                 # AWS CDK code
│   │   ├── stacks/
│   │   └── constructs/
│   └── scripts/
├── backend/
│   ├── lambdas/
│   │   ├── api/             # API Gateway handlers
│   │   │   ├── search.py
│   │   │   ├── results.py
│   │   │   └── analytics.py
│   │   ├── scrapers/        # Scraper functions
│   │   │   ├── marriott.py
│   │   │   ├── hilton.py
│   │   │   └── base.py
│   │   └── utilities/       # Shared utilities
│   ├── layers/              # Lambda layers
│   │   ├── playwright/
│   │   └── shared/
│   ├── stepfunctions/       # Step Function definitions
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/        # API clients
│   │   └── utils/
│   ├── public/
│   └── tests/
├── scripts/                 # Deployment scripts
│   ├── deploy.sh
│   └── setup-env.sh
└── docs/
    ├── api/
    ├── architecture/
    └── runbooks/
```

---

## Quick Reference

**Project Name:** Travel Discount Comparison Tool (working title)
**Architecture:** AWS Serverless (fully managed)
**Primary Goal:** Automate hotel discount comparison across memberships
**Target Users:** Travelers with AARP, AAA, or similar memberships
**Unique Value:** First tool to systematically compare membership discounts
**Timeline:** 15-23 weeks (solo) or 10-14 weeks (team)
**Budget:** $12-40K development + $50-600/month operations (moderate usage)

**Core AWS Services:**
- Lambda (compute)
- API Gateway (API)
- Step Functions (orchestration)
- DynamoDB or Aurora Serverless (database)
- S3 + CloudFront (frontend hosting)
- Cognito (auth)
- CloudWatch (monitoring)

**Key Benefits of Serverless:**
- 20-30% faster development
- 40-70% cost savings
- Zero infrastructure management
- Auto-scaling built-in
- High availability by default

---

**End of Context Document**

*This document should be referenced when continuing the project in a new chat session to maintain full context and avoid repetition.*