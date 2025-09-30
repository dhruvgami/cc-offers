# Travel Discount Comparison Tool - Phases 2-4 Implementation

## Phase 2: Enhanced Features (5-7 weeks)

**Goal:** Scale to 15+ hotel chains, add workflow orchestration, implement historical tracking, and user accounts.

---

## Week 1: Step Functions Workflow Orchestration

### Why Step Functions?
- **Problem with MVP:** Lambda invokes scrapers sequentially or uses Event invocations without coordination
- **Solution:** Step Functions orchestrates complex workflows with parallel execution, error handling, and retry logic

### Day 1-2: Design Workflow

**Workflow Steps:**
```
1. ValidateSearch (Lambda)
   ↓
2. FindHotels (Lambda) - Query hotel database by location
   ↓
3. ParallelScraping (Parallel State)
   ├─ ScrapeMarriott (Lambda)
   ├─ ScrapeHilton (Lambda)
   ├─ ScrapeIHG (Lambda)
   ├─ ScrapeBestWestern (Lambda)
   └─ ScrapeHyatt (Lambda)
   ↓
4. AggregateResults (Lambda)
   ↓
5. SaveToDatabase (Lambda)
   ↓
6. NotifyUser (Lambda) - Send email/notification
```

**Step Functions Definition (ASL - Amazon States Language):**
```json
{
  "Comment": "Hotel Discount Search Workflow",
  "StartAt": "ValidateSearch",
  "States": {
    "ValidateSearch": {
      "Type": "Task",
      "Resource": "${ValidateSearchFunctionArn}",
      "Retry": [
        {
          "ErrorEquals": ["States.TaskFailed"],
          "IntervalSeconds": 2,
          "MaxAttempts": 2,
          "BackoffRate": 2.0
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "HandleError",
          "ResultPath": "$.error"
        }
      ],
      "Next": "FindHotels"
    },
    "FindHotels": {
      "Type": "Task",
      "Resource": "${FindHotelsFunctionArn}",
      "Next": "CheckHotelsFound"
    },
    "CheckHotelsFound": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.hotelCount",
          "NumericGreaterThan": 0,
          "Next": "ParallelScraping"
        }
      ],
      "Default": "NoHotelsFound"
    },
    "ParallelScraping": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "ScrapeMarriott",
          "States": {
            "ScrapeMarriott": {
              "Type": "Task",
              "Resource": "${MarriottScraperArn}",
              "Retry": [
                {
                  "ErrorEquals": ["States.TaskFailed"],
                  "IntervalSeconds": 5,
                  "MaxAttempts": 3,
                  "BackoffRate": 2.0
                }
              ],
              "Catch": [
                {
                  "ErrorEquals": ["States.ALL"],
                  "ResultPath": "$.error",
                  "Next": "MarriottFailed"
                }
              ],
              "End": true
            },
            "MarriottFailed": {
              "Type": "Pass",
              "Result": {"status": "failed", "chain": "Marriott"},
              "End": true
            }
          }
        },
        {
          "StartAt": "ScrapeHilton",
          "States": {
            "ScrapeHilton": {
              "Type": "Task",
              "Resource": "${HiltonScraperArn}",
              "Retry": [
                {
                  "ErrorEquals": ["States.TaskFailed"],
                  "IntervalSeconds": 5,
                  "MaxAttempts": 3,
                  "BackoffRate": 2.0
                }
              ],
              "Catch": [
                {
                  "ErrorEquals": ["States.ALL"],
                  "ResultPath": "$.error",
                  "Next": "HiltonFailed"
                }
              ],
              "End": true
            },
            "HiltonFailed": {
              "Type": "Pass",
              "Result": {"status": "failed", "chain": "Hilton"},
              "End": true
            }
          }
        }
      ],
      "ResultPath": "$.scrapingResults",
      "Next": "AggregateResults"
    },
    "AggregateResults": {
      "Type": "Task",
      "Resource": "${AggregateResultsFunctionArn}",
      "Next": "SaveToDatabase"
    },
    "SaveToDatabase": {
      "Type": "Task",
      "Resource": "${SaveToDatabaseFunctionArn}",
      "Next": "NotifyUser"
    },
    "NotifyUser": {
      "Type": "Task",
      "Resource": "${NotifyUserFunctionArn}",
      "End": true
    },
    "NoHotelsFound": {
      "Type": "Fail",
      "Error": "NoHotelsFound",
      "Cause": "No hotels found in specified location"
    },
    "HandleError": {
      "Type": "Task",
      "Resource": "${HandleErrorFunctionArn}",
      "Next": "WorkflowFailed"
    },
    "WorkflowFailed": {
      "Type": "Fail",
      "Error": "WorkflowFailed",
      "Cause": "Workflow execution failed"
    }
  }
}
```

