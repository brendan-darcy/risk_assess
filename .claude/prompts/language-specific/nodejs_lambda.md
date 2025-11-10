# Skills: nodejs, aws_lambda, typescript, serverless, api_development, testing
# SSDF Practice Group: PW (Produce Well-Secured Software), PS (Protect the Software)
# ARMATech Principles: Cloud First, API Integration, Security, Modern
# Language: Node.js/TypeScript
# Context: Apprise Risk Solutions P&T Team - AWS Lambda Development

## Security Reminder
⚠️ **CRITICAL**: Lambda functions are publicly accessible via API Gateway. All functions must authenticate requests, validate inputs, handle errors securely, and use AWS Secrets Manager for credentials.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only (NOT Production)
- [ ] Using dummy test data (NO client/production data)
- [ ] Will delete Claude Code chat history after this session
- [ ] Pre-flight check passed (`./pre-flight-check.sh`)

## Placeholders
- `[FUNCTION_NAME]` - Lambda function name (kebab-case, e.g., "valuation-metrics-api")
- `[FUNCTIONALITY]` - Function purpose (e.g., "Serve valuation metrics via REST API")
- `[API_PATH]` - API Gateway path (e.g., "/api/v1/metrics")
- `[HTTP_METHOD]` - HTTP method (GET | POST | PUT | DELETE)
- `[DATA_SOURCE]` - Data source (DuckDB | PostgreSQL | S3 | Databricks)

---

## Task: AWS Lambda Function Development

You are a backend engineer at Apprise Risk Solutions developing AWS Lambda functions for the ARMATech valuation platform. Generate production-ready, secure, performant Lambda functions following AWS best practices, OWASP controls, and Apprise coding standards.

### Context

**Company**: Apprise Risk Solutions
- Serverless APIs on AWS Lambda + API Gateway
- TypeScript for type safety
- ISO 27001:2022 compliant, OWASP-based secure coding
- Minimum 80% test coverage required

**AWS Lambda**:
- **Architecture**: Event-driven, serverless compute
- **Execution**: Node.js 20.x runtime
- **Limits**: 15-minute timeout, 10GB memory max
- **Pricing**: Pay per invocation and compute time

**Lambda Standards at Apprise**:
- **Language**: TypeScript (strict mode)
- **Framework**: Serverless Framework for deployment
- **Testing**: Jest with aws-sdk-mock
- **Logging**: Structured JSON logs for CloudWatch
- **Secrets**: AWS Secrets Manager (not environment variables for sensitive data)
- **Cold Start Optimization**: Keep handler lightweight

---

## Lambda Development Specification

**Function Name**: [FUNCTION_NAME]

**Functionality**: [FUNCTIONALITY]

**API Path**: [API_PATH]

**HTTP Method**: [HTTP_METHOD]

**Data Source**: [DATA_SOURCE]

**Test Coverage Target**: 80% minimum

---

## Instructions

### Phase 1: DESIGN (Architecture & Security)

**1. Function Structure**

```
[functionName]/
├── src/
│   ├── handlers/
│   │   └── [functionName].ts       # Lambda handler
│   ├── services/
│   │   └── [serviceName].ts        # Business logic
│   ├── models/
│   │   └── [modelName].ts          # Data models (types)
│   ├── utils/
│   │   ├── logger.ts               # Structured logging
│   │   ├── validator.ts            # Input validation
│   │   └── errorHandler.ts         # Error handling
│   └── config/
│       └── config.ts                # Configuration
├── tests/
│   ├── unit/
│   │   └── [functionName].test.ts
│   └── integration/
│       └── [functionName].int.test.ts
├── serverless.yml                   # Deployment config
├── tsconfig.json                    # TypeScript config
├── package.json
└── .env.example                     # Example environment variables
```

**2. Handler Pattern Selection**

**REST API Handler** (API Gateway HTTP):
```typescript
export const handler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
    // Parse request
    // Call service
    // Return response
};
```

**SQS Message Handler** (event-driven):
```typescript
export const handler = async (event: SQSEvent): Promise<void> => {
    // Process messages
};
```

**S3 Event Handler** (file processing):
```typescript
export const handler = async (event: S3Event): Promise<void> => {
    // Process S3 objects
};
```

**Scheduled Handler** (cron/rate):
```typescript
export const handler = async (event: ScheduledEvent): Promise<void> => {
    // Execute scheduled task
};
```

