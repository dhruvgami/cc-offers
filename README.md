# Travel Discount Comparison Tool

Automated tool to compare hotel rates across multiple discount programs (AARP, AAA, senior, military, etc.).

## Project Structure

```
cc-offers/
├── backend/               # Python FastAPI backend
│   ├── api/              # API endpoints
│   ├── scrapers/         # Hotel website scrapers
│   ├── shared/           # Shared utilities, models, database
│   └── tests/            # Backend tests
├── frontend/             # React TypeScript frontend
├── data/                 # Local SQLite database
├── logs/                 # Application logs
├── instructions/         # Project documentation
└── docker-compose.yml    # Local development environment
```

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (for task queue)
- Git

### Backend Setup

**Quick Start (Recommended):**
```bash
cd backend
./run.sh
```

The `run.sh` script will automatically:
- Create virtual environment if needed
- Install all dependencies
- Install Playwright browser
- Initialize database with sample data
- Start the FastAPI server on http://localhost:8000

**Manual Setup:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Note:** The venv directory is not committed to Git. Run `./run.sh` to set it up automatically.

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Open browser: http://localhost:5173

## Technology Stack

### Local Development
- **Backend**: FastAPI (Python) + SQLite + Celery + Redis
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Scraping**: Playwright
- **Database**: SQLite (dev) / PostgreSQL (production)

### AWS Migration Path
- **Backend**: AWS Lambda + API Gateway
- **Database**: Aurora Serverless / DynamoDB
- **Queue**: SQS + Step Functions
- **Frontend**: S3 + CloudFront + Amplify
- **Auth**: Cognito
- **Monitoring**: CloudWatch

## Features

### Phase 1 (MVP - Current)
- ✅ 3-5 hotel chains (Marriott, Hilton, IHG)
- ✅ Discount testing (AARP, AAA, Senior)
- ✅ Search and comparison interface
- ✅ Local database storage

### Phase 2 (Future)
- 15+ hotel chains
- OTA support (Booking.com, Expedia)
- Historical data tracking
- User authentication
- Scheduled searches

## Environment Variables

Create `.env` file in backend directory:
```
DATABASE_URL=sqlite:///./data/travel_discounts.db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## API Endpoints

- `POST /api/search` - Initiate new hotel search
- `GET /api/results/{search_id}` - Get search results
- `GET /api/health` - Health check

## Development Notes

- Scrapers respect rate limits and robots.txt
- Local development uses SQLite for simplicity
- Production will use PostgreSQL-compatible Aurora
- All code is AWS-ready (can deploy with minimal changes)

## Legal Notice

Web scraping may violate website Terms of Service. Consult legal counsel before production deployment.

## License

Private project - All rights reserved
