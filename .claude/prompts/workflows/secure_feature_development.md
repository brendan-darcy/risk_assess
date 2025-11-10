# Skills: feature_development, secure_coding, testing, code_review
# SSDF Practice Group: PW (Produce Well-Secured Software), PS (Protect the Software)
# ARMATech Principles: Security, Modern, Cloud First
# Language: Multi (APEX, LWC, Node.js, Python, SQL, R)
# Context: Apprise Risk Solutions P&T Team - Primary Feature Development Template

## Security Reminder
⚠️ **CRITICAL**: This is the primary template for developing new features. All features must follow Apprise's Secure Software Development Framework (SSDF) and maintain ISO 27001:2022 compliance.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only (NOT Production)
- [ ] Using dummy test data (NO client/production data)
- [ ] Will delete Claude Code chat history after this session
- [ ] Pre-flight check passed (`./pre-flight-check.sh`)

## Placeholders
- `[COMPONENT_NAME]` - Feature component name (e.g., "Sales Evidence Rating Algorithm", "Property Data Validator")
- `[LANGUAGE]` - Programming language: APEX | LWC | Node.js/TypeScript | Python | SQL | R
- `[BUSINESS_REQUIREMENT]` - Problem this feature solves (2-3 sentences)
- `[ACCEPTANCE_CRITERIA]` - Specific, measurable completion criteria (bullet points)
- `[SECURITY_CONTROLS]` - Required OWASP controls (authentication, input validation, authorization, etc.)
- `[TEST_COVERAGE_TARGET]` - Minimum coverage: 75% (APEX), 80% (LWC/Node.js), 70% (Python/R)
- `[ARMATECH_PRINCIPLE]` - Which ARMATech principle(s) this supports: Security | Cloud First | Modern | API Integration | Distributed Computing
- `[INTEGRATION_POINTS]` - External systems/APIs this feature integrates with (if any)

---

## Task: Secure Feature Development

You are a senior software engineer at Apprise Risk Solutions working on the ARMATech valuation platform. Develop a new feature component following Apprise's Secure Software Development Framework (SSDF), secure coding standards, and architectural principles.

### Context

**Company**: Apprise Risk Solutions
- Property valuation technology platform serving Australian lending market
- Handles sensitive client data: property valuations, borrower information, financial data
- ISO 27001:2022 certified, OWASP-compliant secure coding practices
- NIST SSDF framework for secure development lifecycle

**Security Requirements**:
- ISO 27001:2022 compliance mandatory
- OWASP Top 10 controls integrated into all code
- Minimum test coverage enforced (language-specific)
- Code review required for all features
- Secrets management via environment variables, Named Credentials, or AWS Secrets Manager

**Code Quality Standards**:
- Language-specific conventions strictly followed
- Modular design with single responsibility principle
- Comprehensive test coverage (positive, negative, security scenarios)
- Clear documentation for all public interfaces
- Type safety where applicable (TypeScript strict mode, Python type hints, etc.)

**Architecture**: ARMATech Principles
- **Cloud First**: AWS (Lambda, S3, Secrets Manager) and Salesforce (Platform, Shield)
- **API-First Design**: RESTful APIs, JSON responses, versioning
- **Distributed Computing**: Browser-based processing where appropriate
- **Modern Tech Stack**: Latest LTS versions, minimal technical debt
- **Security**: Highest standards, defense in depth
- **Data-Driven**: Analytics, metrics, dashboards

---

## Feature Specification

**Component Name**: [COMPONENT_NAME]

**Programming Language**: [LANGUAGE]

**ARMATech Principle Alignment**: [ARMATECH_PRINCIPLE]

**Business Requirements**:
[BUSINESS_REQUIREMENT]

**Acceptance Criteria**:
[ACCEPTANCE_CRITERIA]

**Security Requirements**:
[SECURITY_CONTROLS]

**Integration Points**:
[INTEGRATION_POINTS]

**Test Coverage Target**: [TEST_COVERAGE_TARGET]

---

## Instructions

Follow this three-phase structure for secure feature development:

### Phase 1: PLAN (Security & Architecture Analysis)

Before writing any code, provide a comprehensive plan (8-12 bullet points) covering:

**Architecture & Design**:
- High-level approach to implementing the feature
- Component/class structure and responsibilities
- Data flow between components
- Integration points with existing systems
- Dependencies and libraries required

