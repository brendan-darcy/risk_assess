# Skills: security, code_review, static_analysis, vulnerability_assessment
# SSDF Practice Group: RV (Respond to Vulnerabilities)
# ARMATech Principles: Security
# Language: Multi-language (APEX, LWC, Node.js, TypeScript, Python, SQL, R)
# Context: Apprise Risk Solutions P&T Team - Security Code Review

## Security Reminder
⚠️ **CRITICAL**: This template helps identify security vulnerabilities. Findings must be triaged and remediated before production deployment.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only
- [ ] Using dummy test data (NO client data)
- [ ] Will delete Claude Code chat history after this session

## Placeholders
- `[FILE_PATH]` - Path to file(s) to review (e.g., "src/services/ValuationService.ts")
- `[REVIEW_SCOPE]` - OWASP | LANGUAGE_SPECIFIC | TEST_COVERAGE | ALL
- `[SEVERITY_THRESHOLD]` - CRITICAL | HIGH | MEDIUM | LOW | ALL
- `[OUTPUT_FORMAT]` - MARKDOWN | JSON | HTML

---

## Task: Perform Comprehensive Security Code Review

You are a security engineer at Apprise Risk Solutions performing a comprehensive security code review to identify vulnerabilities and ensure compliance with secure coding standards.

This review supports SSDF RV.1 (Identify and confirm vulnerabilities) and integrates with Apprise's code review process (SEH Section 4.4).

### Context
- **Requirement**: All code changes must undergo security review before merge
- **Compliance**: OWASP Top 10, ISO 27001:2022, Apprise Secure Coding Standards
- **Risk**: Vulnerabilities in production code can lead to data breaches, unauthorized access
- **Integration**: Part of PR review process, triggered by reviewers or developers
- **Scope**: Review APEX, LWC, Node.js, TypeScript, Python, SQL, R code

---

## Instructions

### 1. ANALYZE
Review the provided code files for security vulnerabilities in these categories:

**OWASP Top 10:2021 Coverage**:
- **A01:2021** - Broken Access Control
- **A02:2021** - Cryptographic Failures
- **A03:2021** - Injection (SQL, XSS, Command)
- **A04:2021** - Insecure Design
- **A05:2021** - Security Misconfiguration
- **A06:2021** - Vulnerable and Outdated Components
- **A07:2021** - Identification and Authentication Failures
- **A08:2021** - Software and Data Integrity Failures
- **A09:2021** - Security Logging and Monitoring Failures
- **A10:2021** - Server-Side Request Forgery (SSRF)

**Language-Specific Anti-Patterns**:

1. **APEX (Salesforce)**:
   - SOQL/SOSL injection vulnerabilities
   - Missing sharing keywords (with sharing, without sharing)
   - FLS/CRUD violations (Field-Level Security, Object permissions)
   - Governor limit risks (queries in loops, DML in loops)
   - Hardcoded IDs or credentials
   - Missing null checks
   - Unsafe dynamic SOQL/DML

2. **LWC (Lightning Web Components)**:
   - XSS vulnerabilities (innerHTML, unsafe DOM manipulation)
   - Missing Lightning Locker Service compatibility
   - Improper wire service error handling
   - Missing @api property validation
   - Client-side validation only (no server-side backup)
   - Exposed sensitive data in client-side code
   - Missing CSP (Content Security Policy) compliance

3. **Node.js / TypeScript**:
   - SQL injection (if using raw queries)
   - NoSQL injection (MongoDB, DynamoDB)
   - Command injection (exec, spawn with user input)
   - Path traversal (fs operations with user input)
   - Prototype pollution
   - Insecure dependencies (npm audit)
   - Missing input validation
   - Hardcoded secrets or credentials
   - Missing rate limiting
   - Insecure session management

4. **Python (Databricks)**:
   - SQL injection (raw SQL strings)
   - Command injection (os.system, subprocess with shell=True)
   - Pickle deserialization vulnerabilities
   - Path traversal (file operations)
   - Missing pandas/numpy input validation
   - Insecure credential storage
   - Missing logging for security events

5. **SQL**:
   - SQL injection (dynamic SQL, concatenation)
   - Missing parameterization
   - Excessive permissions (SELECT *, GRANT ALL)
   - Missing WHERE clauses (unintentional full table operations)
   - Stored procedures without validation

6. **R**:
   - Command injection (system() calls)
   - Unsafe eval() usage
   - Missing input validation for data frames
   - Path traversal in file operations

**Test Coverage Gaps**:
- Security test coverage for authentication/authorization
- Negative test cases (invalid input, boundary conditions)
- Injection attack test cases
- Error handling test cases

