# Travel Discount Comparison Tool - Implementation Plan

## Phase 1: MVP Implementation (4-6 weeks)

**Goal:** Build a working proof-of-concept that can scrape 3-5 hotel chains, test AARP/AAA/Senior discounts, and display results in a simple web interface.

---

## Week 1: AWS Foundation & Infrastructure Setup

### Day 1-2: AWS Account Setup & IAM Configuration

**Tasks:**
1. Create AWS account (or use existing)
2. Enable MFA on root account
3. Create IAM users and roles:
   - Developer user (with appropriate permissions)
   - Lambda execution role (basic)
   - API Gateway execution role
4. Set up AWS CLI and configure profiles
5. Enable AWS CloudTrail for auditing
6. Set up billing alerts ($50, $100, $200 thresholds)

**IAM Policies Needed:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "apigateway:*",
        "dynamodb:*",
        "s3:*",
        "cloudfront:*",
        "cognito-idp:*",
        "cloudwatch:*",
        "logs:*",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

**Deliverables:**
- AWS account configured with security best practices
- IAM roles and policies documented
- AWS CLI configured locally
- Billing alerts active

---

### Day 3-5: Infrastructure as Code Setup

**Choose IaC Tool:**
- **AWS SAM** (recommended for beginners, simpler)
- **AWS CDK** (recommended for complex projects, more flexibility)

**For SAM approach:**

1. Install AWS SAM CLI:
```bash
pip install aws-sam-cli
```

2. Initialize project structure:
```bash
sam init --name travel-discount-tool --runtime python3.11 --architecture x86_64
```

3. Create base SAM template (`template.yaml`):
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Travel Discount Comparison Tool

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: python3.11
    Environment:
      Variables:
        STAGE: dev
        DYNAMODB_TABLE: !Ref HotelsTable

Resources:
  # DynamoDB Tables
  HotelsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub '${AWS::StackName}-hotels'
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: hotel_id
          AttributeType: S
        - AttributeName: chain
          AttributeType: S
        - AttributeName: city
          AttributeType: S
      KeySchema:
        - AttributeName: hotel_id
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: chain-city-index
          KeySchema:
            - AttributeName: chain
              KeyType: HASH
            - AttributeName: city
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

  SearchesTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub '${AWS::StackName}-searches'
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: search_id
          AttributeType: S
        - AttributeName: created_at
          AttributeType: S
        - AttributeName: user_id
          AttributeType: S
      KeySchema:
        - AttributeName: search_id
          KeyType: HASH
        - AttributeName: created_at
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: user-index
          KeySchema:
            - AttributeName: user_id
              KeyType: HASH
            - AttributeName: created_at
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

  ResultsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub '${AWS::StackName}-results'
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: result_id
          AttributeType: S
        - AttributeName: scraped_at
          AttributeType: S
        - AttributeName: search_id
          AttributeType: S
        - AttributeName: hotel_id
          AttributeType: S
      KeySchema:
        - AttributeName: result_id
          KeyType: HASH
        - AttributeName: scraped_at
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: search-index
          KeySchema:
            - AttributeName: search_id
              KeyType: HASH
            - AttributeName: scraped_at
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
        - IndexName: hotel-index
          KeySchema:
            - AttributeName: hotel_id
              KeyType: HASH
            - AttributeName: scraped_at
              KeyType: RANGE
          Projection:
            ProjectionType: ALL

  # API Gateway
  TravelDiscountApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: dev
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: "'*'"
      Auth:
        DefaultAuthorizer: NONE

  # Lambda Functions
  SearchFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: backend/lambdas/api/
      Handler: search.handler
      Events:
        SearchApi:
          Type: Api
          Properties:
            RestApiId: !Ref TravelDiscountApi
            Path: /search
            Method: POST
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref SearchesTable

  ResultsFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: backend/lambdas/api/
      Handler: results.handler
      Events:
        ResultsApi:
          Type: Api
          Properties:
            RestApiId: !Ref TravelDiscountApi
            Path: /results/{search_id}
            Method: GET
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref ResultsTable

  # S3 Bucket for Frontend
  FrontendBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${AWS::StackName}-frontend'
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: index.html
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false

  FrontendBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref FrontendBucket
      PolicyDocument:
        Statement:
          - Sid: PublicReadGetObject
            Effect: Allow
            Principal: '*'
            Action: 's3:GetObject'
            Resource: !Sub '${FrontendBucket.Arn}/*'

