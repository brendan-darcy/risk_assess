# Skills: debugging, root_cause_analysis, testing, problem_solving
# SSDF Practice Group: PW (Produce Well-Secured Software), RV (Respond to Vulnerabilities)
# ARMATech Principles: Modern, Security
# Language: Multi (APEX, LWC, Node.js, Python, SQL, R)
# Context: Apprise Risk Solutions P&T Team - Structured Bug Fix Workflow

## Security Reminder
⚠️ **CRITICAL**: Bug fixes may introduce new vulnerabilities. All fixes must be security-reviewed and regression-tested before deployment.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only (NOT Production)
- [ ] Using dummy test data to reproduce bug (NO client/production data)
- [ ] Will delete Claude Code chat history after this session
- [ ] Pre-flight check passed (`./pre-flight-check.sh`)

## Placeholders
- `[BUG_ID]` - Bug tracking ID (e.g., "JIRA-1234", "GitHub Issue #567")
- `[BUG_DESCRIPTION]` - Brief description of the bug (1-2 sentences)
- `[LANGUAGE]` - Programming language: APEX | LWC | Node.js/TypeScript | Python | SQL | R
- `[SEVERITY]` - Bug severity: Critical | High | Medium | Low
- `[COMPONENT_NAME]` - Affected component/module name
- `[REPRODUCTION_STEPS]` - Steps to reproduce the bug
- `[EXPECTED_BEHAVIOR]` - What should happen
- `[ACTUAL_BEHAVIOR]` - What actually happens
- `[TEST_COVERAGE_TARGET]` - Minimum coverage: 75% (APEX), 80% (LWC/Node.js), 70% (Python/R)

---

## Task: Structured Bug Fix with Root Cause Analysis

You are a software engineer at Apprise Risk Solutions fixing a bug in the ARMATech platform. Follow a structured debugging approach: understand the root cause, implement a secure fix, generate regression tests, and validate the solution before deployment.

### Context

**Company**: Apprise Risk Solutions
- Property valuation platform handling sensitive client data
- ISO 27001:2022 certified, OWASP-compliant
- Bug fixes must not introduce new vulnerabilities or break existing functionality

**Bug Fix Philosophy**:
- **Understand First**: Don't fix symptoms, fix root causes
- **Test-Driven**: Write failing test first, then fix
- **Security-Aware**: Bug fixes can introduce new vulnerabilities
- **Regression Prevention**: Ensure bug doesn't return
- **Documentation**: Update docs to reflect fix

**Common Bug Categories**:
- **Logic Errors**: Incorrect calculations, wrong conditions
- **Data Handling**: Null pointer exceptions, type mismatches, edge cases
- **Integration Issues**: API failures, timeout errors, authentication problems
- **Performance**: Slow queries, memory leaks, infinite loops
- **Security**: Authentication bypass, injection vulnerabilities, XSS
- **UI/UX**: Display issues, validation errors, accessibility problems

---

## Bug Specification

**Bug ID**: [BUG_ID]

**Severity**: [SEVERITY]

**Component**: [COMPONENT_NAME]

**Language**: [LANGUAGE]

**Description**: [BUG_DESCRIPTION]

**Reproduction Steps**:
[REPRODUCTION_STEPS]

**Expected Behavior**:
[EXPECTED_BEHAVIOR]

**Actual Behavior**:
[ACTUAL_BEHAVIOR]

**Test Coverage Target**: [TEST_COVERAGE_TARGET]

---

## Instructions

Follow this four-phase structured debugging workflow:

### Phase 1: UNDERSTAND (Root Cause Analysis)

Before fixing anything, perform comprehensive root cause analysis:

**1. Reproduce the Bug Locally**:
- Follow reproduction steps with **dummy data** (not production data)
- Confirm bug occurs consistently
- Document exact conditions required to trigger bug
- Note any error messages, stack traces, or logs

**2. Isolate the Problem**:
- Narrow down to specific function/method/component
- Identify the line(s) of code causing the issue
- Use debuggers, logging, or print statements
- Check recent code changes (git blame, pull requests)

**3. Root Cause Analysis Framework**:

Ask these questions:

**a) What is the immediate cause?**
- Which line of code fails?
- What values trigger the failure?
- What condition is not being handled?

**b) Why does this happen?**
- Missing input validation?
- Incorrect logic?
- Unhandled edge case?
- Race condition or timing issue?
- Missing error handling?

**c) Why wasn't this caught earlier?**
- Missing test coverage?
- Test using unrealistic data?
- Integration not tested?
- Edge case not considered?

**d) Are there similar issues elsewhere?**
- Is this pattern repeated in other code?
- Could other components have the same bug?
- Should we search codebase for similar patterns?