**Add to SAM Template:**
```yaml
SearchWorkflow:
  Type: AWS::Serverless::StateMachine
  Properties:
    Name: !Sub '${AWS::StackName}-search-workflow'
    DefinitionUri: stepfunctions/search-workflow.asl.json
    DefinitionSubstitutions:
      ValidateSearchFunctionArn: !GetAtt ValidateSearchFunction.Arn
      FindHotelsFunctionArn: !GetAtt FindHotelsFunction.Arn
      MarriottScraperArn: !GetAtt MarriottScraperFunction.Arn
      HiltonScraperArn: !GetAtt HiltonScraperFunction.Arn
      AggregateResultsFunctionArn: !GetAtt AggregateResultsFunction.Arn
      SaveToDatabaseFunctionArn: !GetAtt SaveToDatabaseFunction.Arn
      NotifyUserFunctionArn: !GetAtt NotifyUserFunction.Arn
      HandleErrorFunctionArn: !GetAtt HandleErrorFunction.Arn
    Policies:
      - LambdaInvokePolicy:
          FunctionName: !Ref ValidateSearchFunction
      - LambdaInvokePolicy:
          FunctionName: !Ref FindHotelsFunction
      # Add policies for all Lambda functions
```

### Day 3-4: Implement Supporting Lambda Functions

**Validate Search Function:**
```python
import json

def handler(event, context):
    """Validate search parameters"""
    
    required_fields = ['location', 'check_in', 'check_out', 'guests']
    
    for field in required_fields:
        if field not in event:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate dates
    from datetime import datetime
    check_in = datetime.fromisoformat(event['check_in'])
    check_out = datetime.fromisoformat(event['check_out'])
    
    if check_out <= check_in:
        raise ValueError("Check-out must be after check-in")
    
    return {
        **event,
        'validated': True
    }
```

**Find Hotels Function:**
```python
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
hotels_table = dynamodb.Table(os.environ['HOTELS_TABLE'])

def handler(event, context):
    """Find hotels in the specified location"""
    
    location = event['location']
    
    # Query hotels by location (city)
    # In MVP, we can use hotel chain headquarters or popular cities
    response = hotels_table.scan(
        FilterExpression=Attr('city').contains(location) | 
                        Attr('name').contains(location)
    )
    
    hotels = response.get('Items', [])
    
    return {
        **event,
        'hotels': hotels,
        'hotelCount': len(hotels)
    }
```

**Aggregate Results Function:**
```python
def handler(event, context):
    """Aggregate results from parallel scraping"""
    
    scraping_results = event.get('scrapingResults', [])
    
    all_results = []
    failed_scrapers = []
    
    for result in scraping_results:
        if 'error' in result:
            failed_scrapers.append(result.get('chain', 'Unknown'))
        else:
            all_results.extend(result.get('results', []))
    
    return {
        **event,
        'aggregatedResults': all_results,
        'totalResults': len(all_results),
        'failedScrapers': failed_scrapers
    }
```

### Day 5: Update Search API to Use Step Functions

**Modify search.py:**
```python
import boto3

stepfunctions = boto3.client('stepfunctions')

def handler(event, context):
    """Handle search request and start Step Functions workflow"""
    
    body = json.loads(event.get('body', '{}'))
    
    # Create search record
    search_id = db.create_search(...)
    
    # Start Step Functions execution
    execution = stepfunctions.start_execution(
        stateMachineArn=os.environ['WORKFLOW_ARN'],
        name=f"search-{search_id}",
        input=json.dumps({
            'search_id': search_id,
            'location': body['location'],
            'check_in': body['check_in'],
            'check_out': body['check_out'],
            'guests': body['guests'],
            'discount_types': body.get('discount_types', ['aarp', 'aaa', 'senior'])
        })
    )
    
    return {
        'statusCode': 202,
        'body': json.dumps({
            'search_id': search_id,
            'execution_arn': execution['executionArn'],
            'status': 'processing'
        })
    }
```

**Deliverables:**
- Step Functions workflow deployed
- Parallel scraping working
- Error handling and retries configured
- Execution logs visible in CloudWatch

---

## Week 2: Expand Hotel Coverage

### Goal: Add 10+ More Hotel Chains

**New Scrapers to Implement:**
1. Best Western
2. Hyatt
3. Wyndham
4. Choice Hotels
5. Radisson
6. La Quinta
7. Comfort Inn
8. Holiday Inn Express
9. Courtyard by Marriott
10. Hampton Inn

### Implementation Strategy

**For each hotel chain:**

1. **Research the website:**
   - Identify search URL structure
   - Find discount code input fields
   - Locate price elements
   - Check for CAPTCHA or bot detection

2. **Create scraper class:**
   - Extend BaseScraper
   - Implement get_search_url()
   - Implement apply_discount()
   - Implement extract_prices()

3. **Test locally:**
   - Verify scraping works
   - Test all discount types
   - Handle edge cases

4. **Deploy as Lambda:**
   - Add to SAM template
   - Deploy and test
   - Add to Step Functions workflow

### Day 1-5: Implement Scrapers