**3. Security Architecture**

**Authentication**:
```typescript
// API Gateway Authorizer (JWT)
export const authorizer = async (event: APIGatewayTokenAuthorizerEvent): Promise<AuthResponse> => {
    const token = event.authorizationToken;
    // Verify JWT
    // Return policy
};

// Or use Cognito User Pools (recommended)
```

**Input Validation**:
```typescript
import Joi from 'joi';

const schema = Joi.object({
    territory: Joi.string().valid('NSW_ACT', 'QLD', 'VIC_TAS', 'SA_NT', 'WA').required(),
    startDate: Joi.date().iso().required(),
    endDate: Joi.date().iso().min(Joi.ref('startDate')).required()
});

// Validate
const { error, value } = schema.validate(input);
if (error) {
    throw new ValidationError(error.message);
}
```

**Secrets Management**:
```typescript
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';

const client = new SecretsManagerClient({ region: 'ap-southeast-2' });

async function getSecret(secretName: string): Promise<string> {
    const response = await client.send(
        new GetSecretValueCommand({ SecretId: secretName })
    );
    return response.SecretString || '';
}

// Cache secrets to reduce API calls
const secretCache: Record<string, string> = {};
```

---

### Phase 2: IMPLEMENT (Lambda Function Generation)

**1. TypeScript Configuration** (`tsconfig.json`)

```json
{
    "compilerOptions": {
        "target": "ES2020",
        "module": "commonjs",
        "lib": ["ES2020"],
        "strict": true,
        "esModuleInterop": true,
        "skipLibCheck": true,
        "forceConsistentCasingInFileNames": true,
        "moduleResolution": "node",
        "resolveJsonModule": true,
        "outDir": "./dist",
        "rootDir": "./src",
        "types": ["node", "jest"]
    },
    "include": ["src/**/*"],
    "exclude": ["node_modules", "dist", "tests"]
}
```

**2. Lambda Handler** (`src/handlers/[functionName].ts`)

```typescript
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { Logger } from '../utils/logger';
import { ValidationError, NotFoundError, AuthorizationError } from '../utils/errors';
import { ErrorHandler } from '../utils/errorHandler';
import { [ServiceName] } from '../services/[serviceName]';

const logger = new Logger('Function Name Handler');
const service = new [ServiceName]();
const errorHandler = new ErrorHandler();

/**
 * Lambda handler for [FUNCTIONALITY]
 *
 * @param event API Gateway event
 * @returns API Gateway response
 */
export const handler = async (
    event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
    const requestId = event.requestContext.requestId;
    logger.info('Request received', { requestId, path: event.path, method: event.httpMethod });

    try {
        // CORS headers
        const headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': true
        };

        // Authentication check (if using API Gateway authorizer, claims available in event.requestContext.authorizer)
        const userId = event.requestContext.authorizer?.claims?.sub;
        if (!userId) {
            throw new AuthorizationError('Unauthorized');
        }

        // Route by HTTP method and path
        const { httpMethod, path } = event;

        if (httpMethod === 'GET' && path === '/api/v1/metrics') {
            return await handleGetMetrics(event, headers);
        } else if (httpMethod === 'POST' && path === '/api/v1/metrics/calculate') {
            return await handleCalculateMetrics(event, headers);
        } else {
            return {
                statusCode: 404,
                headers,
                body: JSON.stringify({ error: 'Not Found' })
            };
        }
    } catch (error) {
        logger.error('Error processing request', { requestId, error });
        return errorHandler.handle(error);
    }
};

/**
 * Handle GET /api/v1/metrics
 */
async function handleGetMetrics(
    event: APIGatewayProxyEvent,
    headers: Record<string, any>
): Promise<APIGatewayProxyResult> {
    // Parse query parameters
    const { territory, startDate, endDate } = event.queryStringParameters || {};

    // Validate inputs
    if (!territory || !startDate || !endDate) {
        throw new ValidationError('Missing required parameters: territory, startDate, endDate');
    }

    // Validate territory
    const validTerritories = ['NSW_ACT', 'QLD', 'VIC_TAS', 'SA_NT', 'WA'];
    if (!validTerritories.includes(territory)) {
        throw new ValidationError(`Invalid territory. Must be one of: ${validTerritories.join(', ')}`);
    }

    // Validate dates
    const start = new Date(startDate);
    const end = new Date(endDate);
    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
        throw new ValidationError('Invalid date format. Use ISO 8601 (YYYY-MM-DD)');
    }
    if (end < start) {
        throw new ValidationError('endDate must be after startDate');
    }

    // Call service
    const metrics = await service.getMetrics({ territory, startDate: start, endDate: end });

    return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
            success: true,
            data: metrics,
            meta: {
                territory,
                startDate: startDate,
                endDate: endDate
            }
        })
    };
}

/**
 * Handle POST /api/v1/metrics/calculate
 */
async function handleCalculateMetrics(
    event: APIGatewayProxyEvent,
    headers: Record<string, any>
): Promise<APIGatewayProxyResult> {
    // Parse request body
    const body = JSON.parse(event.body || '{}');

    // Validate inputs
    if (!body.jobNumbers || !Array.isArray(body.jobNumbers)) {
        throw new ValidationError('jobNumbers must be an array');
    }

    if (body.jobNumbers.length === 0) {
        throw new ValidationError('jobNumbers cannot be empty');
    }

    if (body.jobNumbers.length > 1000) {
        throw new ValidationError('jobNumbers cannot exceed 1000 items');
    }

    // Call service
    const result = await service.calculateMetrics(body.jobNumbers);

    return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
            success: true,
            data: result
        })
    };
}
```

