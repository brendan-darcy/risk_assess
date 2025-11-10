# Skills: code_review, security_audit, quality_analysis, best_practices
# SSDF Practice Group: PW (Produce Well-Secured Software), RV (Respond to Vulnerabilities)
# ARMATech Principles: Security, Modern
# Language: Multi (APEX, LWC, Node.js, Python, SQL, R)
# Context: Apprise Risk Solutions P&T Team - Automated Code Review

## Security Reminder
⚠️ **CRITICAL**: This template requests Claude to review code for security vulnerabilities and quality issues. The code being reviewed may contain sensitive patterns or logic - ensure no production data is included in the review.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only
- [ ] Code being reviewed contains NO hardcoded credentials or secrets
- [ ] Code being reviewed contains NO production/client data
- [ ] Will delete Claude Code chat history after this session
- [ ] Pre-flight check passed (`./pre-flight-check.sh`)

## Placeholders
- `[FILE_PATH]` - Path to file being reviewed (e.g., "src/services/ratingService.ts")
- `[LANGUAGE]` - Programming language: APEX | LWC | Node.js/TypeScript | Python | SQL | R
- `[REVIEW_FOCUS]` - Focus areas: security | code_quality | performance | testing | all
- `[SEVERITY_THRESHOLD]` - Minimum severity to report: Critical | High | Medium | Low
- `[COMPONENT_NAME]` - Component/module name (e.g., "Sales Evidence Rating Service")
- `[PR_NUMBER]` - Pull request number (if applicable)

---

## Task: Comprehensive Code Review

You are a senior code reviewer at Apprise Risk Solutions performing a comprehensive code review for the ARMATech platform. Review the provided code for security vulnerabilities (OWASP Top 10), code quality issues, language-specific anti-patterns, test coverage gaps, and performance concerns.

### Context

**Company**: Apprise Risk Solutions
- Property valuation platform handling sensitive data
- ISO 27001:2022 certified, OWASP-compliant
- Code reviews required for all changes (manual + automated)
- Focus: Security, maintainability, performance, testability

**Code Review Standards**:
- **Security**: OWASP Top 10 compliance mandatory
- **Quality**: Language-specific conventions, readable, maintainable
- **Performance**: Efficient algorithms, optimized queries, minimal resource usage
- **Testing**: Adequate coverage, edge cases, security scenarios
- **Documentation**: Clear comments for complex logic

**Review Philosophy**:
- **Constructive**: Focus on improvement, not criticism
- **Actionable**: Provide specific remediation steps
- **Prioritized**: Critical/High severity first
- **Educational**: Explain why something is an issue

---

## Code Review Request

**File**: [FILE_PATH]

**Component**: [COMPONENT_NAME]

**Language**: [LANGUAGE]

**Review Focus**: [REVIEW_FOCUS]

**Severity Threshold**: [SEVERITY_THRESHOLD]

**Pull Request**: [PR_NUMBER] (if applicable)

---

## Instructions

Perform a comprehensive code review following this framework:

### Review Categories

#### 1. Security Review (OWASP Top 10)

**Check for these vulnerabilities**:

**A01: Broken Access Control**
- Missing authorization checks
- Insecure direct object references
- Privilege escalation opportunities
- CORS misconfiguration

```
❌ Example Issue:
public User getUser(String userId) {
    return [SELECT Id, Name FROM User WHERE Id = :userId];
    // Missing: Check if current user can access this user's data
}

✅ Remediation:
- Add authorization check before query
- Verify current user has permission to access requested user
```

**A02: Cryptographic Failures**
- Hardcoded secrets (API keys, passwords, tokens)
- Weak encryption algorithms
- Sensitive data transmitted over HTTP (not HTTPS)
- Unencrypted storage of sensitive data

```
❌ Example Issue:
const API_KEY = 'sk-1234567890abcdef';  // Hardcoded secret

✅ Remediation:
- Use environment variables: process.env.API_KEY
- Or AWS Secrets Manager for production
- Or Salesforce Named Credentials
```