**Example: Best Western Scraper**
```python
class BestWesternScraper(BaseScraper):
    """Scraper for Best Western hotels"""
    
    CHAIN_NAME = "Best Western"
    BASE_URL = "https://www.bestwestern.com"
    
    def get_search_url(self):
        location_encoded = quote(self.location)
        return (
            f"{self.BASE_URL}/en_US/book/hotel-search.html"
            f"?checkInDate={self.check_in}"
            f"&checkOutDate={self.check_out}"
            f"&numberOfAdults={self.guests}"
            f"&location={location_encoded}"
        )
    
    def apply_discount(self, discount_type):
        discount_codes = {
            'aarp': 'AARP',
            'aaa': 'AAA',
            'senior': '2012001'  # Best Western senior code
        }
        
        code = discount_codes.get(discount_type)
        if not code:
            return
        
        try:
            # Open rate options
            self.page.click('button[aria-label="More Rates"]')
            self.page.wait_for_timeout(1000)
            
            # Select discount type
            self.page.click(f'input[value="{code}"]')
            
            # Apply
            self.page.click('button[type="submit"]')
            self.page.wait_for_load_state('networkidle')
        
        except Exception as e:
            print(f"Error applying discount: {str(e)}")
    
    def extract_prices(self):
        try:
            self.page.wait_for_selector('.rate-amount', timeout=10000)
            
            price_element = self.page.query_selector('.rate-amount')
            if not price_element:
                return None
            
            price_text = price_element.inner_text()
            price = float(price_text.replace('$', '').replace(',', ''))
            
            return {
                'original': price,
                'discounted': price,
                'taxes': 0,  # Extract if available
                'fees': 0,
                'total': price,
                'currency': 'USD'
            }
        
        except Exception as e:
            print(f"Error extracting prices: {str(e)}")
            return None
```

**Deliverables:**
- 10+ additional hotel scrapers implemented
- All scrapers added to Step Functions workflow
- Updated SAM template with new Lambda functions
- Integration tested

---

## Week 3: OTA (Online Travel Agency) Support

### Add Support for Major OTAs

**Target OTAs:**
1. Booking.com
2. Expedia
3. Hotels.com
4. Priceline

### Challenge with OTAs
- OTAs don't typically support membership discount codes
- They show base rates and member-exclusive deals
- Different value proposition: compare OTA prices vs direct booking with discount

### Implementation Approach

**OTA Scraper Structure:**
```python
class BookingComScraper(BaseScraper):
    """Scraper for Booking.com"""
    
    CHAIN_NAME = "Booking.com"
    BASE_URL = "https://www.booking.com"
    
    def get_search_url(self):
        location_encoded = quote(self.location)
        return (
            f"{self.BASE_URL}/searchresults.html"
            f"?checkin={self.check_in}"
            f"&checkout={self.check_out}"
            f"&group_adults={self.guests}"
            f"&ss={location_encoded}"
        )
    
    def apply_discount(self, discount_type):
        # OTAs don't support membership discounts
        # We can check for "Genius" member prices or mobile app rates
        if discount_type == 'genius':
            # Login or check genius pricing
            pass
    
    def extract_prices(self):
        """Extract prices for multiple hotels"""
        hotels = []
        
        # Get all hotel listings
        hotel_cards = self.page.query_selector_all('[data-testid="property-card"]')
        
        for card in hotel_cards[:5]:  # Limit to first 5
            try:
                name = card.query_selector('[data-testid="title"]').inner_text()
                price_element = card.query_selector('[data-testid="price-and-discounted-price"]')
                
                if price_element:
                    price_text = price_element.inner_text()
                    price = float(price_text.replace('$', '').replace(',', ''))
                    
                    hotels.append({
                        'hotel_name': name,
                        'original': price,
                        'discounted': price,
                        'taxes': 0,
                        'fees': 0,
                        'total': price,
                        'currency': 'USD'
                    })
            
            except Exception as e:
                print(f"Error extracting hotel: {str(e)}")
                continue
        
        return hotels
```

**Deliverables:**
- 4 OTA scrapers implemented
- OTA results integrated into main results
- Comparison view showing direct booking vs OTA pricing

---

## Week 4: User Authentication with Cognito

### Setup Amazon Cognito

**Add to SAM Template:**
```yaml
UserPool:
  Type: AWS::Cognito::UserPool
  Properties:
    UserPoolName: !Sub '${AWS::StackName}-users'
    AutoVerifiedAttributes:
      - email
    UsernameAttributes:
      - email
    Schema:
      - Name: email
        Required: true
        Mutable: false
    Policies:
      PasswordPolicy:
        MinimumLength: 8
        RequireUppercase: true
        RequireLowercase: true
        RequireNumbers: true
        RequireSymbols: true

UserPoolClient:
  Type: AWS::Cognito::UserPoolClient
  Properties:
    ClientName: !Sub '${AWS::StackName}-client'
    UserPoolId: !Ref UserPool
    GenerateSecret: false
    ExplicitAuthFlows:
      - ALLOW_USER_SRP_AUTH
      - ALLOW_REFRESH_TOKEN_AUTH
    PreventUserExistenceErrors: ENABLED

UserPoolDomain:
  Type: AWS::Cognito::UserPoolDomain
  Properties:
    Domain: !Sub '${AWS::StackName}-${AWS::AccountId}'
    UserPoolId: !Ref UserPool

# Add Cognito Authorizer to API Gateway
TravelDiscountApi:
  Type: AWS::Serverless::Api
  Properties:
    Auth:
      Authorizers:
        CognitoAuth:
          UserPoolArn: !GetAtt UserPool.Arn
      DefaultAuthorizer: CognitoAuth
```

