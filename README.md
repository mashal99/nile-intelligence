# Nile Intelligence

**Egyptian Real Estate Market Intelligence Platform**

A production-ready SaaS platform providing brokers, developers, and investors with market data, competitor monitoring, pricing trends, inventory tracking, and AI-powered business intelligence for the Egyptian real estate market.

## Architecture

```
nile-intelligence/
├── backend/          # Django + DRF API
│   ├── apps/
│   │   ├── accounts/      # User auth + JWT
│   │   ├── properties/    # Listings, compounds, developers
│   │   ├── market/        # Analytics, snapshots, insights
│   │   ├── monitoring/    # Alerts, rules, competitor tracking
│   │   ├── reports/       # PDF/Excel report generation
│   │   ├── ai_insights/   # Claude AI integration
│   │   └── subscriptions/ # Plans, billing, usage
│   ├── config/       # Settings (dev/prod)
│   └── core/         # Shared utils, middleware
├── frontend/         # Next.js 14 + TypeScript
│   └── src/
│       ├── app/      # App Router pages
│       ├── components/
│       └── lib/      # API client, utils
├── scrapers/         # Scrapy + Playwright
│   └── egyptian_real_estate/
│       └── spiders/  # Aqarmap, Nawy
├── docker/           # Dockerfiles
└── .github/workflows/ # CI/CD
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5 + DRF + JWT |
| Database | PostgreSQL 16 |
| Frontend | Next.js 14 + TypeScript + Tailwind |
| Background Jobs | Celery + Redis |
| Scraping | Scrapy + Playwright |
| AI | Anthropic Claude |
| Storage | AWS S3 |
| Infrastructure | Docker + AWS ECS |
| CI/CD | GitHub Actions |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### Development Setup

```bash
# 1. Clone and configure
git clone https://github.com/mashal99/nile-intelligence.git
cd nile-intelligence
cp .env.example .env
# Edit .env with your settings

# 2. Start infrastructure
docker-compose up postgres redis -d

# 3. Backend setup
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 4. Frontend setup (separate terminal)
cd frontend
npm install
npm run dev
```

### Full Docker Setup

```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- API: http://localhost:8000/api/v1
- Admin: http://localhost:8000/admin
- Celery Flower: http://localhost:5555

## Features

### Market Intelligence Dashboard
- Average price per area and property type
- Price trend charts (7/30/90/365 day)
- Inventory tracking by type
- Developer rankings and market share
- Area heat map (EGP/m²)

### Property Data Collection
- Scrapes Aqarmap.com and Nawy.com
- Automatic deduplication via fingerprinting
- Price change tracking
- Status history
- Runs every 4-6 hours via Celery Beat

### Competitor Monitoring
- User-defined alert rules
- Alerts for: new listings, price drops, price increases, new launches
- Email + in-app notifications
- Market event detection

### Reporting Engine
- PDF reports with charts (ReportLab)
- Excel exports (openpyxl)
- JSON data exports
- AI-generated executive summaries
- Scheduled automated reports

### AI Insights (Claude)
- Weekly market summaries
- Price movement explanations
- Investment opportunity identification
- Natural language market Q&A

### Subscriptions
| Feature | Free | Professional ($299/mo) | Enterprise ($999/mo) |
|---------|------|----------------------|---------------------|
| Listings/day | 50 | 500 | Unlimited |
| Reports/month | 2 | 20 | Unlimited |
| AI queries | 10 | 100 | Unlimited |
| Competitor alerts | ✗ | ✓ | ✓ |
| API access | ✗ | ✗ | ✓ |

## API

All endpoints under `/api/v1/`:

```
POST   /auth/register/
POST   /auth/login/
GET    /auth/me/

GET    /properties/
GET    /properties/{id}/
GET    /properties/areas/
GET    /properties/compounds/
GET    /properties/developers/

GET    /market/dashboard/
GET    /market/trends/{area_slug}/
GET    /market/heatmap/
GET    /market/developer-rankings/
GET    /market/insights/

POST   /monitoring/rules/
GET    /monitoring/alerts/
POST   /monitoring/alerts/read-all/

POST   /reports/
GET    /reports/{id}/download/

POST   /ai/generate/
POST   /ai/ask/

GET    /subscriptions/
POST   /subscriptions/upgrade/
```

## Deployment

### AWS ECS (Production)

See `.github/workflows/deploy.yml`. Requires:
- ECR repository
- ECS cluster `nile-intelligence`
- RDS PostgreSQL instance
- ElastiCache Redis
- S3 bucket for reports
- Secrets in GitHub repository settings

## License

MIT