**A03: Injection**
- SQL injection (string concatenation in queries)
- SOQL injection (unescaped user input)
- Command injection (exec, eval with user input)
- XSS (unescaped output in HTML)

```
❌ Example Issue (APEX):
String query = 'SELECT Id FROM Account WHERE Name = \'' + accountName + '\'';
List<Account> accounts = Database.query(query);  // SQL injection risk

✅ Remediation:
List<Account> accounts = [SELECT Id FROM Account WHERE Name = :accountName];
```

**A04: Insecure Design**
- Missing rate limiting
- No input validation
- Weak password requirements
- Missing security controls

**A05: Security Misconfiguration**
- Default credentials
- Unnecessary features enabled
- Missing security headers
- Overly permissive CORS

**A06: Vulnerable and Outdated Components**
- Outdated dependencies with known CVEs
- Unmaintained libraries
- Missing security patches

**A07: Identification and Authentication Failures**
- Weak session management
- Missing MFA
- Predictable session IDs
- No account lockout

**A08: Software and Data Integrity Failures**
- Unsigned code
- Insecure deserialization
- Missing integrity checks

**A09: Security Logging and Monitoring Failures**
- Sensitive data in logs
- Insufficient logging
- No alerting on suspicious activity

**A10: Server-Side Request Forgery (SSRF)**
- User-controlled URLs without validation
- Internal network access from user input

---

#### 2. Code Quality Review

**Check for these issues**:

**Naming Conventions**:
- Variables/functions have meaningful names (not single letters except loops)
- Follow language-specific conventions (camelCase, PascalCase, snake_case)
- Constants in UPPER_CASE
- Boolean variables start with is/has/can

**Complexity**:
- Functions > 50 lines (consider refactoring)
- Classes > 300 lines (consider splitting)
- Cyclomatic complexity > 10 (too many branches)
- Deeply nested code (> 4 levels)

**Code Duplication**:
- Repeated code blocks (DRY principle violation)
- Similar functions with slight variations
- Copy-pasted code

**Error Handling**:
- Empty catch blocks (swallowing errors)
- Generic exception catching (catch Exception)
- Missing error messages
- Sensitive data in error messages