### Update Frontend for Authentication

**Install AWS Amplify:**
```bash
npm install aws-amplify @aws-amplify/ui-react
```

**Configure Amplify (`src/main.tsx`):**
```typescript
import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    region: 'us-east-1',
    userPoolId: 'YOUR_USER_POOL_ID',
    userPoolWebClientId: 'YOUR_CLIENT_ID',
  }
});
```

**Add Authentication UI:**
```typescript
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';

function App() {
  return (
    <Authenticator>
      {({ signOut, user }) => (
        <div>
          <header>
            <h1>Welcome {user?.username}</h1>
            <button onClick={signOut}>Sign Out</button>
          </header>
          {/* Your app components */}
        </div>
      )}
    </Authenticator>
  );
}
```

**Update API Client to Include Auth Token:**
```typescript
import { fetchAuthSession } from 'aws-amplify/auth';

api.interceptors.request.use(async (config) => {
  try {
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (error) {
    console.error('Error getting auth token:', error);
  }
  
  return config;
});
```

**Deliverables:**
- Cognito User Pool configured
- Frontend authentication working
- Protected API endpoints
- User profile management

---

## Week 5: Historical Data Tracking & Caching

### Implement Caching Strategy

**Add ElastiCache Serverless:**
```yaml
CacheCluster:
  Type: AWS::ElastiCache::ServerlessCache
  Properties:
    Engine: redis
    ServerlessCacheName: !Sub '${AWS::StackName}-cache'
    Description: Cache for hotel search results
    SecurityGroupIds:
      - !Ref CacheSecurityGroup
    SubnetIds:
      - !Ref PrivateSubnet1
      - !Ref PrivateSubnet2
```

**Or use DynamoDB TTL for simpler caching:**
```python
# Add TTL field to results
from datetime import datetime, timedelta

def save_result_with_cache(result_data):
    # Add TTL (24 hours from now)
    ttl = int((datetime.utcnow() + timedelta(hours=24)).timestamp())
    
    item = {
        **result_data,
        'ttl': ttl
    }
    
    results_table.put_item(Item=item)
```

### Track Price History

**Create Price History Table:**
```yaml
PriceHistoryTable:
  Type: AWS::DynamoDB::Table
  Properties:
    TableName: !Sub '${AWS::StackName}-price-history'
    BillingMode: PAY_PER_REQUEST
    AttributeDefinitions:
      - AttributeName: hotel_id
        AttributeType: S
      - AttributeName: recorded_at
        AttributeType: S
      - AttributeName: discount_type
        AttributeType: S
    KeySchema:
      - AttributeName: hotel_id
        KeyType: HASH
      - AttributeName: recorded_at
        KeyType: RANGE
    GlobalSecondaryIndexes:
      - IndexName: discount-type-index
        KeySchema:
          - AttributeName: discount_type
            KeyType: HASH
          - AttributeName: recorded_at
            KeyType: RANGE
        Projection:
          ProjectionType: ALL
```

**Save Historical Data:**
```python
def save_price_history(hotel_id, discount_type, price_data):
    history_table = dynamodb.Table(os.environ['PRICE_HISTORY_TABLE'])
    
    item = {
        'hotel_id': hotel_id,
        'recorded_at': datetime.utcnow().isoformat(),
        'discount_type': discount_type,
        'price': price_data['total'],
        'check_in_date': price_data.get('check_in'),
        'check_out_date': price_data.get('check_out'),
        'nights': price_data.get('nights', 1),
        'currency': price_data.get('currency', 'USD')
    }
    
    history_table.put_item(Item=item)
```

**Deliverables:**
- Caching implemented (ElastiCache or DynamoDB TTL)
- Price history tracking functional
- Historical data API endpoints
- Cache hit rate monitoring

---

## Week 6-7: EventBridge Scheduling & Notifications

### Implement Scheduled Searches

**Add EventBridge Rule:**
```yaml
ScheduledSearchRule:
  Type: AWS::Events::Rule
  Properties:
    Description: Run saved searches daily
    ScheduleExpression: 'cron(0 12 * * ? *)'  # Daily at 12pm UTC
    State: ENABLED
    Targets:
      - Arn: !GetAtt ProcessScheduledSearchesFunction.Arn
        Id: ProcessScheduledSearches
```

**Saved Searches Table:**
```yaml
SavedSearchesTable:
  Type: AWS::DynamoDB::Table
  Properties:
    TableName: !Sub '${AWS::StackName}-saved-searches'
    BillingMode: PAY_PER_REQUEST
    AttributeDefinitions:
      - AttributeName: user_id
        AttributeType: S
      - AttributeName: search_id
        AttributeType: S
    KeySchema:
      - AttributeName: user_id
        KeyType: HASH
      - AttributeName: search_id
        KeyType: RANGE
```

### Implement Email Notifications with SNS

**Add SNS Topic:**
```yaml
NotificationTopic:
  Type: AWS::SNS::Topic
  Properties:
    TopicName: !Sub '${AWS::StackName}-notifications'
    Subscription:
      - Endpoint: !Ref AdminEmail
        Protocol: email
```