**3. Service Layer** (`src/services/[serviceName].ts`)

```typescript
import { DuckDBClient } from '../clients/duckdbClient';
import { Logger } from '../utils/logger';
import { NotFoundError } from '../utils/errors';

const logger = new Logger('[ServiceName]');

export interface MetricsQuery {
    territory: string;
    startDate: Date;
    endDate: Date;
}

export interface MetricsResult {
    date: string;
    totalJobs: number;
    completionRate: number;
    averageDays: number;
}

/**
 * Service for [FUNCTIONALITY]
 */
export class [ServiceName] {
    private duckdb: DuckDBClient;

    constructor() {
        this.duckdb = new DuckDBClient();
    }

    /**
     * Get metrics for territory and date range
     */
    async getMetrics(query: MetricsQuery): Promise<MetricsResult[]> {
        logger.info('Getting metrics', { query });

        try {
            // Build query
            const sql = `
                SELECT
                    date,
                    total_jobs,
                    completion_rate,
                    average_days
                FROM delta_scan('s3://apprise-gold-data/gold/valuation_metrics_daily')
                WHERE territory = ?
                  AND date >= ?
                  AND date <= ?
                ORDER BY date
            `;

            // Execute query (parameterized)
            const result = await this.duckdb.query(sql, [
                query.territory,
                query.startDate.toISOString().split('T')[0],
                query.endDate.toISOString().split('T')[0]
            ]);

            if (result.length === 0) {
                logger.warn('No metrics found', { query });
                return [];
            }

            // Transform result
            return result.map(row => ({
                date: row.date,
                totalJobs: row.total_jobs,
                completionRate: row.completion_rate,
                averageDays: row.average_days
            }));
        } catch (error) {
            logger.error('Error getting metrics', { error, query });
            throw error;
        }
    }

    /**
     * Calculate metrics for specific job numbers
     */
    async calculateMetrics(jobNumbers: string[]): Promise<any> {
        logger.info('Calculating metrics', { count: jobNumbers.length });

        // Implementation
        const sql = `
            SELECT
                COUNT(*) as total,
                AVG(days_to_complete) as avgDays,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM delta_scan('s3://apprise-silver-data/silver/valuation_orders')
            WHERE job_number IN (${jobNumbers.map(() => '?').join(',')})
        `;

        const result = await this.duckdb.query(sql, jobNumbers);

        return {
            total: result[0].total,
            averageDays: Math.round(result[0].avgDays),
            completionRate: (result[0].completed / result[0].total * 100).toFixed(2)
        };
    }
}
```

**4. Logger** (`src/utils/logger.ts`)

```typescript
/**
 * Structured logger for CloudWatch Logs
 */
export class Logger {
    private context: string;

    constructor(context: string) {
        this.context = context;
    }

    info(message: string, metadata?: Record<string, any>): void {
        this.log('INFO', message, metadata);
    }

    warn(message: string, metadata?: Record<string, any>): void {
        this.log('WARN', message, metadata);
    }

    error(message: string, metadata?: Record<string, any>): void {
        this.log('ERROR', message, metadata);
    }

    private log(level: string, message: string, metadata?: Record<string, any>): void {
        const logEntry = {
            timestamp: new Date().toISOString(),
            level,
            context: this.context,
            message,
            ...metadata
        };

        console.log(JSON.stringify(logEntry));
    }
}
```