**Security Analysis**:
- Which OWASP Top 10 vulnerabilities are relevant?
- Authentication/authorization requirements
- Input validation strategy (what data needs validation?)
- Secrets management approach (credentials, API keys, tokens)
- Error handling strategy (no sensitive data in errors)
- Logging requirements (what to log, what NOT to log)

**Architecture Alignment**:
- How does this align with ARMATech principles?
- Cloud services utilized (AWS Lambda, S3, Salesforce Platform)
- API design considerations (RESTful patterns, versioning)
- Performance considerations (caching, query optimization)

**Testing Strategy**:
- Test scenarios (positive, negative, security, edge cases)
- Test data generation approach (dummy data only)
- Coverage targets and how to achieve them
- Integration testing requirements

**Risks & Mitigations**:
- Potential risks (security, performance, compatibility)
- Mitigation strategies for each risk
- Rollback considerations

---

### Phase 2: BUILD (Secure Implementation)

Generate production-ready code with all security controls, quality standards, and testing integrated.

---

#### Security Requirements (MANDATORY)

**1. NO Hardcoded Credentials**
```
❌ BAD:
const API_KEY = 'sk-1234567890abcdef';
const PASSWORD = 'MySecret123';

✅ GOOD:
// Node.js/Python
const API_KEY = process.env.API_KEY;  // or AWS Secrets Manager

// APEX
String apiKey = [SELECT ApiKey__c FROM ApiCredential__mdt WHERE DeveloperName = 'PropTrack'].ApiKey__c;

// Use Named Credentials for external APIs
HttpRequest req = new HttpRequest();
req.setEndpoint('callout:PropTrack_API/v1/properties');
```

**2. Input Validation (All User Inputs & External Data)**
```
✅ Validate ALL inputs before processing:
- Type validation (string, number, date, email, URL)
- Format validation (regex patterns, allowed characters)
- Range validation (min/max values, length limits)
- Business rule validation (valid territory, valid status)
- Sanitization (remove dangerous characters)

Examples:
// APEX
String sanitizedInput = String.escapeSingleQuotes(userInput);
if (!Pattern.matches('[a-zA-Z0-9\\s]+', sanitizedInput)) {
    throw new IllegalArgumentException('Invalid input format');
}

// TypeScript
import validator from 'validator';
if (!validator.isEmail(email)) {
    throw new ValidationError('Invalid email format');
}

// Python
import re
if not re.match(r'^[A-Z]{2,3}_[A-Z]{3}$', territory):
    raise ValueError('Invalid territory format')
```

**3. Parameterized Queries (NO String Concatenation)**
```
❌ BAD (SQL Injection vulnerability):
String query = 'SELECT Id FROM Account WHERE Name = \'' + accountName + '\'';
List<Account> accounts = Database.query(query);

✅ GOOD (Parameterized):
List<Account> accounts = [SELECT Id FROM Account WHERE Name = :accountName];
```

**4. Proper Error Handling (NO Sensitive Data in Errors)**
```
❌ BAD:
catch (Exception e) {
    System.debug('Error with user john.smith@example.com: ' + e.getMessage());
    throw new CustomException('Database error: ' + e.getMessage());  // May expose DB structure
}

✅ GOOD:
catch (Exception e) {
    System.debug(LoggingLevel.ERROR, 'Feature X error: ' + e.getMessage());  // Logs for debugging
    throw new CustomException('Unable to process request. Please contact support.');  // Generic user message
}
```

**5. Authentication/Authorization Checks**
```
✅ Verify user permissions before operations:
// APEX
if (!Schema.sObjectType.Account.isAccessible()) {
    throw new SecurityException('Insufficient permissions');
}

// LWC
import { getRecord } from 'lightning/uiRecordApi';
// Lightning Data Service enforces FLS/CRUD

// Node.js (Lambda with API Gateway)
if (!event.requestContext.authorizer.claims) {
    return {
        statusCode: 401,
        body: JSON.stringify({ error: 'Unauthorized' })
    };
}
```

**6. Secure Random Values (if applicable)**
```
❌ BAD:
String token = String.valueOf(Math.random());  // Predictable

✅ GOOD:
Blob randomBytes = Crypto.generateAesKey(128);
String token = EncodingUtil.base64Encode(randomBytes);
```

**7. HTTPS Only (All Network Calls)**
```
✅ Enforce HTTPS:
// APEX
req.setEndpoint('https://api.example.com/v1/data');  // https:// required

// Node.js
const https = require('https');
// or axios with https enforcement
```