Outputs:
  ApiUrl:
    Description: API Gateway URL
    Value: !Sub 'https://${TravelDiscountApi}.execute-api.${AWS::Region}.amazonaws.com/dev'
  
  FrontendBucketUrl:
    Description: Frontend S3 Website URL
    Value: !GetAtt FrontendBucket.WebsiteURL
```

4. Create local development environment file (`.env`):
```bash
AWS_REGION=us-east-1
STAGE=dev
LOG_LEVEL=INFO
```

**Deliverables:**
- Complete SAM template or CDK stack
- Project structure initialized
- DynamoDB tables defined
- API Gateway configuration
- S3 bucket for frontend
- Documentation on deployment commands

---

## Week 2: Backend Development - Core Lambda Functions

### Day 1-3: API Lambda Functions

**Directory Structure:**
```
backend/
├── lambdas/
│   ├── api/
│   │   ├── search.py           # Handle search requests
│   │   ├── results.py          # Retrieve results
│   │   └── requirements.txt
│   ├── scrapers/
│   │   ├── base.py             # Base scraper class
│   │   ├── marriott.py         # Marriott scraper
│   │   ├── hilton.py           # Hilton scraper
│   │   ├── ihg.py              # IHG scraper
│   │   └── requirements.txt
│   └── shared/
│       ├── models.py           # Data models
│       ├── database.py         # DynamoDB client
│       └── utils.py
```

**1. Create shared utilities (`backend/lambdas/shared/database.py`):**
```python
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import uuid
import os

dynamodb = boto3.resource('dynamodb')

class DynamoDBClient:
    def __init__(self):
        self.hotels_table = dynamodb.Table(os.environ['HOTELS_TABLE'])
        self.searches_table = dynamodb.Table(os.environ['SEARCHES_TABLE'])
        self.results_table = dynamodb.Table(os.environ['RESULTS_TABLE'])
    
    def create_search(self, user_id, location, check_in, check_out, guests, filters=None):
        search_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'search_id': search_id,
            'created_at': timestamp,
            'user_id': user_id or 'anonymous',
            'location': location,
            'check_in_date': check_in,
            'check_out_date': check_out,
            'guests': guests,
            'filters': filters or {},
            'status': 'pending'
        }
        
        self.searches_table.put_item(Item=item)
        return search_id
    
    def update_search_status(self, search_id, status):
        self.searches_table.update_item(
            Key={'search_id': search_id},
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': status}
        )
    
    def save_result(self, search_id, hotel_id, discount_type, prices, available=True):
        result_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'result_id': result_id,
            'scraped_at': timestamp,
            'search_id': search_id,
            'hotel_id': hotel_id,
            'discount_type': discount_type,
            'original_price': prices.get('original'),
            'discounted_price': prices.get('discounted'),
            'taxes': prices.get('taxes', 0),
            'fees': prices.get('fees', 0),
            'total_price': prices.get('total'),
            'currency': prices.get('currency', 'USD'),
            'available': available
        }
        
        self.results_table.put_item(Item=item)
        return result_id
    
    def get_results_by_search(self, search_id):
        response = self.results_table.query(
            IndexName='search-index',
            KeyConditionExpression=Key('search_id').eq(search_id)
        )
        return response.get('Items', [])
```

**2. Create search API handler (`backend/lambdas/api/search.py`):**
```python
import json
import os
from shared.database import DynamoDBClient

db = DynamoDBClient()