**Documentation**:
- Missing docstrings for public functions
- Unclear variable names requiring comments
- Complex logic without explanation
- Outdated comments (don't match code)

**Type Safety** (where applicable):
- Missing type hints (Python)
- Using `any` type (TypeScript)
- Type mismatches
- Unsafe type coercions

---

#### 3. Language-Specific Anti-Patterns

**APEX**:
- Non-bulkified code (operating on single records in loops)
- SOQL in loops (governor limit violation)
- DML in loops (governor limit violation)
- Missing `with sharing` keyword
- Not using collections
- Direct variable access instead of properties

```
❌ Bad (APEX):
for (Account acc : accounts) {
    Contact c = [SELECT Id FROM Contact WHERE AccountId = :acc.Id LIMIT 1];  // SOQL in loop!
    update c;  // DML in loop!
}

✅ Good (APEX):
Set<Id> accountIds = new Set<Id>();
for (Account acc : accounts) {
    accountIds.add(acc.Id);
}
List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId IN :accountIds];
update contacts;
```

**LWC (Lightning Web Components)**:
- Direct @track property mutation (use immutability)
- Not using Lightning Data Service (manual CRUD instead)
- Missing error boundaries
- Accessibility issues (missing ARIA labels)
- Shadow DOM violations

**Node.js/TypeScript**:
- Callback hell (nested callbacks instead of async/await)
- Unhandled promise rejections
- Synchronous file operations in async code
- Memory leaks (event listeners not cleaned up)

**Python**:
- Mutable default arguments
- Catching bare exceptions (except:)
- Not using context managers (with statements)
- Not using list comprehensions (verbose loops)

**SQL**:
- SELECT * instead of explicit columns
- Missing indexes on WHERE/JOIN columns
- String concatenation instead of parameterized queries
- No LIMIT clause on queries returning large results

**R**:
- Not using vectorized operations (slow loops)
- Growing vectors in loops (performance issue)
- Not using tidyverse when appropriate
- Missing package namespace (conflicts)

---

#### 4. Performance Review

**Check for these performance issues**:

**Inefficient Algorithms**:
- N+1 query problems
- Nested loops on large datasets
- Unnecessary iterations
- Missing caching

**Database/Query Issues**:
- Missing indexes
- Inefficient JOINs
- Fetching unnecessary columns (SELECT *)
- Not using pagination

**Memory Issues**:
- Loading entire datasets into memory
- Memory leaks (unreleased resources)
- Large object allocations in loops

**Network Issues**:
- Unnecessary API calls
- Missing request batching
- Not using connection pooling
- Synchronous calls in loops

---

#### 5. Testing Review

**Check for these testing gaps**:

**Coverage**:
- Missing tests for critical functions
- Coverage below target (75% APEX, 80% LWC/Node, 70% Python)
- Only happy path tested (missing edge cases)

**Test Quality**:
- Tests don't actually test anything (no assertions)
- Tests using production data
- Flaky tests (non-deterministic)
- Tests dependent on each other

**Test Scenarios Missing**:
- Negative test cases (error handling)
- Security test cases (injection, unauthorized access)
- Edge cases (null, empty, boundary values)
- Integration tests

---

## Output Format

Generate a structured code review report:

### Code Review Report

**File**: [FILE_PATH]
**Component**: [COMPONENT_NAME]
**Language**: [LANGUAGE]
**Reviewed**: [Date]
**Reviewer**: Claude Code (Automated Review)

---

### Summary

- **Total Findings**: [Number]
- **Critical**: [Number]
- **High**: [Number]
- **Medium**: [Number]
- **Low**: [Number]

**Overall Assessment**: [Pass with minor issues | Needs revision | Requires significant changes]

---

### Findings

#### Finding #1: [Title] - **[SEVERITY]**

**Category**: [Security | Code Quality | Performance | Testing]

**Location**: Line [X] or Lines [X-Y]

**Issue Description**:
[Clear description of the problem]

**Code Snippet**:
```[language]
[Problematic code]
```

**Security Impact** (if applicable):
[How this could be exploited]

**Recommended Fix**:
```[language]
[Fixed code example]
```

**Explanation**:
[Why this is an issue and why the fix works]

**Priority**: [Immediate | Before merge | Future improvement]

---

#### Finding #2: [Title] - **[SEVERITY]**

[Same format as above]

---

### Positive Observations

[List things done well - this is important for constructive feedback]

Examples:
- ✅ Good use of parameterized queries
- ✅ Comprehensive error handling
- ✅ Clear function documentation
- ✅ Proper input validation

---

### Recommendations

1. [High-priority recommendation]
2. [Medium-priority recommendation]
3. [Nice-to-have improvement]

---

### Severity Definitions

**Critical**: Must fix before deployment (security vulnerabilities, data corruption risks)
**High**: Should fix before merge (performance issues, significant bugs)
**Medium**: Should fix soon (code quality, maintainability)
**Low**: Nice to have (minor improvements, style issues)

---

## Example Usage

### Scenario: Review Sales Evidence Rating Service

**File**: `src/services/salesEvidenceRatingService.ts`

**Component**: Sales Evidence Rating Service

**Language**: Node.js/TypeScript

**Review Focus**: all

**Severity Threshold**: Medium

### Code to Review

```typescript
import { DynamoDBClient, GetItemCommand } from '@aws-sdk/client-dynamodb';

const API_KEY = 'sk-1234567890abcdef';  // TODO: Move to env

export class SalesEvidenceRatingService {
  private dynamodb = new DynamoDBClient({ region: 'ap-southeast-2' });

  async rateEvidence(evidenceId: string, userId: string) {
    // Get evidence from database
    const result = await this.dynamodb.send(
      new GetItemCommand({
        TableName: 'sales_evidence',
        Key: { id: { S: evidenceId } }
      })
    );

    if (!result.Item) {
      throw new Error('Evidence not found: ' + evidenceId);
    }

    const evidence = result.Item;
    const age_days = this.calculateAge(evidence.sale_date.S);

    let rating;
    if (age_days < 90) rating = 5;
    else if (age_days < 180) rating = 4;
    else if (age_days < 365) rating = 3;
    else rating = 1;

    return { rating: rating, confidence: 0.8 };
  }

  calculateAge(dateStr: string) {
    const saleDate = new Date(dateStr);
    const today = new Date();
    return (today - saleDate) / (1000 * 60 * 60 * 24);
  }
}
```

### Expected Review Report

```markdown
### Code Review Report

**File**: src/services/salesEvidenceRatingService.ts
**Component**: Sales Evidence Rating Service
**Language**: Node.js/TypeScript
**Reviewed**: 2025-10-25
**Reviewer**: Claude Code (Automated Review)

---

### Summary

- **Total Findings**: 6
- **Critical**: 1
- **High**: 2
- **Medium**: 2
- **Low**: 1

**Overall Assessment**: Needs revision (critical security issue must be fixed)

---

### Findings

#### Finding #1: Hardcoded API Key - **CRITICAL**

**Category**: Security (A02: Cryptographic Failures)

**Location**: Line 3

**Issue Description**:
API key is hardcoded in source code, exposing it to anyone with repository access.

**Code Snippet**:
```typescript
const API_KEY = 'sk-1234567890abcdef';  // TODO: Move to env
```

**Security Impact**:
- API key visible in version control history
- Accessible to all developers with code access
- If repository is ever made public, key is exposed
- Cannot rotate key without code deployment

**Recommended Fix**:
```typescript
const API_KEY = process.env.API_KEY;
if (!API_KEY) {
  throw new Error('API_KEY environment variable not set');
}
```

**Explanation**:
Use environment variables to store secrets. This allows key rotation without code changes and keeps secrets out of version control.

**Priority**: Immediate (block merge)

---

#### Finding #2: Missing Authorization Check - **HIGH**

**Category**: Security (A01: Broken Access Control)

**Location**: Lines 10-16

**Issue Description**:
Function accepts userId parameter but never validates that the user has permission to rate this evidence.

**Code Snippet**:
```typescript
async rateEvidence(evidenceId: string, userId: string) {
  // No authorization check here!
  const result = await this.dynamodb.send(...)
```

**Security Impact**:
Any authenticated user could rate any evidence, including evidence from valuations they shouldn't access. Potential for data manipulation.

**Recommended Fix**:
```typescript
async rateEvidence(evidenceId: string, userId: string) {
  // Verify user has permission
  const hasPermission = await this.checkUserPermission(userId, evidenceId);
  if (!hasPermission) {
    throw new AuthorizationError('User not authorized to rate this evidence');
  }

  const result = await this.dynamodb.send(...)
```

**Explanation**:
Always verify authorization before performing operations on resources. Check that the user owns the resource or has explicit permission.

**Priority**: Immediate (security vulnerability)

---

#### Finding #3: Sensitive Data in Error Message - **HIGH**

**Category**: Security (A09: Security Logging Failures)

**Location**: Line 19

**Issue Description**:
Error message includes evidenceId, which could expose internal IDs to end users.

**Code Snippet**:
```typescript
throw new Error('Evidence not found: ' + evidenceId);
```

**Security Impact**:
- Exposes internal resource IDs
- Could be used for enumeration attacks
- May reveal system structure

**Recommended Fix**:
```typescript
// Log detailed error server-side
console.error('Evidence not found', { evidenceId, userId });

// Generic error to user
throw new NotFoundError('Evidence not found');
```

**Explanation**:
Log detailed errors server-side for debugging, but return generic errors to users to avoid information leakage.

**Priority**: Before merge

---

#### Finding #4: Missing Input Validation - **MEDIUM**

**Category**: Code Quality / Security

**Location**: Lines 10-11

**Issue Description**:
No validation that evidenceId and userId are valid formats.

**Code Snippet**:
```typescript
async rateEvidence(evidenceId: string, userId: string) {
  // No validation here
```

**Recommended Fix**:
```typescript
async rateEvidence(evidenceId: string, userId: string) {
  // Validate inputs
  if (!evidenceId || typeof evidenceId !== 'string' || evidenceId.trim() === '') {
    throw new ValidationError('Invalid evidenceId');
  }
  if (!userId || typeof userId !== 'string') {
    throw new ValidationError('Invalid userId');
  }

  // Or use a validation library like Joi, Zod, validator.js
```

**Priority**: Before merge

---

#### Finding #5: Missing Error Handling - **MEDIUM**

**Category**: Code Quality

**Location**: Line 25

**Issue Description**:
calculateAge assumes dateStr is valid format, will crash on invalid dates.

**Code Snippet**:
```typescript
calculateAge(dateStr: string) {
  const saleDate = new Date(dateStr);  // Could be Invalid Date
  const today = new Date();
  return (today - saleDate) / (1000 * 60 * 60 * 24);  // Could be NaN
}
```

**Recommended Fix**:
```typescript
calculateAge(dateStr: string): number {
  const saleDate = new Date(dateStr);
  if (isNaN(saleDate.getTime())) {
    throw new ValidationError('Invalid date format');
  }

  const today = new Date();
  const ageMs = today.getTime() - saleDate.getTime();
  return Math.floor(ageMs / (1000 * 60 * 60 * 24));
}
```

**Priority**: Before merge

---

#### Finding #6: Missing Type Annotations - **LOW**

**Category**: Code Quality (TypeScript)

**Location**: Lines 10, 24, 25

**Issue Description**:
Some functions/variables missing explicit type annotations.

**Code Snippet**:
```typescript
async rateEvidence(evidenceId: string, userId: string) {  // Return type missing
  ...
  let rating;  // Type inferred as 'number | undefined'
  ...
  return { rating: rating, confidence: 0.8 };  // Return type unclear
}
```

**Recommended Fix**:
```typescript
interface RatingResult {
  rating: number;
  confidence: number;
}

async rateEvidence(evidenceId: string, userId: string): Promise<RatingResult> {
  ...
  let rating: number;
  ...
  return { rating, confidence: 0.8 };
}
```

**Priority**: Future improvement

---

### Positive Observations

- ✅ Good use of AWS SDK v3 (modular imports)
- ✅ Async/await pattern used correctly
- ✅ Clear rating logic (easy to understand thresholds)
- ✅ Separated date calculation into helper method

---

### Recommendations

1. **Immediate**: Fix hardcoded API key (Critical)
2. **Immediate**: Add authorization check (High)
3. **Before Merge**: Improve error handling and input validation
4. **Before Merge**: Add comprehensive tests (positive, negative, security scenarios)
5. **Future**: Add TypeScript strict mode types
6. **Future**: Add caching layer for frequently accessed evidence
7. **Future**: Add monitoring/metrics (success rate, latency)

---

**Conclusion**: Code has good structure but requires security fixes before deployment. Critical and High severity issues must be addressed immediately.
```

---

## Related Templates

**Before Code Review**:
- Use `secure_feature_development.md` to build features with best practices
- Use `bug_fix_workflow.md` for structured debugging

**After Code Review**:
- Use `refactoring_workflow.md` if major quality issues found
- Use `../security/security_review.md` for deeper security audit
- Use `../security/input_validation.md` if validation issues found

---

## Notes

**Review Effectiveness**:
- Automated reviews (this template) catch common patterns
- Human reviews still essential for:
  - Business logic correctness
  - Design decisions
  - Context-specific issues
  - Subjective quality assessments

**When to Use This Template**:
- ✅ Before merging pull requests
- ✅ After significant refactoring
- ✅ When onboarding to new codebase (learning)
- ✅ Regular code health audits

**When NOT to Use**:
- ❌ Real-time pairing (use human reviewer)
- ❌ Architectural design review (different process)
- ❌ Code with hardcoded production secrets (security risk)

---

**Template Version**: 1.0
**Last Updated**: October 2025
**Owner**: P&T Team / AI Approach Project