---

#### Code Quality Requirements

**Language-Specific Standards**:

**APEX**:
- Salesforce naming standards (PascalCase for classes, camelCase for methods/variables)
- SFDX Prettier configuration
- Bulkified design (collections, not single records)
- Governor limits awareness (SOQL queries < 100, DML statements < 150, heap size < 6MB)
- `with sharing` keyword for classes (enforce sharing rules)
- Minimum 75% test coverage

**LWC (Lightning Web Components)**:
- SFDX naming conventions (kebab-case for component folders, camelCase for JS)
- ESLint + Prettier
- Lightning Data Service where possible (automatic FLS/CRUD)
- `@api`, `@track`, `@wire` decorators used appropriately
- Error handling with LightningAlert or toast notifications
- Accessibility (ARIA labels, semantic HTML, keyboard navigation)
- Minimum 80% test coverage

**Node.js/TypeScript**:
- ESLint configuration (matching LWC standards where applicable)
- TypeScript strict mode (`strict: true` in tsconfig.json)
- Async/await patterns (avoid callback hell)
- Environment variable management (dotenv, AWS Parameter Store)
- Structured logging (JSON format for CloudWatch)
- AWS SDK v3 (modular imports)
- Minimum 80% test coverage

**Python (Databricks)**:
- PEP 8 standards (enforced by Black or autopep8)
- Type hints for function signatures
- Docstrings for all public functions (Google or NumPy style)
- Databricks notebook structure (imports → config → functions → execution)
- Virtual environment or conda for dependencies
- Minimum 70% test coverage

**SQL (Databricks)**:
- Databricks SQL auto-formatting
- Parameterized queries (using placeholders)
- Query optimization (partition pruning, broadcast joins)
- Clear table/column naming (lowercase with underscores)
- Comments for complex queries

**R (POSIT)**:
- Tidyverse style guide
- POSIT environment conventions
- `renv` for package management
- R Markdown for reproducible reports
- Clear function documentation (roxygen2 style)
- Minimum 70% test coverage