def handler(event, context):
    """
    Handle POST /search request
    
    Expected body:
    {
        "location": "New York, NY",
        "check_in": "2025-12-01",
        "check_out": "2025-12-03",
        "guests": 2,
        "discount_types": ["aarp", "aaa", "senior"]
    }
    """
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Validate required fields
        required = ['location', 'check_in', 'check_out', 'guests']
        for field in required:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        # Get user ID from auth (if implemented) or use anonymous
        user_id = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub')
        
        # Create search record
        search_id = db.create_search(
            user_id=user_id,
            location=body['location'],
            check_in=body['check_in'],
            check_out=body['check_out'],
            guests=body['guests'],
            filters=body.get('filters', {})
        )
        
        # TODO: Trigger Step Function or invoke scraper Lambdas
        # For MVP, we'll invoke scrapers synchronously (not ideal, but simpler)
        
        return {
            'statusCode': 202,  # Accepted
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'search_id': search_id,
                'status': 'pending',
                'message': 'Search initiated. Use /results/{search_id} to check progress.'
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
```

**3. Create results API handler (`backend/lambdas/api/results.py`):**
```python
import json
from shared.database import DynamoDBClient

db = DynamoDBClient()

def handler(event, context):
    """
    Handle GET /results/{search_id} request
    """
    
    try:
        # Get search_id from path parameters
        search_id = event.get('pathParameters', {}).get('search_id')
        
        if not search_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing search_id'})
            }
        
        # Retrieve results
        results = db.get_results_by_search(search_id)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'search_id': search_id,
                'count': len(results),
                'results': results
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
```

**Deliverables:**
- Working API Lambda functions for search and results
- DynamoDB client library
- Basic error handling
- CORS headers configured
- Unit tests (optional for MVP)

---

### Day 4-5: Deploy and Test API

**Deployment:**
```bash
# Build and package
sam build

# Deploy
sam deploy --guided \
  --stack-name travel-discount-dev \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

**Testing:**
```bash
# Get API URL from outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name travel-discount-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

# Test search endpoint
curl -X POST "${API_URL}/search" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "New York, NY",
    "check_in": "2025-12-01",
    "check_out": "2025-12-03",
    "guests": 2
  }'

# Test results endpoint (use search_id from previous response)
curl "${API_URL}/results/{search_id}"
```

**Deliverables:**
- Deployed API to AWS
- API URL documented
- Basic integration tests passed
- CloudWatch logs configured

---

## Week 3: Web Scraping Development

### Day 1-2: Set Up Playwright in Lambda

**Challenge:** Lambda doesn't include Chromium by default. We need to create a Lambda Layer with Playwright.

**Solution 1: Use Pre-built Layer**
```bash
# Use AWS Lambda Playwright layer (community)
# Add to SAM template:
```

```yaml
ScraperFunction:
  Type: AWS::Serverless::Function
  Properties:
    Layers:
      - arn:aws:lambda:us-east-1:764866452798:layer:chrome-aws-lambda:31
      - arn:aws:lambda:us-east-1:764866452798:layer:playwright:1
```

**Solution 2: Build Custom Layer (Recommended)**

1. Create layer directory:
```bash
mkdir -p layers/playwright/python
cd layers/playwright
```

2. Install Playwright and dependencies:
```bash
pip install playwright -t python/
python -m playwright install chromium
```

3. Create layer zip:
```bash
zip -r playwright-layer.zip python/
```

4. Upload to Lambda:
```bash
aws lambda publish-layer-version \
  --layer-name playwright-chromium \
  --zip-file fileb://playwright-layer.zip \
  --compatible-runtimes python3.11
```

**Deliverables:**
- Playwright Lambda layer created and uploaded
- Test Lambda function verifying Playwright works
- Documentation on layer ARN

---

### Day 3-5: Implement Hotel Scrapers

**Base Scraper Class (`backend/lambdas/scrapers/base.py`):**
```python
from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright
import json

class BaseScraper(ABC):
    """Base class for hotel scrapers"""
    
    def __init__(self, check_in, check_out, guests, location):
        self.check_in = check_in
        self.check_out = check_out
        self.guests = guests
        self.location = location
        self.browser = None
        self.context = None
        self.page = None
    
    def setup_browser(self):
        """Initialize Playwright browser"""
        playwright = sync_playwright().start()
        
        # Launch browser in headless mode
        self.browser = playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        # Create context with realistic settings
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        self.page = self.context.new_page()
    
    def teardown_browser(self):
        """Clean up browser resources"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
    
    @abstractmethod
    def get_search_url(self):
        """Return the search URL for this hotel chain"""
        pass
    
    @abstractmethod
    def apply_discount(self, discount_type):
        """Apply discount code on the page"""
        pass
    
    @abstractmethod
    def extract_prices(self):
        """Extract price information from the page"""
        pass
    
    def scrape(self, discount_types=['none', 'aarp', 'aaa', 'senior']):
        """Main scraping method"""
        results = []
        
        try:
            self.setup_browser()
            
            for discount_type in discount_types:
                # Navigate to search page
                url = self.get_search_url()
                self.page.goto(url, wait_until='networkidle')
                
                # Apply discount if specified
                if discount_type != 'none':
                    self.apply_discount(discount_type)
                    self.page.wait_for_load_state('networkidle')
                
                # Extract prices
                prices = self.extract_prices()
                
                results.append({
                    'discount_type': discount_type,
                    'prices': prices,
                    'available': prices is not None
                })
                
                # Add delay to avoid detection
                self.page.wait_for_timeout(2000)
            
            return results
        
        except Exception as e:
            print(f"Scraping error: {str(e)}")
            return []
        
        finally:
            self.teardown_browser()
```