**Apprise-Specific Concerns**:
- Client data exposure risks (PII, valuation data)
- Integration security (Salesforce ↔ AWS, Databricks ↔ Salesforce)
- Named Credentials usage (Salesforce)
- Secrets Manager usage (AWS)
- API authentication patterns
- Logging of sensitive data

### 2. CLASSIFY
For each finding, provide:

**Severity Classification**:
- **CRITICAL**: Immediate data breach risk, authentication bypass, RCE
  - Examples: SQL injection in production, hardcoded admin credentials, authentication bypass
- **HIGH**: Significant security risk, potential for exploitation
  - Examples: XSS vulnerabilities, missing access control, insecure crypto
- **MEDIUM**: Security weakness, exploitation requires specific conditions
  - Examples: Information disclosure, missing rate limiting, weak validation
- **LOW**: Security improvement opportunity, minimal immediate risk
  - Examples: Missing security headers, weak error messages, code quality issues

**Finding Details**:
- **Vulnerability Type**: OWASP category, CWE ID if applicable
- **Location**: File path, line numbers, function name
- **Risk**: What could an attacker exploit?
- **Impact**: What data/systems could be compromised?
- **Proof of Concept**: Example exploit scenario (if safe to demonstrate)
- **Remediation**: Specific code fix with example

### 3. REPORT
Generate a comprehensive security review report with:

**Executive Summary**:
- Total findings by severity
- High-level risk assessment
- Approval recommendation (APPROVE, APPROVE WITH CONDITIONS, REJECT)

**Detailed Findings**:
- Grouped by severity (Critical → Low)
- Each finding with location, description, remediation
- Code snippets showing vulnerable code and fixed code

**Recommendations**:
- Priority order for remediation
- Testing recommendations
- Long-term security improvements

---

## Output Expected

### Security Review Report Structure