**Send Notification Lambda:**
```python
import boto3

sns = boto3.client('sns')

def handler(event, context):
    """Send email notification for search results"""
    
    search_id = event['search_id']
    user_email = event['user_email']
    results = event['aggregatedResults']
    
    # Find best deal
    best_deal = min(results, key=lambda x: x['total_price'])
    
    message = f"""
    Your hotel search is complete!
    
    Search ID: {search_id}
    Total Results: {len(results)}
    
    Best Deal:
    - Hotel: {best_deal['hotel_name']}
    - Discount: {best_deal['discount_type']}
    - Price: ${best_deal['total_price']}
    
    View full results: https://your-app-url.com/results/{search_id}
    """
    
    sns.publish(
        TopicArn=os.environ['TOPIC_ARN'],
        Subject='Hotel Search Results Ready',
        Message=message
    )
```

**Deliverables:**
- EventBridge scheduled searches
- SNS email notifications
- Saved searches feature
- User notification preferences

---

## Phase 2 Success Criteria

✅ **Features Completed:**
- Step Functions orchestrating parallel scraping
- 15+ hotel chains supported
- 4+ OTA sites supported
- User authentication with Cognito
- Historical price tracking
- Caching implemented
- Scheduled searches
- Email notifications

✅ **Performance:**
- Search completes in < 45 seconds (with 15 chains)
- 95%+ scraping success rate
- Cache hit rate > 60%

✅ **Infrastructure:**
- Fully serverless AWS architecture
- Auto-scaling enabled
- Monitoring dashboards
- Cost < $300/month for moderate usage

---

## Phase 3: Advanced Analytics (3-5 weeks)

### Week 1: Data Lake with Athena & Glue

**Setup S3 Data Lake:**
```yaml
DataLakeBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub '${AWS::StackName}-data-lake'
    LifecycleConfiguration:
      Rules:
        - Id: ArchiveOldData
          Status: Enabled
          Transitions:
            - TransitionInDays: 90
              StorageClass: GLACIER
```

**Glue Database & Crawler:**
```yaml
GlueDatabase:
  Type: AWS::Glue::Database
  Properties:
    CatalogId: !Ref AWS::AccountId
    DatabaseInput:
      Name: !Sub '${AWS::StackName}_analytics'

GlueCrawler:
  Type: AWS::Glue::Crawler
  Properties:
    Name: !Sub '${AWS::StackName}-crawler'
    Role: !GetAtt GlueCrawlerRole.Arn
    DatabaseName: !Ref GlueDatabase
    Targets:
      S3Targets:
        - Path: !Sub 's3://${DataLakeBucket}/results/'
    Schedule:
      ScheduleExpression: 'cron(0 2 * * ? *)'
```

**Export Results to S3:**
```python
import boto3
import json
from datetime import datetime

s3 = boto3.client('s3')

def export_to_data_lake(results):
    """Export results to S3 in Parquet format for Athena"""
    
    # Organize by date partition
    date_path = datetime.utcnow().strftime('%Y/%m/%d')
    key = f"results/{date_path}/results_{int(datetime.utcnow().timestamp())}.json"
    
    s3.put_object(
        Bucket=os.environ['DATA_LAKE_BUCKET'],
        Key=key,
        Body=json.dumps(results),
        ContentType='application/json'
    )
```

**Query with Athena:**
```sql
-- Average price by hotel chain and discount type
SELECT 
    hotel_chain,
    discount_type,
    AVG(total_price) as avg_price,
    COUNT(*) as sample_count
FROM results
WHERE recorded_at >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
GROUP BY hotel_chain, discount_type
ORDER BY avg_price ASC;

-- Best discount by day of week
SELECT 
    DAYOFWEEK(check_in_date) as day_of_week,
    discount_type,
    AVG(total_price - original_price) as avg_savings
FROM results
GROUP BY DAYOFWEEK(check_in_date), discount_type
ORDER BY avg_savings DESC;
```

**Deliverables:**
- S3 data lake configured
- Glue crawler running
- Athena queries working
- Analytics Lambda functions

---

### Week 2: Price Prediction Model

**Simple ML Model with Lambda:**
```python
import numpy as np
from sklearn.linear_model import LinearRegression
import pickle

def train_price_prediction_model():
    """Train simple price prediction model"""
    
    # Fetch historical data
    history = fetch_price_history(days=180)
    
    # Features: days_until_checkin, day_of_week, month, hotel_chain_id
    X = []
    y = []
    
    for record in history:
        features = [
            record['days_until_checkin'],
            record['day_of_week'],
            record['month'],
            record['hotel_chain_encoded']
        ]
        X.append(features)
        y.append(record['price'])
    
    # Train model
    model = LinearRegression()
    model.fit(np.array(X), np.array(y))
    
    # Save model to S3
    model_bytes = pickle.dumps(model)
    s3.put_object(
        Bucket=os.environ['MODELS_BUCKET'],
        Key='price_prediction_model.pkl',
        Body=model_bytes
    )
    
    return model

def predict_price(hotel_chain, check_in_date, discount_type):
    """Predict price for future date"""
    
    # Load model from S3
    response = s3.get_object(
        Bucket=os.environ['MODELS_BUCKET'],
        Key='price_prediction_model.pkl'
    )
    model = pickle.loads(response['Body'].read())
    
    # Prepare features
    days_until = (check_in_date - datetime.now()).days
    features = [[days_until, check_in_date.weekday(), check_in_date.month, hotel_chain_id]]
    
    # Predict
    predicted_price = model.predict(features)[0]
    
    return predicted_price
```