**5. Error Handler** (`src/utils/errorHandler.ts`)

```typescript
import { APIGatewayProxyResult } from 'aws-lambda';
import { Logger } from './logger';

const logger = new Logger('ErrorHandler');

/**
 * Custom error classes
 */
export class ValidationError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'ValidationError';
    }
}

export class NotFoundError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'NotFoundError';
    }
}

export class AuthorizationError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'AuthorizationError';
    }
}

/**
 * Error handler for Lambda functions
 */
export class ErrorHandler {
    handle(error: unknown): APIGatewayProxyResult {
        const headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        };

        if (error instanceof ValidationError) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({
                    success: false,
                    error: 'Validation Error',
                    message: error.message
                })
            };
        }

        if (error instanceof NotFoundError) {
            return {
                statusCode: 404,
                headers,
                body: JSON.stringify({
                    success: false,
                    error: 'Not Found',
                    message: error.message
                })
            };
        }

        if (error instanceof AuthorizationError) {
            return {
                statusCode: 401,
                headers,
                body: JSON.stringify({
                    success: false,
                    error: 'Unauthorized',
                    message: error.message
                })
            };
        }

        // Unknown error - don't expose details
        logger.error('Unexpected error', { error });

        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: 'Internal Server Error',
                message: 'An unexpected error occurred'
            })
        };
    }
}
```

**6. Serverless Configuration** (`serverless.yml`)

```yaml
service: [function-name]

frameworkVersion: '3'

provider:
  name: aws
  runtime: nodejs20.x
  region: ap-southeast-2
  stage: ${opt:stage, 'dev'}
  timeout: 30
  memorySize: 1024

  environment:
    NODE_ENV: ${self:provider.stage}
    LOG_LEVEL: info

  iam:
    role:
      statements:
        # S3 Read access (for Delta tables)
        - Effect: Allow
          Action:
            - s3:GetObject
            - s3:ListBucket
          Resource:
            - arn:aws:s3:::apprise-*-data
            - arn:aws:s3:::apprise-*-data/*

        # Secrets Manager access
        - Effect: Allow
          Action:
            - secretsmanager:GetSecretValue
          Resource:
            - arn:aws:secretsmanager:ap-southeast-2:*:secret:apprise/${self:provider.stage}/*

functions:
  api:
    handler: dist/handlers/[functionName].handler
    description: [FUNCTIONALITY]
    events:
      - httpApi:
          path: /api/v1/metrics
          method: GET
          authorizer:
            type: jwt
            identitySource: $request.header.Authorization
            issuerUrl: https://cognito-idp.ap-southeast-2.amazonaws.com/${cf:auth-stack.UserPoolId}
            audience:
              - ${cf:auth-stack.UserPoolClientId}

      - httpApi:
          path: /api/v1/metrics/calculate
          method: POST
          authorizer:
            type: jwt
            identitySource: $request.header.Authorization
            issuerUrl: https://cognito-idp.ap-southeast-2.amazonaws.com/${cf:auth-stack.UserPoolId}
            audience:
              - ${cf:auth-stack.UserPoolClientId}

plugins:
  - serverless-plugin-typescript
  - serverless-offline

custom:
  serverless-offline:
    httpPort: 3000
```

---

### Phase 3: TEST (80% Coverage Target)

**Unit Test** (`tests/unit/[functionName].test.ts`)