```markdown
# Security Code Review Report

**Project**: [PROJECT_NAME]
**Reviewed By**: Claude Code Security Review
**Review Date**: [DATE]
**Files Reviewed**: [FILE_LIST]
**Scope**: [REVIEW_SCOPE]

---

## Executive Summary

**Overall Risk Level**: [CRITICAL | HIGH | MEDIUM | LOW]

**Findings Summary**:
- 🔴 Critical: X findings
- 🟠 High: X findings
- 🟡 Medium: X findings
- 🟢 Low: X findings

**Recommendation**: [APPROVE | APPROVE WITH CONDITIONS | REJECT]

**Rationale**: [Brief explanation of recommendation]

---

## Critical Findings

### [C-1] SQL Injection in Valuation Query

**Severity**: 🔴 CRITICAL
**OWASP Category**: A03:2021 - Injection
**CWE ID**: CWE-89
**File**: src/services/ValuationService.ts:142-145

**Vulnerable Code**:
```typescript
// ❌ CRITICAL: SQL injection vulnerability
async getValuationByAddress(address: string) {
  const query = `SELECT * FROM valuations WHERE address = '${address}'`;
  return await db.query(query);
}
```

**Risk**: Attacker can inject malicious SQL to access all valuation records, modify data, or execute arbitrary database commands.

**Proof of Concept**:
```
address = "' OR '1'='1'; DROP TABLE valuations; --"
Result: All valuation data exposed or deleted
```

**Impact**:
- Data breach: Exposure of all client valuation data
- Data loss: Potential database destruction
- Compliance violation: ISO 27001:2022, ISMS policies

**Remediation**:
```typescript
// ✅ FIXED: Use parameterized query
async getValuationByAddress(address: string) {
  // Validate input first
  const validated = validateAddress(address);
  if (!validated.isValid) {
    throw new ValidationError(validated.errorMessage);
  }

  // Use parameterized query
  const query = 'SELECT * FROM valuations WHERE address = ?';
  return await db.query(query, [validated.sanitizedValue]);
}
```

**Verification**:
- [ ] Unit test with SQL injection payloads
- [ ] Integration test with edge cases
- [ ] Manual testing by reviewer

**Priority**: 🚨 IMMEDIATE - Must fix before merge

---

## High Findings

### [H-1] Missing APEX Sharing Declaration

**Severity**: 🟠 HIGH
**OWASP Category**: A01:2021 - Broken Access Control
**File**: force-app/main/default/classes/ValuationController.cls:1

**Vulnerable Code**:
```apex
// ❌ HIGH: No sharing keyword - may expose unauthorized data
public class ValuationController {
    @AuraEnabled
    public static List<Valuation__c> getValuations() {
        return [SELECT Id, Address__c, Amount__c FROM Valuation__c];
    }
}
```

**Risk**: Without sharing enforcement, users may access valuation records they shouldn't see, violating record-level security.

**Impact**:
- Data breach: Users see other users' valuations
- Compliance violation: ISMS 3 (Information Classification)

**Remediation**:
```apex
// ✅ FIXED: Add 'with sharing' keyword
public with sharing class ValuationController {
    @AuraEnabled
    public static List<Valuation__c> getValuations() {
        return [SELECT Id, Address__c, Amount__c FROM Valuation__c];
    }
}
```

**Additional Checks**:
- Add FLS/CRUD checks using `Security.stripInaccessible()`
- Add unit test verifying sharing behavior with different user profiles

**Priority**: ⚠️ HIGH - Fix before production deployment

---

## Medium Findings

### [M-1] Missing Input Validation in API Endpoint

[Similar structure as above...]

---

## Low Findings

### [L-1] Missing Security Headers

[Similar structure as above...]

---

## Test Coverage Analysis

**Current Coverage**: [X]%
**Target Coverage**:
- APEX: 75%
- LWC: 80%
- Node.js: 80%
- Python: 70%

**Security Test Gaps**:
- ❌ No SQL injection test cases
- ❌ No XSS test cases
- ❌ Missing authentication test coverage
- ✅ Basic input validation tests present

**Recommendations**:
1. Add security-focused test suite (see test recommendations below)
2. Implement integration tests for authentication flows
3. Add negative test cases for all input validation

---

## Recommendations

### Immediate Actions (Before Merge)
1. **Fix all Critical findings** - Block merge until resolved
2. **Review High findings** - Must have remediation plan
3. **Update tests** - Add security test coverage

### Short-Term (Within Sprint)
1. Fix Medium findings
2. Implement automated security scanning (see secrets_detection.md)
3. Add pre-commit hooks for common vulnerabilities

### Long-Term (Within Quarter)
1. Security training for development team
2. Implement SAST/DAST in CI/CD
3. Conduct penetration testing
4. Review and update secure coding standards

---

## Approval Decision

**Status**: [APPROVED | APPROVED WITH CONDITIONS | REJECTED]

**Conditions** (if applicable):
- [ ] All Critical findings resolved and tested
- [ ] High findings have remediation plan with timeline
- [ ] Security tests added with >80% coverage
- [ ] Code re-reviewed after fixes

**Sign-off**:
- Developer: [NAME]
- Reviewer: [NAME]
- InfoSec (if required): [NAME]

---

## Compliance Checklist

- [ ] OWASP Top 10 review completed
- [ ] Language-specific anti-patterns checked
- [ ] Test coverage validated
- [ ] Secrets detection run (no hardcoded credentials)
- [ ] Input validation verified
- [ ] Access control reviewed
- [ ] Logging and monitoring adequate
- [ ] ISMS policy compliance confirmed

---

## Appendix: Testing Recommendations

### Security Test Suite to Add

**SQL Injection Tests**:
```typescript
describe('ValuationService - SQL Injection Prevention', () => {
  it('should reject SQL injection in address field', async () => {
    const maliciousInput = "'; DROP TABLE valuations; --";
    await expect(
      service.getValuationByAddress(maliciousInput)
    ).rejects.toThrow(ValidationError);
  });

  it('should reject SQL injection with UNION', async () => {
    const maliciousInput = "' UNION SELECT * FROM users --";
    await expect(
      service.getValuationByAddress(maliciousInput)
    ).rejects.toThrow(ValidationError);
  });
});
```

**XSS Tests** (for LWC):
```javascript
describe('ValuationCard - XSS Prevention', () => {
  it('should sanitize HTML in address field', () => {
    const maliciousAddress = '<script>alert("XSS")</script>';
    const element = createElement('c-valuation-card', {
      is: ValuationCard
    });
    element.address = maliciousAddress;
    document.body.appendChild(element);

    // Verify script tag not present in DOM
    const rendered = element.shadowRoot.querySelector('.address');
    expect(rendered.innerHTML).not.toContain('<script>');
    expect(rendered.textContent).toBe(maliciousAddress); // Text only
  });
});
```

**APEX Sharing Tests**:
```apex
@IsTest
private class ValuationControllerTest {
    @IsTest
    static void testSharingEnforced() {
        // Create test data owned by User A
        User userA = TestDataFactory.createUser('Standard User');
        Valuation__c valuation = TestDataFactory.createValuation(userA.Id);

        // Query as User B (should not see User A's records)
        User userB = TestDataFactory.createUser('Standard User');
        System.runAs(userB) {
            List<Valuation__c> results = ValuationController.getValuations();
            // Assert userB cannot see userA's valuation
            System.assertEquals(0, results.size(),
                'User B should not see User A records due to sharing');
        }
    }
}
```

---
```