**Marriott Scraper (`backend/lambdas/scrapers/marriott.py`):**
```python
from .base import BaseScraper
from urllib.parse import quote

class MarriottScraper(BaseScraper):
    """Scraper for Marriott hotels"""
    
    CHAIN_NAME = "Marriott"
    BASE_URL = "https://www.marriott.com"
    
    def get_search_url(self):
        """Build Marriott search URL"""
        # Example URL structure (adjust based on actual Marriott URL format)
        location_encoded = quote(self.location)
        url = (
            f"{self.BASE_URL}/search/default.mi?"
            f"destinationAddress={location_encoded}"
            f"&fromDate={self.check_in}"
            f"&toDate={self.check_out}"
            f"&numRooms=1"
            f"&numberOfGuests={self.guests}"
        )
        return url
    
    def apply_discount(self, discount_type):
        """Apply discount code for Marriott"""
        discount_codes = {
            'aarp': 'ZA9',  # Marriott AARP code
            'aaa': 'ZAA',   # Marriott AAA code
            'senior': 'ZA9'  # Senior rate
        }
        
        code = discount_codes.get(discount_type)
        if not code:
            return
        
        try:
            # Click on "Special Rates" or similar button
            self.page.click('button[aria-label="Special Rates"]', timeout=5000)
            
            # Enter discount code
            self.page.fill('input[name="corporateCode"]', code)
            
            # Click apply
            self.page.click('button[type="submit"]')
            
            # Wait for results to update
            self.page.wait_for_timeout(3000)
        
        except Exception as e:
            print(f"Error applying discount {discount_type}: {str(e)}")
    
    def extract_prices(self):
        """Extract price information from Marriott page"""
        try:
            # Wait for price elements to load
            self.page.wait_for_selector('.room-rate', timeout=10000)
            
            # Extract first available room price
            # (Adjust selectors based on actual Marriott HTML structure)
            price_element = self.page.query_selector('.room-rate .price')
            
            if not price_element:
                return None
            
            price_text = price_element.inner_text()
            
            # Parse price (e.g., "$199.00")
            price = float(price_text.replace('$', '').replace(',', ''))
            
            # Extract taxes if available
            taxes_element = self.page.query_selector('.taxes-fees')
            taxes = 0
            if taxes_element:
                taxes_text = taxes_element.inner_text()
                taxes = float(taxes_text.replace('$', '').replace(',', ''))
            
            return {
                'original': price,
                'discounted': price,
                'taxes': taxes,
                'fees': 0,
                'total': price + taxes,
                'currency': 'USD'
            }
        
        except Exception as e:
            print(f"Error extracting prices: {str(e)}")
            return None

def handler(event, context):
    """Lambda handler for Marriott scraper"""
    
    # Parse input
    check_in = event.get('check_in')
    check_out = event.get('check_out')
    guests = event.get('guests', 2)
    location = event.get('location')
    discount_types = event.get('discount_types', ['none', 'aarp', 'aaa'])
    
    # Initialize scraper
    scraper = MarriottScraper(check_in, check_out, guests, location)
    
    # Execute scraping
    results = scraper.scrape(discount_types)
    
    return {
        'statusCode': 200,
        'body': {
            'chain': 'Marriott',
            'results': results
        }
    }
```

**Note:** The above scrapers are examples. Actual implementation will require:
1. Reverse-engineering hotel websites
2. Finding correct CSS selectors
3. Handling dynamic content loading
4. Managing CAPTCHA challenges
5. Respecting rate limits

**Deliverables:**
- Base scraper class
- Marriott scraper implemented
- Hilton scraper implemented
- IHG scraper implemented
- Scrapers tested locally
- Lambda functions deployed

---

### Day 6-7: Integration and Testing