```typescript
import { APIGatewayProxyEvent, Context } from 'aws-lambda';
import { handler } from '../../src/handlers/[functionName]';
import { [ServiceName] } from '../../src/services/[serviceName]';

// Mock service
jest.mock('../../src/services/[serviceName]');

describe('[FunctionName] Handler', () => {
    let mockService: jest.Mocked<[ServiceName]>;

    beforeEach(() => {
        mockService = new [ServiceName]() as jest.Mocked<[ServiceName]>;
        jest.clearAllMocks();
    });

    describe('GET /api/v1/metrics', () => {
        it('returns metrics for valid request', async () => {
            // Arrange
            const event: Partial<APIGatewayProxyEvent> = {
                httpMethod: 'GET',
                path: '/api/v1/metrics',
                queryStringParameters: {
                    territory: 'NSW_ACT',
                    startDate: '2025-10-01',
                    endDate: '2025-10-31'
                },
                requestContext: {
                    requestId: 'test-request-id',
                    authorizer: {
                        claims: {
                            sub: 'user-123'
                        }
                    }
                } as any
            };

            const mockMetrics = [
                { date: '2025-10-01', totalJobs: 100, completionRate: 0.95, averageDays: 5 }
            ];
            mockService.getMetrics.mockResolvedValue(mockMetrics);

            // Act
            const result = await handler(event as APIGatewayProxyEvent);

            // Assert
            expect(result.statusCode).toBe(200);
            const body = JSON.parse(result.body);
            expect(body.success).toBe(true);
            expect(body.data).toEqual(mockMetrics);
        });

        it('returns 400 for missing parameters', async () => {
            // Arrange
            const event: Partial<APIGatewayProxyEvent> = {
                httpMethod: 'GET',
                path: '/api/v1/metrics',
                queryStringParameters: {},
                requestContext: {
                    requestId: 'test-request-id',
                    authorizer: { claims: { sub: 'user-123' } }
                } as any
            };

            // Act
            const result = await handler(event as APIGatewayProxyEvent);

            // Assert
            expect(result.statusCode).toBe(400);
            const body = JSON.parse(result.body);
            expect(body.success).toBe(false);
            expect(body.error).toBe('Validation Error');
        });

        it('returns 401 for unauthorized request', async () => {
            // Arrange
            const event: Partial<APIGatewayProxyEvent> = {
                httpMethod: 'GET',
                path: '/api/v1/metrics',
                queryStringParameters: {
                    territory: 'NSW_ACT',
                    startDate: '2025-10-01',
                    endDate: '2025-10-31'
                },
                requestContext: {
                    requestId: 'test-request-id'
                } as any  // No authorizer
            };

            // Act
            const result = await handler(event as APIGatewayProxyEvent);

            // Assert
            expect(result.statusCode).toBe(401);
        });
    });

    describe('POST /api/v1/metrics/calculate', () => {
        it('calculates metrics for job numbers', async () => {
            // Arrange
            const event: Partial<APIGatewayProxyEvent> = {
                httpMethod: 'POST',
                path: '/api/v1/metrics/calculate',
                body: JSON.stringify({
                    jobNumbers: ['00295677', '00295676']
                }),
                requestContext: {
                    requestId: 'test-request-id',
                    authorizer: { claims: { sub: 'user-123' } }
                } as any
            };

            const mockResult = {
                total: 2,
                averageDays: 5,
                completionRate: '100.00'
            };
            mockService.calculateMetrics.mockResolvedValue(mockResult);

            // Act
            const result = await handler(event as APIGatewayProxyEvent);

            // Assert
            expect(result.statusCode).toBe(200);
            const body = JSON.parse(result.body);
            expect(body.success).toBe(true);
            expect(body.data).toEqual(mockResult);
        });

        it('returns 400 for invalid job numbers', async () => {
            // Arrange
            const event: Partial<APIGatewayProxyEvent> = {
                httpMethod: 'POST',
                path: '/api/v1/metrics/calculate',
                body: JSON.stringify({
                    jobNumbers: 'not-an-array'  // Invalid
                }),
                requestContext: {
                    requestId: 'test-request-id',
                    authorizer: { claims: { sub: 'user-123' } }
                } as any
            };

            // Act
            const result = await handler(event as APIGatewayProxyEvent);

            // Assert
            expect(result.statusCode).toBe(400);
        });
    });
});
```

**Run Tests**:
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

---

## Output Expected

1. **Handler**: `src/handlers/[functionName].ts`
2. **Service**: `src/services/[serviceName].ts`
3. **Utils**: Logger, ErrorHandler, Validator
4. **Tests**: Unit tests (80%+ coverage)
5. **Config**: `serverless.yml`, `tsconfig.json`
6. **Docs**: README with deployment instructions

---

## Related Templates

- Use `../workflows/data_services_api.md` for DuckDB query patterns
- Use `../core-workflows/secure_feature_development.md` for overall feature development
- Use `../core-workflows/code_review_request.md` for code review

---

**Template Version**: 1.0
**Last Updated**: October 2025
**Owner**: P&T Team / AI Approach Project