**Or Use SageMaker for Advanced Models:**
```yaml
PredictionModel:
  Type: AWS::SageMaker::Model
  Properties:
    ModelName: !Sub '${AWS::StackName}-price-prediction'
    PrimaryContainer:
      Image: !Sub '382416733822.dkr.ecr.${AWS::Region}.amazonaws.com/xgboost:latest'
      ModelDataUrl: !Sub 's3://${ModelsBucket}/model.tar.gz'
    ExecutionRoleArn: !GetAtt SageMakerRole.Arn
```

**Deliverables:**
- Price prediction model trained
- Prediction API endpoint
- Model retraining scheduled
- Accuracy metrics tracked

---

### Week 3: Discount Effectiveness Scoring

**Calculate Discount Scores:**
```python
def calculate_discount_effectiveness(hotel_chain, discount_type, period_days=90):
    """Calculate how effective a discount is for a hotel chain"""
    
    # Get historical data
    baseline_prices = get_prices(hotel_chain, 'none', period_days)
    discount_prices = get_prices(hotel_chain, discount_type, period_days)
    
    if not baseline_prices or not discount_prices:
        return None
    
    avg_baseline = np.mean(baseline_prices)
    avg_discount = np.mean(discount_prices)
    
    # Calculate metrics
    avg_savings = avg_baseline - avg_discount
    pct_savings = (avg_savings / avg_baseline) * 100
    availability = len(discount_prices) / len(baseline_prices) * 100
    
    # Score (0-100)
    score = (pct_savings * 0.7) + (availability * 0.3)
    
    return {
        'hotel_chain': hotel_chain,
        'discount_type': discount_type,
        'avg_savings': avg_savings,
        'pct_savings': pct_savings,
        'availability': availability,
        'score': min(score, 100),
        'sample_size': len(discount_prices)
    }
```

**Create Analytics Dashboard API:**
```python
def handler(event, context):
    """Get analytics for dashboard"""
    
    # Get all hotel chains
    chains = ['Marriott', 'Hilton', 'IHG', 'Best Western', 'Hyatt']
    discount_types = ['aarp', 'aaa', 'senior']
    
    results = []
    
    for chain in chains:
        for discount in discount_types:
            score = calculate_discount_effectiveness(chain, discount)
            if score:
                results.append(score)
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'rankings': results,
            'generated_at': datetime.utcnow().isoformat()
        })
    }
```

**Deliverables:**
- Discount effectiveness algorithm
- Rankings API endpoint
- Trend analysis
- Insights generation

---

### Week 4-5: Custom Alerts & Export Features

**Price Drop Alerts:**
```python
def check_price_drops():
    """Check for price drops on saved searches"""
    
    # Get all active saved searches
    saved_searches = get_active_saved_searches()
    
    for search in saved_searches:
        # Get current prices
        current_results = execute_search(search)
        
        # Get previous best price
        previous_best = get_previous_best_price(search['search_id'])
        
        # Check for drop
        current_best = min([r['total_price'] for r in current_results])
        
        if current_best < previous_best * 0.95:  # 5% drop
            # Send alert
            send_price_drop_alert(
                user_id=search['user_id'],
                search=search,
                old_price=previous_best,
                new_price=current_best,
                savings=previous_best - current_best
            )
```

**Export to CSV/Excel:**
```python
import csv
import io
import boto3

def export_results_to_csv(search_id):
    """Export search results to CSV"""
    
    results = get_results_by_search(search_id)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(['Hotel', 'Chain', 'Discount Type', 'Original Price', 
                    'Discounted Price', 'Taxes', 'Total', 'Savings'])
    
    # Data
    for result in results:
        writer.writerow([
            result['hotel_name'],
            result['chain'],
            result['discount_type'],
            f"${result['original_price']:.2f}",
            f"${result['discounted_price']:.2f}",
            f"${result['taxes']:.2f}",
            f"${result['total_price']:.2f}",
            f"${result['savings']:.2f}"
        ])
    
    # Upload to S3
    s3_key = f"exports/{search_id}.csv"
    s3.put_object(
        Bucket=os.environ['EXPORTS_BUCKET'],
        Key=s3_key,
        Body=output.getvalue(),
        ContentType='text/csv'
    )
    
    # Generate presigned URL (valid for 1 hour)
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.environ['EXPORTS_BUCKET'], 'Key': s3_key},
        ExpiresIn=3600
    )
    
    return url
```

**Deliverables:**
- Price drop alerts working
- Custom alert rules
- CSV/Excel export
- Scheduled reports

---

## Phase 4: Scale & Optimize (3-5 weeks)

### Week 1: Performance Optimization

**Lambda Optimization:**
1. Right-size memory (test 512MB, 1024MB, 2048MB)
2. Use Lambda Layers for common dependencies
3. Optimize cold starts (provisioned concurrency for critical functions)
4. Implement connection pooling for DynamoDB