**4. Security Impact Assessment**:

⚠️ **CRITICAL**: Assess if this bug is a security vulnerability:

**Security Questions**:
- Does this allow unauthorized access? (authentication bypass)
- Does this expose sensitive data? (information disclosure)
- Does this allow injection attacks? (SQL, SOQL, XSS, command injection)
- Does this cause denial of service? (infinite loops, memory exhaustion)
- Does this bypass input validation? (business rule violation)

**If YES to any**: This is a security vulnerability, prioritize fix and follow RV (Respond to Vulnerabilities) protocol.

**5. Impact Analysis**:
- How many users affected?
- Which environments affected? (Dev, UAT, Prod)
- Data integrity impact?
- Performance impact?
- Workaround available?

**6. Proposed Solution** (3-5 bullet points):
- Describe the fix approach
- Why this solves the root cause (not just symptoms)
- Alternative approaches considered
- Risks of the fix
- Breaking changes (if any)

---

### Phase 2: FIX (Secure Implementation)

Implement the fix following best practices:

**1. Write a Failing Test First (TDD Approach)**:

Before fixing the bug, write a test that reproduces it:

```python
# Example: Python test for bug reproduction
def test_bug_[BUG_ID]_reproduction():
    """
    Reproduces bug [BUG_ID]: [Brief description]
    This test should FAIL before the fix and PASS after the fix.
    """
    # Setup: Create conditions that trigger the bug
    input_data = create_edge_case_data()  # Dummy data

    # Execute: Call the buggy function
    result = buggy_function(input_data)

    # Assert: This will fail before fix, pass after fix
    assert result.status == 'success', "Bug [BUG_ID]: Function fails on edge case"
    assert result.value is not None, "Bug [BUG_ID]: Returns None instead of valid value"
```

**Run the test - it should FAIL** (confirming bug exists)

**2. Implement the Fix**:

**Fix Checklist**:
- [ ] Addresses root cause (not just symptoms)
- [ ] Handles all edge cases identified
- [ ] Maintains backward compatibility (or documents breaking changes)
- [ ] Follows language-specific conventions
- [ ] Includes input validation (if missing)
- [ ] Has proper error handling
- [ ] No hardcoded values (use configuration)
- [ ] No security vulnerabilities introduced

**Security-Aware Fixes**:

```javascript
// ❌ BAD FIX: Introduces security vulnerability
function getUser(userId) {
    // Bug fix: Handle null userId
    if (!userId) {
        userId = 'admin';  // ❌ Default to admin is security risk!
    }
    return db.query(`SELECT * FROM users WHERE id = ${userId}`);  // ❌ SQL injection!
}

// ✅ GOOD FIX: Secure and proper
function getUser(userId) {
    // Input validation
    if (!userId || typeof userId !== 'string') {
        throw new ValidationError('Invalid userId');
    }

    // Parameterized query (prevents SQL injection)
    return db.query('SELECT * FROM users WHERE id = ?', [userId]);
}
```

**3. Code Quality**:

Apply language-specific standards:

**APEX**:
- Bulkified fix (handle collections, not single records)
- Governor limits considered
- `with sharing` enforced
- Proper exception handling (AuraHandledException for LWC)

**LWC**:
- Immutability preserved (no direct prop mutation)
- Shadow DOM considerations
- Error boundaries implemented
- Accessibility maintained

**Node.js/TypeScript**:
- Async/await patterns (no callback hell)
- TypeScript strict mode types
- Proper promise error handling
- Environment variables for config

**Python**:
- Type hints updated
- PEP 8 compliance
- Proper exception types
- Logging added for debugging

**4. Run the Test - It Should Pass**:

```bash
# The failing test from step 1 should now pass
pytest tests/test_[component_name].py::test_bug_[BUG_ID]_reproduction -v
```

✅ Test should pass, confirming bug is fixed

---

### Phase 3: VALIDATE (Regression Testing & Review)

Ensure the fix doesn't break existing functionality:

**1. Regression Test Suite**:

Create comprehensive regression tests:

**a) Bug-Specific Test (from Phase 2)**:
- Test that reproduces original bug
- Test edge cases that caused the bug
- Test boundary conditions

**b) Related Functionality Tests**:
- Test all functions that call the fixed code
- Test all functions the fixed code calls
- Test integration points

**c) Security Regression Tests**:
```python
def test_bug_[BUG_ID]_no_security_regression():
    """Ensure bug fix didn't introduce security vulnerabilities"""

    # Test 1: Input validation still enforced
    with pytest.raises(ValidationError):
        fixed_function(malicious_input='<script>alert(1)</script>')

    # Test 2: Authorization still checked
    unauthorized_user = create_test_user(role='viewer')
    with pytest.raises(PermissionError):
        fixed_function(user=unauthorized_user)

    # Test 3: No sensitive data in errors
    try:
        fixed_function(invalid_data='test')
    except Exception as e:
        assert 'password' not in str(e).lower()
        assert 'secret' not in str(e).lower()
```