---

## Example Usage

### Command Line Usage

```bash
# Review specific file
claude-code-review --file src/services/ValuationService.ts

# Review entire PR
claude-code-review --pr 123

# Review with specific scope
claude-code-review --scope OWASP --severity HIGH

# Generate JSON report for CI/CD
claude-code-review --format JSON --output security-report.json
```

### In Claude Code Conversation

**Example 1: Review APEX Class**

```
I need you to perform a comprehensive security review using the security_review.md template.

Review this APEX class for OWASP vulnerabilities and Salesforce-specific issues:

[FILE_PATH]: force-app/main/default/classes/ValuationIntegrationService.cls
[REVIEW_SCOPE]: ALL
[SEVERITY_THRESHOLD]: MEDIUM

Focus on:
- SOQL injection
- Sharing enforcement
- FLS/CRUD compliance
- Hardcoded credentials
- Error handling
```

**Example 2: Review Node.js Lambda Function**

```
Using security_review.md, review this Lambda function:

[FILE_PATH]: src/lambda/processValuation.ts
[REVIEW_SCOPE]: OWASP
[SEVERITY_THRESHOLD]: HIGH

Check for:
- SQL/NoSQL injection
- Input validation
- Secrets management (should use Secrets Manager)
- Error information disclosure
- API authentication
```

**Example 3: Review PR Before Merge**

```
Perform a security review on all files in this PR:

Files changed:
- src/controllers/ValuationController.ts
- src/services/PropertyService.ts
- src/components/valuationForm.js

Use security_review.md template. Generate MARKDOWN report.
Focus on injection attacks and authentication issues.
Block merge if any CRITICAL findings.
```

---

## Apprise-Specific Review Scenarios

### Scenario 1: Reviewing Salesforce Integration Code

**Context**: Developer created new APEX REST API to receive valuation requests from external system

**Security Concerns**:
- Authentication: Is API properly authenticated?
- Authorization: Does it enforce org sharing rules?
- Input validation: Are incoming JSON fields validated?
- Rate limiting: Protected against DoS?
- Logging: Are requests logged for audit?

**Review Checklist**:
```apex
// Check for these patterns:
@RestResource(urlMapping='/api/valuation/*')
global with sharing class ValuationAPI {  // ✅ 'with sharing' present

    @HttpPost
    global static Response createValuation(Request req) {
        // ✅ Check: Input validation
        if (String.isBlank(req.address)) {
            return new Response(400, 'Address required');
        }

        // ✅ Check: FLS/CRUD
        if (!Schema.sObjectType.Valuation__c.isCreateable()) {
            throw new SecurityException('No create access');
        }

        // ✅ Check: No hardcoded values
        String apiKey = getApiKeyFromCustomMetadata(); // Not hardcoded

        // ✅ Check: Parameterized SOQL
        List<Valuation__c> existing = [
            SELECT Id FROM Valuation__c
            WHERE Address__c = :req.address  // Bound variable
        ];
    }
}
```

### Scenario 2: Reviewing Node.js Lambda for AWS Integration

**Context**: Lambda function queries RDS database and calls Salesforce API

**Security Concerns**:
- Credentials: Using Secrets Manager or hardcoded?
- SQL injection: Parameterized queries?
- Salesforce auth: OAuth flow or hardcoded token?
- Error handling: Does it expose sensitive stack traces?
- Input validation: Are inputs from API Gateway validated?

**Review Checklist**:
```typescript
export const handler = async (event: APIGatewayEvent) => {
  // ✅ Check: Input validation
  const body = JSON.parse(event.body || '{}');
  const validated = validateValuationRequest(body);
  if (!validated.isValid) {
    return { statusCode: 400, body: validated.error };
  }

  // ✅ Check: Secrets from Secrets Manager
  const dbCreds = await getSecretValue('prod/rds/credentials');
  // NOT: const dbCreds = { user: 'admin', password: 'P@ssw0rd' };

  // ✅ Check: Parameterized query
  const result = await db.query(
    'SELECT * FROM valuations WHERE id = ?',
    [validated.id]  // Parameterized
  );

  // ✅ Check: Error handling doesn't expose internals
  try {
    await salesforceClient.upsertValuation(result);
  } catch (error) {
    logger.error('Salesforce API error', { requestId: event.requestId });
    // NOT: return { statusCode: 500, body: error.stack };
    return { statusCode: 500, body: 'Internal server error' };
  }
};
```

### Scenario 3: Reviewing Databricks Python Notebook

**Context**: Python notebook processes valuation data from S3 and writes to Databricks Delta table