**Example: Provisioned Concurrency**
```yaml
SearchFunctionAlias:
  Type: AWS::Lambda::Alias
  Properties:
    FunctionName: !Ref SearchFunction
    FunctionVersion: !GetAtt SearchFunctionVersion.Version
    Name: live
    ProvisionedConcurrencyConfig:
      ProvisionedConcurrentExecutions: 5
```

**DynamoDB Optimization:**
```python
# Batch operations
with results_table.batch_writer() as batch:
    for result in results:
        batch.put_item(Item=result)

# Use consistent reads only when necessary
response = table.query(
    KeyConditionExpression=Key('search_id').eq(search_id),
    ConsistentRead=False  # Eventually consistent is cheaper
)
```

**Caching Improvements:**
```python
import hashlib

def get_cache_key(search_params):
    """Generate cache key from search parameters"""
    key_string = f"{search_params['location']}-{search_params['check_in']}-{search_params['check_out']}"
    return hashlib.md5(key_string.encode()).hexdigest()

def get_cached_results(search_params):
    """Check cache before scraping"""
    cache_key = get_cache_key(search_params)
    
    # Check DynamoDB for recent results (< 6 hours old)
    response = cache_table.get_item(Key={'cache_key': cache_key})
    
    if 'Item' in response:
        cached_at = datetime.fromisoformat(response['Item']['cached_at'])
        if datetime.utcnow() - cached_at < timedelta(hours=6):
            return response['Item']['results']
    
    return None
```

**Deliverables:**
- Lambda functions optimized
- Response times improved by 30%+
- Cost reduced by 20%+
- Performance benchmarks documented

---

### Week 2: Security Hardening

**Add AWS WAF:**
```yaml
WebACL:
  Type: AWS::WAFv2::WebACL
  Properties:
    Scope: REGIONAL
    DefaultAction:
      Allow: {}
    Rules:
      - Name: RateLimitRule
        Priority: 1
        Statement:
          RateBasedStatement:
            Limit: 1000
            AggregateKeyType: IP
        Action:
          Block: {}
        VisibilityConfig:
          SampledRequestsEnabled: true
          CloudWatchMetricsEnabled: true
          MetricName: RateLimitRule
      
      - Name: GeoBlockRule
        Priority: 2
        Statement:
          GeoMatchStatement:
            CountryCodes:
              - CN  # Block specific countries if needed
              - RU
        Action:
          Block: {}
        VisibilityConfig:
          SampledRequestsEnabled: true
          CloudWatchMetricsEnabled: true
          MetricName: GeoBlockRule

WebACLAssociation:
  Type: AWS::WAFv2::WebACLAssociation
  Properties:
    ResourceArn: !Sub 'arn:aws:apigateway:${AWS::Region}::/restapis/${TravelDiscountApi}/stages/dev'
    WebACLArn: !GetAtt WebACL.Arn
```

**Encrypt Sensitive Data:**
```yaml
# Enable encryption for DynamoDB
ResultsTable:
  Type: AWS::DynamoDB::Table
  Properties:
    SSESpecification:
      SSEEnabled: true
      SSEType: KMS
      KMSMasterKeyId: !Ref EncryptionKey

EncryptionKey:
  Type: AWS::KMS::Key
  Properties:
    Description: Encryption key for DynamoDB tables
    KeyPolicy:
      Version: '2012-10-17'
      Statement:
        - Sid: Enable IAM User Permissions
          Effect: Allow
          Principal:
            AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:root'
          Action: 'kms:*'
          Resource: '*'
```

**Secrets Manager for API Keys:**
```python
import boto3
import json

secrets_client = boto3.client('secretsmanager')

def get_secret(secret_name):
    """Retrieve secret from Secrets Manager"""
    response = secrets_client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
proxy_credentials = get_secret('proxy-service-api-key')
captcha_key = get_secret('captcha-service-key')
```

**Deliverables:**
- WAF rules deployed
- Encryption enabled
- Secrets Manager configured
- Security audit passed

---

### Week 3: CI/CD Pipeline

**CodePipeline Setup:**
```yaml
CodePipeline:
  Type: AWS::CodePipeline::Pipeline
  Properties:
    Name: !Sub '${AWS::StackName}-pipeline'
    RoleArn: !GetAtt CodePipelineRole.Arn
    ArtifactStore:
      Type: S3
      Location: !Ref ArtifactsBucket
    Stages:
      - Name: Source
        Actions:
          - Name: SourceAction
            ActionTypeId:
              Category: Source
              Owner: ThirdParty
              Provider: GitHub
              Version: '1'
            Configuration:
              Owner: !Ref GitHubOwner
              Repo: !Ref GitHubRepo
              Branch: main
              OAuthToken: !Ref GitHubToken
            OutputArtifacts:
              - Name: SourceOutput
      
      - Name: Build
        Actions:
          - Name: BuildAction
            ActionTypeId:
              Category: Build
              Owner: AWS
              Provider: CodeBuild
              Version: '1'
            Configuration:
              ProjectName: !Ref CodeBuildProject
            InputArtifacts:
              - Name: SourceOutput
            OutputArtifacts:
              - Name: BuildOutput
      
      - Name: Deploy
        Actions:
          - Name: DeployAction
            ActionTypeId:
              Category: Deploy
              Owner: AWS
              Provider: CloudFormation
              Version: '1'
            Configuration:
              ActionMode: CREATE_UPDATE
              StackName: !Sub '${AWS::StackName}-app'
              TemplatePath: BuildOutput::packaged.yaml
              Capabilities: CAPABILITY_IAM
            InputArtifacts:
              - Name: BuildOutput
```