**2. Test Coverage Validation**:

```bash
# Verify test coverage meets target
# APEX
sfdx force:apex:test:run -n [ComponentName]Test -c -r human
# Coverage should be ≥ 75%

# LWC/Node.js
npm test -- --coverage
# Coverage should be ≥ 80%

# Python
pytest --cov=[component_name] --cov-report=html
# Coverage should be ≥ 70%
```

**3. Manual Testing Checklist**:
- [ ] Bug reproduction steps no longer reproduce the bug
- [ ] Expected behavior now occurs
- [ ] No new errors in console/logs
- [ ] Performance acceptable (no significant slowdown)
- [ ] UI/UX unchanged (unless intentional)
- [ ] Works in all supported browsers/environments
- [ ] Edge cases handled gracefully

**4. Security Review**:

Use `code_review_request.md` template to request security review:
- OWASP Top 10 vulnerability check
- Input validation review
- Error handling review
- Authentication/authorization check

**5. Code Review Checklist** (for human reviewers):
- [ ] Root cause addressed (not symptoms)
- [ ] Fix is minimal (smallest change possible)
- [ ] No breaking changes (or documented)
- [ ] Test coverage adequate
- [ ] Security vulnerabilities not introduced
- [ ] Code follows language standards
- [ ] Documentation updated

---

### Phase 4: DOCUMENT (Knowledge Capture)

Document the fix for future reference:

**1. Code Comments**:

Add inline comments explaining the fix:

```python
def calculate_total(prices: list[float]) -> float:
    """Calculate total price with tax."""

    # BUG FIX [BUG_ID]: Handle empty list case
    # Previously this would raise IndexError when prices was empty
    # Now returns 0.0 for empty list
    if not prices:
        return 0.0

    subtotal = sum(prices)
    tax = subtotal * 0.10
    return subtotal + tax
```

**2. Commit Message**:

```
fix([COMPONENT_NAME]): [Brief description] ([BUG_ID])

Root cause: [1-2 sentence explanation]

Fix: [1-2 sentence explanation of solution]

Breaking changes: [None | Description]

Fixes [BUG_ID]
```

**Example**:
```
fix(SalesEvidenceRatingService): Handle null property type (JIRA-1234)

Root cause: Method did not validate input for null property_type, causing
NullPointerException when processing sales evidence without property type.

Fix: Added input validation to check for null/empty property_type before
processing. Returns default rating with low confidence for missing data.

Breaking changes: None

Fixes JIRA-1234
```

**3. Update Documentation**:

**a) README or CHANGELOG**:
```markdown
## [1.2.1] - 2025-10-25

### Fixed
- **[BUG_ID]**: Fixed [brief description]. Previously [old behavior], now [new behavior]. ([#PR_NUMBER])
```

**b) Known Issues (if removing from list)**:
```markdown
### Known Issues
- ~~[BUG_ID]: [Description]~~ - Fixed in v1.2.1
```

**c) API Documentation (if public API changed)**:
Update parameter descriptions, return types, error codes

**4. Lessons Learned** (optional, for significant bugs):
- What caused the bug?
- Why wasn't it caught earlier?
- What process improvements would prevent this?
- Should we audit codebase for similar patterns?

---

## Output Expected

Deliver the following:

### 1. Fix Implementation
**Filename**: `[component_name].[extension]` (modified)

**Contents**:
- Bug fix with inline comments explaining the change
- Input validation added (if missing)
- Error handling improved
- Security controls maintained

### 2. Regression Test Suite
**Filename**: `test_[component_name].[extension]` (modified or new)

**Contents**:
- Test that reproduces original bug (should pass after fix)
- Regression tests for related functionality
- Security regression tests
- Test coverage ≥ target

### 3. Documentation Updates
**Files to update**:
- Code comments (inline)
- Commit message (following convention)
- CHANGELOG.md or README.md (version notes)
- Known issues list (if applicable)
- API docs (if public API changed)

### 4. Root Cause Analysis Report
**Format**: Text or Markdown

**Contents**:
- Bug description
- Root cause explanation (why it happened)
- Fix description (what was changed)
- Testing approach (how fix was validated)
- Security impact (if any)
- Prevention recommendations (process improvements)

---

## Example Usage

### Scenario: Null Pointer Exception in Sales Evidence Rating

**Bug ID**: JIRA-1234

**Severity**: High

**Component**: SalesEvidenceRatingService

**Language**: Python