**Security Concerns**:
- Credentials: Using dbutils.secrets or hardcoded?
- SQL injection: Dynamic SQL with f-strings?
- Data masking: PII protection?
- File access: Path traversal risks?

**Review Checklist**:
```python
# ✅ Check: Secrets from Databricks Secret Scope
aws_access_key = dbutils.secrets.get(scope="aws", key="access_key")
# NOT: aws_access_key = "AKIAIOSFODNN7EXAMPLE"

# ✅ Check: Parameterized Spark SQL
from pyspark.sql import functions as F

df = spark.read.parquet(f"s3://bucket/{validated_path}")

# ✅ Check: No dynamic SQL with user input
query = """
  SELECT * FROM valuations
  WHERE address = :address
"""
result = spark.sql(query, {"address": user_input})  # Parameterized

# NOT: query = f"SELECT * FROM valuations WHERE address = '{user_input}'"

# ✅ Check: Data masking for PII
from pyspark.sql.functions import sha2, regexp_replace

masked_df = df.withColumn(
  "borrower_name",
  regexp_replace("borrower_name", ".+", "[REDACTED]")
)
```

---

## Integration with Apprise SDLC

**Design Phase** (SEH Module 2.2):
- Security design review using threat modeling
- Identify sensitive data flows
- Document security controls needed

**Development Phase** (SEH Module 3):
- Developer performs self-review using this template before PR
- Addresses obvious security issues proactively

**Code Review Phase** (SEH Module 4.4):
- **Mandatory**: All PRs undergo security review
- Use this template to guide review
- Document findings in PR comments
- Block merge if Critical findings unresolved

**Testing Phase** (SEH Module 5):
- Validate security test coverage
- Run automated security scans
- Perform manual penetration testing for high-risk features

**Deployment Phase** (SEH Module 6.5):
- Final security checklist verification
- CAB review includes security assessment
- Sign-off required for Critical/High findings

---

## SSDF Compliance (RV Practice Group)

**RV.1: Identify and Confirm Vulnerabilities**
- ✅ Automated: Secrets detection, SAST tools
- ✅ Manual: This security review template
- ✅ Continuous: Pre-commit hooks, CI/CD integration

**RV.2: Assess, Prioritize, and Remediate Vulnerabilities**
- ✅ Severity classification (Critical → Low)
- ✅ Remediation guidance with code examples
- ✅ Priority order based on risk

**RV.3: Analyze Vulnerabilities to Identify Root Causes**
- ✅ Root cause analysis in report
- ✅ Recommendations for systemic improvements
- ✅ Training needs identified

**Evidence for Audits**:
- Security review reports for all PRs
- Tracking of findings remediation (Jira tickets)
- Test coverage reports showing security tests
- Pre-commit hook configurations

---

## Quick Reference: Common Vulnerabilities by Language

### APEX Top 5
1. **SOQL Injection**: Use `:boundVariable`, not string concatenation
2. **Missing Sharing**: Add `with sharing` to controllers
3. **FLS/CRUD Violations**: Use `Security.stripInaccessible()` or `Schema` checks
4. **Hardcoded IDs**: Use Custom Metadata or Custom Settings
5. **Queries in Loops**: Bulkify with collections

### LWC Top 5
1. **XSS**: Never use `innerHTML` with user input; use textContent
2. **Client-only Validation**: Always validate on server (APEX)
3. **Exposed Secrets**: No API keys in JS; call APEX
4. **Missing Error Handling**: Handle wire service errors gracefully
5. **Unsanitized Display**: Use Lightning Data Service formatters

### Node.js/TypeScript Top 5
1. **SQL Injection**: Use parameterized queries/ORMs
2. **Command Injection**: Avoid `exec`/`spawn` with user input
3. **Hardcoded Secrets**: Use Secrets Manager, not .env in prod
4. **Prototype Pollution**: Validate object inputs, use `Object.create(null)`
5. **Insecure Dependencies**: Run `npm audit fix` regularly

### Python Top 5
1. **SQL Injection**: Use parameterized queries (?, %s with tuple)
2. **Command Injection**: Avoid `os.system`, use `subprocess` with `shell=False`
3. **Pickle Deserialization**: Avoid `pickle.loads` on untrusted data
4. **Path Traversal**: Validate file paths, use `os.path.abspath`
5. **Missing Input Validation**: Validate DataFrame inputs, especially from user uploads

---

**Remember**:
- ⚠️ All Critical findings must be fixed before merge
- ⚠️ High findings require remediation plan
- ⚠️ Security reviews are MANDATORY for all production code
- ⚠️ DELETE chat history after this session