**buildspec.yml:**
```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.11
      nodejs: 18
    commands:
      - pip install aws-sam-cli
      - npm install -g npm@latest
  
  pre_build:
    commands:
      - echo "Running tests..."
      - cd backend && python -m pytest tests/
      - cd ../frontend && npm install && npm test
  
  build:
    commands:
      - echo "Building SAM application..."
      - sam build
      - sam package --output-template-file packaged.yaml --s3-bucket $ARTIFACTS_BUCKET
      - echo "Building frontend..."
      - cd frontend && npm run build

artifacts:
  files:
    - packaged.yaml
    - frontend/dist/**/*
```

**Deliverables:**
- CI/CD pipeline operational
- Automated testing
- Blue/green deployments
- Rollback capability

---

### Week 4: Advanced Monitoring & X-Ray

**Enable X-Ray Tracing:**
```yaml
Globals:
  Function:
    Tracing: Active
  Api:
    TracingEnabled: true
```

**Custom CloudWatch Dashboard:**
```yaml
Dashboard:
  Type: AWS::CloudWatch::Dashboard
  Properties:
    DashboardName: !Sub '${AWS::StackName}-metrics'
    DashboardBody: !Sub |
      {
        "widgets": [
          {
            "type": "metric",
            "properties": {
              "metrics": [
                ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
                [".", "Errors", {"stat": "Sum"}],
                [".", "Duration", {"stat": "Average"}]
              ],
              "period": 300,
              "stat": "Average",
              "region": "${AWS::Region}",
              "title": "Lambda Metrics"
            }
          },
          {
            "type": "metric",
            "properties": {
              "metrics": [
                ["AWS/States", "ExecutionsFailed"],
                [".", "ExecutionsSucceeded"]
              ],
              "period": 300,
              "stat": "Sum",
              "region": "${AWS::Region}",
              "title": "Step Functions Executions"
            }
          }
        ]
      }
```

**Custom Metrics:**
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def put_custom_metric(metric_name, value, unit='Count'):
    """Send custom metric to CloudWatch"""
    cloudwatch.put_metric_data(
        Namespace='TravelDiscountTool',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }
        ]
    )

# Usage
put_custom_metric('ScrapingSuccessRate', 0.97, 'Percent')
put_custom_metric('AverageSavingsFound', 45.23, 'None')
```

**Deliverables:**
- X-Ray tracing enabled
- Custom CloudWatch dashboard
- Alarms configured
- Log insights queries

---

### Week 5: Load Testing & Documentation

**Load Testing with Artillery:**
```yaml
# load-test.yml
config:
  target: 'https://your-api-gateway-url.com/dev'
  phases:
    - duration: 60
      arrivalRate: 10
    - duration: 120
      arrivalRate: 50
    - duration: 60
      arrivalRate: 100
  
scenarios:
  - name: "Search hotels"
    flow:
      - post:
          url: "/search"
          json:
            location: "New York, NY"
            check_in: "2025-12-01"
            check_out: "2025-12-03"
            guests: 2
      - think: 5
      - get:
          url: "/results/{{ search_id }}"
```

**Final Documentation:**
1. Architecture diagrams (updated)
2. API documentation (OpenAPI spec)
3. Operations runbook
4. Disaster recovery plan
5. Cost optimization guide
6. Scaling guide
7. Troubleshooting guide

**Deliverables:**
- Load testing completed (1000+ concurrent users)
- Complete documentation
- Operations runbook
- Production-ready deployment

---

## Complete Project Success Metrics

**Technical Metrics:**
- ✅ Supports 15+ hotel chains + 4 OTAs
- ✅ 95%+ scraping success rate
- ✅ Search completion < 45 seconds
- ✅ API response time < 2 seconds
- ✅ System uptime > 99.5%
- ✅ Cost < $600/month (moderate usage)

**Business Metrics:**
- ✅ Average savings per search: $40+
- ✅ User retention rate: 60%+
- ✅ Daily active users: 100+
- ✅ Searches per user per month: 5+

**Project Completion:**
- ✅ All 4 phases completed
- ✅ Production deployment successful
- ✅ Documentation complete
- ✅ Monitoring operational
- ✅ CI/CD pipeline functional

---

## Total Project Timeline

**Phase 1 (MVP):** 4-6 weeks
**Phase 2 (Enhanced):** 5-7 weeks
**Phase 3 (Analytics):** 3-5 weeks
**Phase 4 (Scale):** 3-5 weeks

**Total:** 15-23 weeks (solo developer)
**Total:** 10-14 weeks (team of 2-3)

**Total Budget:**
- Development: $12,000-40,000
- Infrastructure (annual): $1,800-7,200
- **Grand Total Year 1:** $13,800-47,200