**Modify Search API to Invoke Scrapers:**

Update `search.py` to invoke scraper Lambdas:
```python
import boto3

lambda_client = boto3.client('lambda')

# After creating search record, invoke scrapers
scrapers = ['MarriottScraperFunction', 'HiltonScraperFunction', 'IHGScraperFunction']

for scraper in scrapers:
    payload = {
        'search_id': search_id,
        'check_in': body['check_in'],
        'check_out': body['check_out'],
        'guests': body['guests'],
        'location': body['location'],
        'discount_types': body.get('discount_types', ['none', 'aarp', 'aaa'])
    }
    
    # Invoke asynchronously
    lambda_client.invoke(
        FunctionName=scraper,
        InvocationType='Event',  # Async
        Payload=json.dumps(payload)
    )
```

**Update Scraper to Save Results:**
```python
from shared.database import DynamoDBClient

db = DynamoDBClient()

# After scraping, save results
for result in results:
    db.save_result(
        search_id=event['search_id'],
        hotel_id=f"{CHAIN_NAME}-{location}",  # Generate hotel ID
        discount_type=result['discount_type'],
        prices=result['prices'],
        available=result['available']
    )

# Update search status
db.update_search_status(event['search_id'], 'completed')
```

**Deliverables:**
- End-to-end integration working
- Search → Scrape → Store → Retrieve flow functional
- CloudWatch logs showing successful executions

---

## Week 4: Frontend Development

### Day 1-2: React Application Setup

**Initialize React Project:**
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```

**Install Dependencies:**
```bash
npm install \
  @tanstack/react-query \
  axios \
  zustand \
  react-router-dom \
  date-fns \
  recharts \
  @headlessui/react \
  @heroicons/react
```

**Project Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── SearchForm.tsx
│   │   ├── ResultsTable.tsx
│   │   └── LoadingSpinner.tsx
│   ├── pages/
│   │   ├── Home.tsx
│   │   └── Results.tsx
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── public/
└── index.html
```

**API Service (`src/services/api.ts`):**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://your-api-url.com/dev';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SearchRequest {
  location: string;
  check_in: string;
  check_out: string;
  guests: number;
  discount_types?: string[];
}

export interface SearchResponse {
  search_id: string;
  status: string;
  message: string;
}

export interface Result {
  result_id: string;
  hotel_id: string;
  discount_type: string;
  original_price: number;
  discounted_price: number;
  taxes: number;
  fees: number;
  total_price: number;
  currency: string;
  available: boolean;
}

export interface ResultsResponse {
  search_id: string;
  count: number;
  results: Result[];
}

export const searchHotels = async (request: SearchRequest): Promise<SearchResponse> => {
  const response = await api.post<SearchResponse>('/search', request);
  return response.data;
};

export const getResults = async (searchId: string): Promise<ResultsResponse> => {
  const response = await api.get<ResultsResponse>(`/results/${searchId}`);
  return response.data;
};
```

**Deliverables:**
- React project initialized with TypeScript
- API client configured
- Basic routing setup
- Type definitions

---

### Day 3-4: Build UI Components

**Search Form Component:**
```typescript
// src/components/SearchForm.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchHotels } from '../services/api';