**General Code Quality**:
- Clear docstrings/comments explaining complex logic (not obvious code)
- Type hints where applicable (TypeScript, Python, R)
- Meaningful variable and function names (no single letters except loop counters)
- Modular design with single responsibility principle
- DRY (Don't Repeat Yourself) - extract reusable functions
- Maximum function length: ~50 lines (refactor if longer)
- Maximum class length: ~300 lines (refactor if longer)

---

#### Testing Requirements

Generate comprehensive tests achieving minimum coverage target: **[TEST_COVERAGE_TARGET]**

**Test Scenarios (MANDATORY)**:

**1. Positive Scenarios (Happy Path)**:
- Valid inputs produce expected outputs
- All acceptance criteria verified
- Normal workflow completes successfully

**2. Negative Scenarios (Error Handling)**:
- Invalid inputs handled gracefully
- Null/undefined/empty values handled
- Boundary conditions tested (min/max values, empty lists)
- Missing required fields rejected
- Malformed data rejected

**3. Security Scenarios**:
- Unauthorized access attempts blocked
- SQL/SOQL injection attempts fail
- XSS attempts sanitized
- Invalid tokens rejected
- Insufficient permissions handled

**4. Edge Cases**:
- Large data volumes (performance testing)
- Concurrent operations (race conditions)
- Network failures (retry logic, timeouts)
- External API failures (graceful degradation)

**Test Data**:
- ⚠️ **CRITICAL**: Use DUMMY DATA ONLY (no client/production data)
- Generate realistic synthetic test data
- Use factories or builders for test objects
- Parameterized tests for multiple scenarios

**Test Structure**:
```
// APEX Test Structure
@isTest
private class [ComponentName]Test {
    @TestSetup
    static void setup() {
        // Create test data
    }

    @isTest
    static void testPositiveScenario() { ... }

    @isTest
    static void testNegativeScenario() { ... }

    @isTest
    static void testSecurityScenario() { ... }
}

// Jest Test Structure (LWC/Node.js)
describe('[ComponentName]', () => {
    beforeEach(() => {
        // Setup
    });

    it('should handle valid input', () => { ... });

    it('should reject invalid input', () => { ... });

    it('should prevent unauthorized access', () => { ... });
});

// Python Test Structure (pytest)
class Test[ComponentName]:
    def setup_method(self):
        # Setup

    def test_positive_scenario(self):
        # Test

    def test_negative_scenario(self):
        # Test

    def test_security_scenario(self):
        # Test
```

**Test Independence**:
- Tests must be independent (no shared state)
- Tests must be repeatable (same result every time)
- Tests must be fast (< 1 second per test ideally)
- Mock external dependencies (APIs, databases, file systems)

---

### Phase 3: EXPLAIN (Documentation)

Provide comprehensive documentation for the feature:

**1. Implementation Summary** (3-5 sentences):
- Brief explanation of the approach taken
- Key design decisions and rationale
- Trade-offs considered

**2. Security Controls Implemented**:
- List all OWASP controls applied
- Authentication/authorization approach
- Input validation strategy
- Secrets management implementation
- Logging approach (what's logged, what's excluded)

**3. How to Run Tests Locally**:
```bash
# APEX
sfdx force:apex:test:run -n [ComponentName]Test -r human

# LWC
npm test -- [componentName].test.js

# Node.js
npm test

# Python
pytest tests/test_[component_name].py -v

# R
testthat::test_file("tests/testthat/test_[component_name].R")
```

**4. Configuration Requirements**:
- Environment variables needed (with example values, NOT real secrets):
  ```
  API_KEY=<your_api_key_here>
  API_ENDPOINT=https://api.example.com/v1
  AWS_REGION=ap-southeast-2
  ```
- Named Credentials (APEX): `[CredentialName]`
- AWS Secrets: `apprise/[environment]/[secret_name]`
- Feature flags or custom metadata

**5. Deployment Considerations**:
- **Dev → UAT**: Deployment steps, configuration changes, test scenarios
- **UAT → Prod**: Final verification checklist, rollback plan
- Database migrations (if any)
- External service dependencies
- Backward compatibility notes

**6. Monitoring & Logging**:
- Key metrics to monitor (success rate, latency, error rate)
- CloudWatch logs to review (Lambda)
- Salesforce debug logs to check
- Alerts to configure (error thresholds)

**7. Known Limitations** (if any):
- Performance constraints
- Scalability limits
- Browser/platform compatibility
- Future enhancements planned

---

## Output Expected

Deliver the following files:

### 1. Implementation File
**Filename**: `[component_name].[extension]`

**Contents**:
- Production-ready code with inline comments
- All security controls implemented
- Modular design (single responsibility functions/classes)
- Type safety (where applicable)
- Error handling throughout

**Example**:
- APEX: `SalesEvidenceRatingService.cls`
- LWC: `salesEvidenceRating/salesEvidenceRating.js`
- Node.js: `src/services/salesEvidenceRatingService.ts`
- Python: `sales_evidence_rating_service.py`

### 2. Test File
**Filename**: `test_[component_name].[extension]` or `[component_name]Test.cls`

**Contents**:
- Comprehensive test coverage achieving target
- Test setup/teardown (dummy data generation)
- Positive, negative, security, edge case scenarios
- Clear test names describing what's being tested
- Assertions with meaningful error messages

**Example**:
- APEX: `SalesEvidenceRatingServiceTest.cls`
- LWC: `salesEvidenceRating/__tests__/salesEvidenceRating.test.js`
- Node.js: `tests/services/salesEvidenceRatingService.test.ts`
- Python: `tests/test_sales_evidence_rating_service.py`

### 3. Documentation File
**Filename**: `README_[component_name].md`

**Contents**:
- Purpose and functionality (what problem does this solve?)
- Security controls implemented (OWASP checklist)
- Configuration requirements (env vars, credentials, settings)
- How to run tests locally (commands with examples)
- Deployment notes (dev → UAT → prod)
- Monitoring and logging guidance
- Known limitations and future enhancements

---

## Example Usage

Here's a realistic Apprise scenario with all placeholders filled:

### Scenario: Sales Evidence Rating Algorithm

**Component Name**: Sales Evidence Rating Algorithm

**Language**: Python

**ARMATech Principle**: Modern (reducing technical debt in legacy rating system)

**Business Requirements**:
The current sales evidence rating system is manual and inconsistent. We need an automated algorithm that rates sales evidence quality (1-5 stars) based on recency, relevance, and completeness. This will improve valuation accuracy and reduce manual review time.

**Acceptance Criteria**:
- Rate evidence with age <90 days as 5 stars
- Rate evidence with age 90-180 days as 4 stars
- Rate evidence with age 180-365 days as 3 stars
- Rate evidence with age >365 days as 1-2 stars
- Consider property type match in rating (house vs unit)
- Consider sale type (open market vs distressed)
- Return rating (1-5 stars) and confidence score (0-1)
- Handle missing data gracefully (default to lower rating)

**Security Requirements**:
- Input validation on property data (address, sale price, date)
- No PII in logs (mask address, sale price)
- Validate date formats (prevent injection)
- Error handling (no stack traces to end users)

**Integration Points**:
- Reads from `gold.sales_evidence` Delta table in Databricks
- Writes ratings to `gold.sales_evidence_ratings` table
- Called by valuation workflow API

**Test Coverage Target**: 70% (Python)

### Expected Output

**File 1**: `sales_evidence_rating_service.py` (implementation)
```python
from typing import Dict, Optional
from datetime import datetime, timedelta
from pyspark.sql import DataFrame
import pyspark.sql.functions as F

class SalesEvidenceRatingService:
    """Service for rating sales evidence quality based on recency, relevance, and completeness."""

    def rate_evidence(
        self,
        evidence_age_days: int,
        property_type_match: bool,
        sale_type: str,
        completeness_score: float
    ) -> Dict[str, float]:
        """
        Rate sales evidence quality.

        Args:
            evidence_age_days: Days since sale date
            property_type_match: True if property types match
            sale_type: 'open_market', 'distressed', 'family_transfer'
            completeness_score: 0-1 score for data completeness

        Returns:
            Dict with 'rating' (1-5 stars) and 'confidence' (0-1)
        """
        # Input validation
        if evidence_age_days < 0:
            raise ValueError("Evidence age cannot be negative")
        if not 0 <= completeness_score <= 1:
            raise ValueError("Completeness score must be between 0 and 1")

        # Base rating on age
        if evidence_age_days < 90:
            base_rating = 5.0
        elif evidence_age_days < 180:
            base_rating = 4.0
        elif evidence_age_days < 365:
            base_rating = 3.0
        else:
            base_rating = 1.5

        # Adjust for property type match
        if not property_type_match:
            base_rating -= 0.5

        # Adjust for sale type
        if sale_type == 'distressed':
            base_rating -= 1.0
        elif sale_type == 'family_transfer':
            base_rating -= 1.5

        # Adjust for completeness
        base_rating *= completeness_score

        # Clamp to 1-5 range
        rating = max(1.0, min(5.0, base_rating))

        # Calculate confidence (higher for recent, complete data)
        confidence = (completeness_score * 0.5) + (self._age_confidence(evidence_age_days) * 0.5)

        return {
            'rating': round(rating, 1),
            'confidence': round(confidence, 2)
        }

    def _age_confidence(self, age_days: int) -> float:
        """Calculate confidence based on evidence age."""
        if age_days < 90:
            return 1.0
        elif age_days < 180:
            return 0.8
        elif age_days < 365:
            return 0.5
        else:
            return 0.2
```

**File 2**: `tests/test_sales_evidence_rating_service.py` (tests)
**File 3**: `README_sales_evidence_rating.md` (documentation)

---

## Related Templates

**After Feature Development**:
- Use `code_review_request.md` to request code review from Claude
- Use `../security/security_review.md` for comprehensive security audit
- Use `refactoring_workflow.md` if technical debt needs addressing

**Before Deployment**:
- Review `../security/_security_checklist.md` one final time
- Run `./pre-flight-check.sh` to verify environment
- Delete Claude Code chat history

---

## Notes

**Common Mistakes to Avoid**:
- ❌ Hardcoding credentials in code
- ❌ String concatenation for SQL/SOQL queries
- ❌ Exposing sensitive data in error messages or logs
- ❌ Skipping input validation ("trust the input")
- ❌ Low test coverage (below targets)
- ❌ Missing security scenarios in tests
- ❌ Committing .env files or credentials

**Best Practices**:
- ✅ Plan before coding (architecture, security, testing)
- ✅ Use language-specific standards consistently
- ✅ Test early and often (TDD approach)
- ✅ Document as you go (don't leave it to the end)
- ✅ Review OWASP Top 10 before starting
- ✅ Use secrets management from day one
- ✅ Consider performance and scalability

**Success Indicators**:
- All acceptance criteria met
- Test coverage target achieved
- Security checklist complete
- Code review passes on first attempt
- No security vulnerabilities found
- Clear documentation for maintenance

---

**Template Version**: 1.0
**Last Updated**: October 2025
**Owner**: P&T Team / AI Approach Project