**Description**: Service crashes when processing sales evidence without property type field

**Reproduction Steps**:
1. Call `rate_evidence()` with sales data
2. Sales data has null/missing `property_type` field
3. Service throws `NullPointerException` or `AttributeError`
4. Rating is not calculated

**Expected Behavior**:
Service should handle missing property type gracefully, returning a default rating with low confidence score

**Actual Behavior**:
Service crashes with `AttributeError: 'NoneType' object has no attribute 'lower'`

### Root Cause Analysis

**Immediate Cause**:
Line 47 in `sales_evidence_rating_service.py`:
```python
if property_type.lower() == 'house':  # Crashes if property_type is None
```

**Why It Happened**:
- Missing input validation for `property_type` parameter
- Assumed all sales evidence has property type (not always true)
- Edge case not considered during initial implementation

**Why Not Caught Earlier**:
- Test data always included property type
- Edge case test missing for null/missing fields
- Integration test didn't cover data quality issues

**Similar Issues Elsewhere**:
- Searched codebase: 3 other methods assume non-null values
- Need to audit all methods for missing null checks

**Security Impact**:
- Low risk: This is availability issue (DoS), not data exposure
- No authentication/authorization bypass
- No injection vulnerability

### Proposed Fix

1. Add input validation for `property_type` (check for None/empty)
2. Use default value ('unknown') when property type missing
3. Reduce confidence score when using defaults
4. Add test case for null property type
5. Audit similar methods for same issue

### Implementation

**File 1**: `sales_evidence_rating_service.py` (fixed)
```python
def rate_evidence(
    self,
    evidence_age_days: int,
    property_type: Optional[str],  # Now explicitly Optional
    sale_type: str,
    completeness_score: float
) -> Dict[str, float]:
    """Rate sales evidence quality."""

    # BUG FIX JIRA-1234: Handle null/missing property type
    # Validate and normalize property type
    if not property_type or not property_type.strip():
        property_type = 'unknown'
        # Reduce confidence when property type is missing
        completeness_score *= 0.8  # 20% penalty for missing data

    property_type = property_type.lower().strip()

    # Rest of implementation...
```

**File 2**: `tests/test_sales_evidence_rating_service.py` (regression test added)
```python
def test_bug_jira_1234_null_property_type():
    """
    Bug JIRA-1234: Handle null property type gracefully
    Previously crashed with AttributeError, now returns default rating with low confidence.
    """
    service = SalesEvidenceRatingService()

    # Test with None
    result = service.rate_evidence(
        evidence_age_days=60,
        property_type=None,  # This used to crash
        sale_type='open_market',
        completeness_score=0.9
    )

    assert result['rating'] >= 1.0
    assert result['rating'] <= 5.0
    assert result['confidence'] < 0.8  # Lower confidence due to missing data

    # Test with empty string
    result = service.rate_evidence(
        evidence_age_days=60,
        property_type='',  # Edge case
        sale_type='open_market',
        completeness_score=0.9
    )

    assert result['rating'] >= 1.0
    assert result['confidence'] < 0.8
```

**File 3**: `CHANGELOG.md` (updated)
```markdown
## [1.2.1] - 2025-10-25

### Fixed
- **JIRA-1234**: Fixed crash when processing sales evidence without property type. Service now handles null/missing property type gracefully by using default value and reducing confidence score. (#PR-567)
```

**File 4**: Root cause analysis report (text)

---

## Related Templates

**After Bug Fix**:
- Use `code_review_request.md` for security review
- Use `../security/security_review.md` if bug was security-related
- Use `refactoring_workflow.md` if fix revealed larger code quality issues

**Testing**:
- Refer to Phase 4 testing templates (when available)
- Use language-specific test generation templates

---

## Notes

**Common Bug Fix Mistakes**:
- ❌ Fixing symptoms instead of root cause (bug will return)
- ❌ Not writing regression tests (bug returns in future)
- ❌ Introducing security vulnerabilities in the fix
- ❌ Breaking existing functionality (insufficient testing)
- ❌ Not documenting the fix (knowledge lost)

**Best Practices**:
- ✅ Understand root cause before fixing
- ✅ Write failing test first (TDD approach)
- ✅ Minimal fix (smallest change possible)
- ✅ Comprehensive regression testing
- ✅ Security review for all fixes
- ✅ Document thoroughly (code, commit, changelog)

**When to Escalate**:
- Bug affects production with no workaround → Escalate immediately
- Bug is security vulnerability → Follow RV protocol
- Fix requires breaking changes → Get approval before implementing
- Root cause unclear after investigation → Request pair programming/debugging session

---

**Template Version**: 1.0
**Last Updated**: October 2025
**Owner**: P&T Team / AI Approach Project