export const SearchForm: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    location: '',
    check_in: '',
    check_out: '',
    guests: 2,
    discount_types: ['aarp', 'aaa', 'senior'],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await searchHotels(formData);
      navigate(`/results/${response.search_id}`);
    } catch (error) {
      console.error('Search failed:', error);
      alert('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">Search Hotel Discounts</h2>
      
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Location</label>
        <input
          type="text"
          value={formData.location}
          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          placeholder="City or Hotel Name"
          className="w-full p-2 border rounded"
          required
        />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium mb-2">Check-in</label>
          <input
            type="date"
            value={formData.check_in}
            onChange={(e) => setFormData({ ...formData, check_in: e.target.value })}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Check-out</label>
          <input
            type="date"
            value={formData.check_out}
            onChange={(e) => setFormData({ ...formData, check_out: e.target.value })}
            className="w-full p-2 border rounded"
            required
          />
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">Guests</label>
        <input
          type="number"
          value={formData.guests}
          onChange={(e) => setFormData({ ...formData, guests: parseInt(e.target.value) })}
          min="1"
          max="10"
          className="w-full p-2 border rounded"
        />
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Discount Types</label>
        <div className="space-y-2">
          {['AARP', 'AAA', 'Senior'].map((type) => (
            <label key={type} className="flex items-center">
              <input
                type="checkbox"
                checked={formData.discount_types.includes(type.toLowerCase())}
                onChange={(e) => {
                  const types = e.target.checked
                    ? [...formData.discount_types, type.toLowerCase()]
                    : formData.discount_types.filter((t) => t !== type.toLowerCase());
                  setFormData({ ...formData, discount_types: types });
                }}
                className="mr-2"
              />
              {type}
            </label>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
      >
        {loading ? 'Searching...' : 'Search Hotels'}
      </button>
    </form>
  );
};
```

**Results Table Component:**
```typescript
// src/components/ResultsTable.tsx
import React from 'react';
import { Result } from '../services/api';

interface ResultsTableProps {
  results: Result[];
}

export const ResultsTable: React.FC<ResultsTableProps> = ({ results }) => {
  if (results.length === 0) {
    return <div className="text-center py-8">No results found.</div>;
  }

  // Group by hotel
  const grouped = results.reduce((acc, result) => {
    if (!acc[result.hotel_id]) {
      acc[result.hotel_id] = [];
    }
    acc[result.hotel_id].push(result);
    return acc;
  }, {} as Record<string, Result[]>);

  return (
    <div className="space-y-6">
      {Object.entries(grouped).map(([hotelId, hotelResults]) => (
        <div key={hotelId} className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">{hotelId}</h3>
          
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Discount Type</th>
                <th className="text-right p-2">Price</th>
                <th className="text-right p-2">Taxes</th>
                <th className="text-right p-2">Total</th>
                <th className="text-right p-2">Savings</th>
              </tr>
            </thead>
            <tbody>
              {hotelResults.map((result) => {
                const basePrice = hotelResults.find((r) => r.discount_type === 'none')?.total_price || result.total_price;
                const savings = basePrice - result.total_price;
                
                return (
                  <tr key={result.result_id} className="border-b">
                    <td className="p-2 font-medium capitalize">{result.discount_type}</td>
                    <td className="text-right p-2">${result.discounted_price.toFixed(2)}</td>
                    <td className="text-right p-2">${result.taxes.toFixed(2)}</td>
                    <td className="text-right p-2 font-bold">${result.total_price.toFixed(2)}</td>
                    <td className="text-right p-2 text-green-600">
                      {savings > 0 ? `-$${savings.toFixed(2)}` : '-'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
};
```

**Deliverables:**
- Search form component
- Results table component
- Loading states
- Error handling
- Responsive design with Tailwind

---

### Day 5: Integrate and Test

**Results Page (`src/pages/Results.tsx`):**
```typescript
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getResults, ResultsResponse } from '../services/api';
import { ResultsTable } from '../components/ResultsTable';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Results: React.FC = () => {
  const { searchId } = useParams<{ searchId: string }>();
  const [data, setData] = useState<ResultsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      if (!searchId) return;

      try {
        const response = await getResults(searchId);
        setData(response);
      } catch (err) {
        setError('Failed to load results');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
    
    // Poll for results if status is pending
    const interval = setInterval(fetchResults, 5000);
    
    return () => clearInterval(interval);
  }, [searchId]);

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="text-red-600 text-center">{error}</div>;
  if (!data) return <div>No data</div>;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Search Results</h1>
      <p className="mb-4 text-gray-600">Found {data.count} results</p>
      <ResultsTable results={data.results} />
    </div>
  );
};
```

**Deploy Frontend to S3:**
```bash
# Build
npm run build

# Deploy to S3
aws s3 sync dist/ s3://your-frontend-bucket/ --delete

# Invalidate CloudFront (if using)
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

**Deliverables:**
- Complete frontend application
- Deployed to S3
- Working end-to-end flow
- Responsive design tested

---

## Week 5-6: Testing, Documentation, and Refinement

### Week 5: Testing

**Tasks:**
1. **Integration Testing**
   - Test search flow end-to-end
   - Verify all discount types work
   - Test error scenarios (invalid dates, missing fields)
   
2. **Scraper Testing**
   - Test each hotel chain scraper individually
   - Verify price extraction accuracy
   - Test discount code application
   - Handle edge cases (no availability, price changes)

3. **Performance Testing**
   - Measure Lambda cold starts
   - Test concurrent searches
   - Monitor DynamoDB read/write capacity
   - Check API Gateway response times

4. **Security Testing**
   - Test CORS configuration
   - Verify input validation
   - Check for injection vulnerabilities
   - Review IAM permissions (principle of least privilege)

**Deliverables:**
- Test plan document
- Test results and bug reports
- Performance benchmarks
- Security audit report

---

### Week 6: Documentation and Polish

**Tasks:**
1. **Documentation**
   - API documentation (OpenAPI/Swagger)
   - Deployment guide
   - Architecture diagram
   - Operations runbook
   - User guide

2. **Monitoring Setup**
   - CloudWatch dashboards
   - Alarms for errors and latency
   - Cost monitoring alerts

3. **Code Cleanup**
   - Remove debug code
   - Add comments
   - Refactor duplicate code
   - Update README

4. **MVP Demo**
   - Prepare demo presentation
   - Create demo video
   - Showcase key features

**Deliverables:**
- Complete documentation
- Monitoring dashboards
- Clean, commented code
- MVP ready for demonstration

---

## Success Criteria for Phase 1 MVP

✅ **Functional Requirements Met:**
- Users can search for hotels by location and dates
- System scrapes 3-5 hotel chains
- Tests AARP, AAA, and senior discounts
- Displays results in a clear table
- Shows price comparisons and savings
- Stores results in DynamoDB

✅ **Technical Requirements Met:**
- Deployed to AWS using serverless architecture
- API Gateway + Lambda functions working
- DynamoDB storing data
- Frontend hosted on S3
- CloudWatch logging enabled
- Infrastructure as Code (SAM/CDK)

✅ **Performance Targets:**
- Search completes in < 60 seconds
- API response time < 3 seconds
- Frontend loads in < 2 seconds
- 95%+ scraping success rate

✅ **Documentation:**
- Architecture documented
- API documented
- Deployment guide complete
- Operations runbook ready

---

## Phase 1 Budget Estimate

**AWS Costs (MVP with light testing):**
- Lambda: $5-10
- API Gateway: $2-5
- DynamoDB: $5-10
- S3 + CloudFront: $3-5
- CloudWatch: $2-3
- **Total: $20-35/month**

**Development Time:**
- Solo developer: 4-6 weeks
- Pair: 3-4 weeks

**Next Steps After MVP:**
- Proceed to Phase 2: Enhanced Features
- Add more hotel chains
- Implement Step Functions
- Add user authentication
- Historical data tracking
- Basic analytics

---

## Risks and Mitigation

**High Priority Risks:**

1. **Website Structure Changes**
   - Risk: Hotel websites change, breaking scrapers
   - Mitigation: Modular scraper design, automated testing

2. **IP Blocking**
   - Risk: Hotels block Lambda IPs
   - Mitigation: Add delays, rotate IPs in Phase 2

3. **CAPTCHA Challenges**
   - Risk: Websites implement CAPTCHA
   - Mitigation: Manual fallback, CAPTCHA solving service in Phase 2

4. **Lambda Timeouts**
   - Risk: Scraping takes > 15 minutes (Lambda limit)
   - Mitigation: Use Fargate for long-running scrapes in Phase 2

**Medium Priority Risks:**

1. **Data Accuracy**
   - Risk: Extracted prices incorrect
   - Mitigation: Validation checks, user feedback

2. **Cost Overruns**
   - Risk: AWS costs higher than expected
   - Mitigation: Set billing alarms, monitor usage

---

## Tools and Resources

**Development Tools:**
- VS Code or PyCharm
- AWS CLI
- AWS SAM CLI or CDK
- Postman (API testing)
- Docker (local testing)

**AWS Services Dashboard:**
- CloudWatch Logs: Monitor Lambda execution
- CloudWatch Metrics: Track performance
- DynamoDB Console: View stored data
- S3 Console: Manage frontend files
- Lambda Console: Update functions

**Helpful Links:**
- AWS SAM Docs: https://docs.aws.amazon.com/serverless-application-model/
- Playwright Docs: https://playwright.dev/python/
- React Docs: https://react.dev/

---

**End of Phase 1 Implementation Plan**

This plan provides a solid foundation for building the MVP. Once Phase 1 is complete, we can proceed to Phase 2 with more advanced features like Step Functions, more hotel chains, user authentication, and historical analytics.