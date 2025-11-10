# Skills: refactoring, technical_debt, code_quality, testing, architecture
# SSDF Practice Group: PW (Produce Well-Secured Software)
# ARMATech Principles: Modern, Security
# Language: Multi (APEX, LWC, Node.js, Python, SQL, R)
# Context: Apprise Risk Solutions P&T Team - Technical Debt Reduction

## Security Reminder
⚠️ **CRITICAL**: Refactoring can introduce bugs or security vulnerabilities. Always ensure test coverage BEFORE refactoring and maintain backward compatibility unless breaking changes are explicitly approved.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only (NOT Production)
- [ ] Using dummy test data (NO client/production data)
- [ ] Will delete Claude Code chat history after this session
- [ ] Pre-flight check passed (`./pre-flight-check.sh`)
- [ ] **CRITICAL**: Test coverage exists BEFORE starting refactoring (safety net)

## Placeholders
- `[COMPONENT_NAME]` - Component/module to refactor (e.g., "Sales Evidence Rating Service")
- `[FILE_PATH]` - Path to file being refactored (e.g., "src/services/ratingService.ts")
- `[LANGUAGE]` - Programming language: APEX | LWC | Node.js/TypeScript | Python | SQL | R
- `[REFACTORING_REASON]` - Why refactoring is needed (technical debt | performance | maintainability | security)
- `[CODE_SMELLS]` - Identified code smells (duplicated_code | long_methods | large_classes | feature_envy)
- `[BREAKING_CHANGES]` - Are breaking changes allowed? (yes | no)
- `[TEST_COVERAGE_TARGET]` - Minimum coverage: 75% (APEX), 80% (LWC/Node.js), 70% (Python/R)

---

## Task: Safe Technical Debt Reduction Through Refactoring

You are a software engineer at Apprise Risk Solutions refactoring code to reduce technical debt while maintaining system stability. Follow a disciplined approach: assess code quality, ensure test coverage exists, plan incremental changes, refactor systematically, and validate thoroughly.

### Context

**Company**: Apprise Risk Solutions
- Property valuation platform with 10+ years of legacy code
- High stability requirement (production system)
- Technical debt accumulated from rapid feature development
- ISO 27001:2022 compliant, cannot introduce security regressions

**Refactoring Philosophy**:
- **Test First**: Never refactor without tests (tests are your safety net)
- **Incremental**: Small, safe changes (not big bang rewrites)
- **Backward Compatible**: Maintain existing APIs unless approved otherwise
- **Reversible**: Can roll back if issues discovered
- **Value-Driven**: Refactor what matters (not perfectionism)

**When to Refactor**:
- ✅ Before adding new features (clean up first)
- ✅ When fixing bugs in messy code
- ✅ When code is difficult to understand
- ✅ When performance is suffering
- ✅ When security vulnerabilities present

**When NOT to Refactor**:
- ❌ Production is broken (fix first, refactor later)
- ❌ No test coverage (write tests first)
- ❌ Under time pressure (defer to later)
- ❌ Code works and rarely changes (leave it alone)

---

## Refactoring Request

**Component**: [COMPONENT_NAME]

**File**: [FILE_PATH]

**Language**: [LANGUAGE]

**Reason for Refactoring**: [REFACTORING_REASON]

**Code Smells Identified**: [CODE_SMELLS]

**Breaking Changes Allowed**: [BREAKING_CHANGES]

**Current Test Coverage**: [XX]% (must be ≥ target before refactoring)

**Test Coverage Target**: [TEST_COVERAGE_TARGET]

---

## Instructions

Follow this four-phase disciplined refactoring workflow:

### Phase 1: ASSESS (Code Quality Analysis)

Before touching any code, assess current state:

**1. Identify Code Smells**

**Common Code Smells**:

**Duplicated Code**
- Same/similar code blocks repeated
- Copy-pasted functions with slight variations
- Similar logic in multiple places

```python
# Example: Duplicated validation logic
def process_valuation_order(order):
    if not order.territory or order.territory not in ['NSW', 'VIC', 'QLD']:
        raise ValueError('Invalid territory')
    # Process...

def process_valuation_report(report):
    if not report.territory or report.territory not in ['NSW', 'VIC', 'QLD']:
        raise ValueError('Invalid territory')
    # Process...

# REFACTOR: Extract to shared validation function
```

**Long Methods**
- Functions > 50 lines
- Multiple levels of abstraction
- Difficult to understand at a glance

**Large Classes**
- Classes > 300 lines
- Too many responsibilities
- Difficult to test

**Feature Envy**
- Method uses data from another class more than its own
- Sign of misplaced responsibility

**Primitive Obsession**
- Using primitives instead of small objects
- Example: Using separate `lat`, `lon` instead of `Coordinates` object

**Long Parameter Lists**
- Functions with > 5 parameters
- Difficult to remember order
- Sign of missing abstraction

**Divergent Change**
- Class changes for multiple reasons
- Violates Single Responsibility Principle

**Shotgun Surgery**
- Single change requires modifications in many places
- Poor cohesion

**Comments Explaining Complex Code**
- Comments shouldn't be necessary for simple logic
- Extract method with self-explanatory name instead

**2. Measure Current State**

**Code Metrics to Measure**:
- Test coverage (must be ≥ target)
- Cyclomatic complexity (should be < 10 per function)
- Function length (should be < 50 lines)
- Class length (should be < 300 lines)
- Number of dependencies
- Performance metrics (baseline for comparison)

**Tools**:
```bash
# APEX
sfdx force:apex:test:run -c -r human  # Coverage

# JavaScript/TypeScript
npm test -- --coverage
npm run lint  # Code quality

# Python
pytest --cov=[module] --cov-report=html
flake8 [file]  # Code quality
pylint [file]  # Detailed analysis

# R
library(covr)
package_coverage()
```

**3. Check Test Coverage**

⚠️ **CRITICAL**: DO NOT REFACTOR without adequate test coverage

**Test Coverage Requirements**:
- Existing tests pass consistently
- Coverage ≥ target (75% APEX, 80% LWC/Node, 70% Python/R)
- Tests cover critical paths
- Tests are independent and repeatable

**If Coverage Insufficient**:
1. STOP refactoring
2. Write tests first to reach target coverage
3. Ensure tests pass
4. Then proceed with refactoring

**4. Document Current Behavior**

Before changing code, document what it currently does:
- Public API (method signatures, return types, exceptions)
- Side effects (database writes, API calls, file operations)
- Edge cases handled
- Performance characteristics
- Known limitations or bugs

This documentation becomes your specification for refactored code.

---

### Phase 2: PLAN (Refactoring Strategy)

Plan refactoring approach before making changes:

**1. Choose Refactoring Patterns**

**Common Refactoring Patterns**:

**Extract Method** (for long methods):
```python
# Before: Long method
def process_order(order):
    # 80 lines of code mixing validation, calculation, and persistence

# After: Extracted methods
def process_order(order):
    validate_order(order)
    amount = calculate_total(order)
    persist_order(order, amount)

def validate_order(order):
    # Validation logic

def calculate_total(order):
    # Calculation logic

def persist_order(order, amount):
    # Persistence logic
```

**Extract Class** (for large classes):
```typescript
// Before: God class with too many responsibilities
class ValuationOrderManager {
  // 500 lines doing validation, calculation, notification, reporting
}

// After: Separated responsibilities
class ValuationOrderValidator { /* validation logic */ }
class ValuationOrderCalculator { /* calculation logic */ }
class ValuationOrderNotifier { /* notification logic */ }
class ValuationOrderManager {
  // Coordinates the above classes
}
```

**Replace Conditional with Polymorphism** (for complex if/else):
```python
# Before: Complex conditionals
def calculate_rating(evidence, evidence_type):
    if evidence_type == 'sale':
        # 20 lines of sale logic
    elif evidence_type == 'listing':
        # 20 lines of listing logic
    elif evidence_type == 'appraisal':
        # 20 lines of appraisal logic

# After: Polymorphism
class EvidenceRater(ABC):
    @abstractmethod
    def rate(self, evidence): pass

class SaleRater(EvidenceRater):
    def rate(self, evidence): # Sale logic

class ListingRater(EvidenceRater):
    def rate(self, evidence): # Listing logic

def calculate_rating(evidence, rater: EvidenceRater):
    return rater.rate(evidence)
```

**Replace Magic Numbers with Named Constants**:
```javascript
// Before
if (age_days < 90) rating = 5;
else if (age_days < 180) rating = 4;

// After
const EXCELLENT_THRESHOLD_DAYS = 90;
const GOOD_THRESHOLD_DAYS = 180;
const EXCELLENT_RATING = 5;
const GOOD_RATING = 4;

if (age_days < EXCELLENT_THRESHOLD_DAYS) rating = EXCELLENT_RATING;
else if (age_days < GOOD_THRESHOLD_DAYS) rating = GOOD_RATING;
```

**Introduce Parameter Object** (for long parameter lists):
```python
# Before: Long parameter list
def create_valuation(address, suburb, postcode, state, property_type, bedrooms, bathrooms, land_size):
    pass

# After: Parameter object
@dataclass
class PropertyDetails:
    address: str
    suburb: str
    postcode: str
    state: str
    property_type: str
    bedrooms: int
    bathrooms: int
    land_size: float

def create_valuation(property_details: PropertyDetails):
    pass
```

**2. Plan Incremental Steps**

Break refactoring into small, safe steps:

**Example: Refactoring Large Class**

Step 1: Extract one method (deploy, test)
Step 2: Extract another method (deploy, test)
Step 3: Group related methods into new class (deploy, test)
Step 4: Repeat until responsibilities separated

Each step:
- Can be deployed independently
- Has tests passing
- Can be rolled back if issues

**3. Backward Compatibility Strategy**

If breaking changes NOT allowed:

**Approach A: Deprecation Path**
```typescript
// Step 1: Create new API, keep old one
function calculateRating(evidence: Evidence): Rating {  // New API
  return calculateRatingV2(evidence);
}

/** @deprecated Use calculateRating instead */
function calculateRatingOld(evidenceId: string): number {  // Old API
  const evidence = loadEvidence(evidenceId);
  return calculateRating(evidence).value;
}

// Step 2 (future release): Remove old API after migration period
```

**Approach B: Adapter Pattern**
```python
# Old interface still works via adapter
class OldRatingService:
    def rate(self, evidence_id: str) -> float:
        # Adapter that calls new implementation
        evidence = Evidence.load(evidence_id)
        return NewRatingService().rate(evidence).rating
```

**4. Document Refactoring Plan**

Create refactoring plan document:
- What will change (code structure, not behavior)
- Why it's needed (technical debt, performance, maintainability)
- How it will be done (step-by-step)
- What stays the same (public APIs, behavior)
- Rollback plan if issues discovered
- Testing strategy

For significant refactorings, create ADR (Architecture Decision Record).

---

### Phase 3: REFACTOR (Incremental Implementation)

Execute refactoring plan incrementally:

**1. One Change at a Time**

Make ONE refactoring change, then:
1. Run all tests (must pass)
2. Commit with descriptive message
3. Deploy to dev environment
4. Verify functionality
5. Move to next change

**Never batch multiple refactorings in one commit** (hard to debug if issues)

**2. Test After Each Change**

```bash
# After EACH refactoring change, run full test suite
pytest tests/ -v  # Python
npm test  # Node.js
sfdx force:apex:test:run  # APEX
```

✅ All tests must pass before proceeding

**3. Maintain Test Coverage**

After refactoring:
```bash
# Verify coverage maintained or improved
pytest --cov=[module] --cov-report=term-missing
```

Coverage should be ≥ original (refactoring shouldn't reduce coverage)

**4. Refactoring Safety Checklist**

After each refactoring step:
- [ ] All existing tests pass
- [ ] Test coverage maintained or improved
- [ ] No new linter warnings
- [ ] Public API unchanged (unless breaking changes approved)
- [ ] Performance not degraded (run benchmarks)
- [ ] Security controls maintained
- [ ] Code committed with clear message

**5. Handle Discovered Issues**

If refactoring reveals bugs:
- Document bugs found
- Fix bugs in separate commits (not mixed with refactoring)
- Add regression tests for bugs
- Continue refactoring after bug fixes

**6. Update Tests**

If internal implementation changed significantly:
- Update integration tests if necessary
- Unit tests should mostly still pass (testing behavior, not implementation)
- Add tests for new internal functions if complex

---

### Phase 4: VALIDATE (Quality Assurance)

After refactoring complete, comprehensive validation:

**1. Test Suite Validation**

Run comprehensive test suite:
```bash
# Run ALL tests (unit, integration, E2E)
npm run test:all  # Node.js
pytest tests/ --slow  # Python (including slow tests)
sfdx force:apex:test:run --codecoverage --resultformat human  # APEX
```

**Validation Checklist**:
- [ ] All tests pass
- [ ] Test coverage ≥ target (or improved)
- [ ] No flaky tests introduced
- [ ] Performance tests pass (no regression)

**2. Code Quality Validation**

Run linters and quality tools:
```bash
# Check code quality metrics
npm run lint  # JavaScript/TypeScript
flake8 . && pylint [module]  # Python
sfdx scanner:run --target "[files]"  # APEX
```

**Quality Checklist**:
- [ ] No new linter warnings
- [ ] Cyclomatic complexity reduced
- [ ] Function/class lengths improved
- [ ] Code duplication reduced
- [ ] Comments reduced (self-explanatory code)

**3. Functional Validation**

Manual testing in dev environment:
- [ ] Core workflows still function
- [ ] Edge cases handled correctly
- [ ] Error handling works
- [ ] Performance acceptable
- [ ] UI/UX unchanged (unless intentional)

**4. Performance Validation**

Compare before/after performance:
```python
# Benchmark critical paths
import time

start = time.time()
# Run operation 1000 times
for _ in range(1000):
    refactored_function(test_data)
elapsed = time.time() - start

print(f"Performance: {elapsed:.2f}s for 1000 operations")
# Compare to baseline before refactoring
```

**Performance Checklist**:
- [ ] No significant slowdown (< 10% regression acceptable)
- [ ] Ideally improved performance
- [ ] No memory leaks introduced
- [ ] Database queries not increased

**5. Security Validation**

Use `code_review_request.md` to verify:
- [ ] No security regressions
- [ ] Input validation maintained
- [ ] Authentication/authorization unchanged
- [ ] Error handling still secure (no data leakage)
- [ ] Secrets management maintained

**6. Documentation Updates**

Update documentation to reflect changes:
- [ ] Code comments updated (inline)
- [ ] API documentation (if public API changed)
- [ ] Architecture diagrams (if structure changed significantly)
- [ ] ADR created (for significant refactorings)
- [ ] Commit messages clear and descriptive

---

## Output Expected

Deliver the following:

### 1. Refactored Code
**Files**: `[component_name].[extension]` (modified)

**Quality Improvements**:
- Reduced complexity (cyclomatic complexity, function length)
- Eliminated code duplication
- Improved readability (self-explanatory names, clear structure)
- Better separation of concerns
- Maintained or improved test coverage

### 2. Test Updates
**Files**: `test_[component_name].[extension]` (modified if needed)

**Validation**:
- All tests pass
- Coverage ≥ target
- Tests still test behavior (not implementation details)

### 3. Documentation
**Files to update**:
- Inline code comments (if complex logic)
- ADR (if significant architectural refactoring)
- CHANGELOG.md (note refactoring, especially if any API changes)

### 4. Refactoring Report
**Format**: Text or Markdown

**Contents**:
- What was refactored (components, classes, functions)
- Why (technical debt reason, code smells addressed)
- How (refactoring patterns used)
- Before/after metrics (complexity, coverage, performance)
- Breaking changes (if any)
- Rollback plan (if needed)

---

## Example Usage

### Scenario: Refactor Sales Evidence Rating Service (Duplicated Code)

**Component**: Sales Evidence Rating Service

**File**: `src/services/salesEvidenceRatingService.py`

**Language**: Python

**Reason**: Technical debt - duplicated validation logic across 5 methods

**Code Smells**: Duplicated code, long methods

**Breaking Changes Allowed**: No

**Current Test Coverage**: 85% (above 70% target ✅)

### Assessment

**Code Smell**: Duplicated validation logic
```python
# Method 1
def rate_sale_evidence(self, evidence):
    if not evidence.property_type or evidence.property_type not in VALID_PROPERTY_TYPES:
        raise ValueError('Invalid property type')
    if not evidence.sale_date or evidence.sale_date > datetime.now():
        raise ValueError('Invalid sale date')
    # Rating logic...

# Method 2
def rate_listing_evidence(self, evidence):
    if not evidence.property_type or evidence.property_type not in VALID_PROPERTY_TYPES:
        raise ValueError('Invalid property type')
    if not evidence.listing_date or evidence.listing_date > datetime.now():
        raise ValueError('Invalid listing date')
    # Rating logic...

# ... 3 more methods with similar validation
```

**Metrics**:
- Cyclomatic complexity: 8 per method (borderline)
- Code duplication: ~40 lines duplicated
- Test coverage: 85%

### Refactoring Plan

**Pattern**: Extract Method

**Steps**:
1. Extract common validation to `_validate_property_type()`
2. Extract common validation to `_validate_date()`
3. Update all methods to use extracted validators
4. Run tests after each step

**Backward Compatibility**: No API changes, pure internal refactoring

### Refactored Code

```python
class SalesEvidenceRatingService:
    """Service for rating sales evidence quality."""

    def _validate_property_type(self, property_type: Optional[str]) -> None:
        """Validate property type is provided and valid."""
        if not property_type or property_type not in VALID_PROPERTY_TYPES:
            raise ValidationError(
                f'Invalid property type. Must be one of: {", ".join(VALID_PROPERTY_TYPES)}'
            )

    def _validate_date(self, date: Optional[datetime], field_name: str) -> None:
        """Validate date is provided and not in future."""
        if not date:
            raise ValidationError(f'{field_name} is required')
        if date > datetime.now():
            raise ValidationError(f'{field_name} cannot be in the future')

    def rate_sale_evidence(self, evidence: SaleEvidence) -> RatingResult:
        """Rate sale evidence quality."""
        # Validation (extracted to reusable methods)
        self._validate_property_type(evidence.property_type)
        self._validate_date(evidence.sale_date, 'Sale date')

        # Rating logic (unchanged)
        age_days = (datetime.now() - evidence.sale_date).days
        return self._calculate_rating(age_days, evidence.property_type)

    def rate_listing_evidence(self, evidence: ListingEvidence) -> RatingResult:
        """Rate listing evidence quality."""
        # Validation (reusing same methods)
        self._validate_property_type(evidence.property_type)
        self._validate_date(evidence.listing_date, 'Listing date')

        # Rating logic (unchanged)
        age_days = (datetime.now() - evidence.listing_date).days
        return self._calculate_rating(age_days, evidence.property_type)
```

### Validation Results

**Test Results**: ✅ All 45 tests pass

**Coverage**: 87% (improved from 85%)

**Code Metrics**:
- Cyclomatic complexity: 4 per method (improved from 8)
- Code duplication: 0 lines (eliminated 40 lines of duplication)
- Lines of code: Reduced by 35 lines

**Performance**: No change (refactoring was structural, not algorithmic)

**Commit Message**:
```
refactor(SalesEvidenceRatingService): Extract duplicated validation logic

Extracted common validation logic for property type and dates into
reusable private methods. Eliminates 40 lines of code duplication
across 5 rating methods.

Before: 8 cyclomatic complexity per method, 40 lines duplicated
After: 4 cyclomatic complexity per method, 0 duplication

No API changes, pure internal refactoring.
Test coverage improved from 85% to 87%.
```

---

## Related Templates

**Before Refactoring**:
- Use `code_review_request.md` to identify code smells
- Ensure test coverage with language-specific test templates

**After Refactoring**:
- Use `code_review_request.md` to verify quality improvements
- Use `secure_feature_development.md` to add new features to refactored code

---

## Notes

**Refactoring Best Practices**:
- ✅ Test coverage BEFORE refactoring (safety net)
- ✅ Incremental changes (small, safe steps)
- ✅ Commit after each step (easy rollback)
- ✅ Run tests after each change (catch issues immediately)
- ✅ Maintain backward compatibility (unless approved)
- ✅ Document significant refactorings (ADR)

**Common Refactoring Mistakes**:
- ❌ Refactoring without tests (dangerous!)
- ❌ Big bang rewrites (high risk)
- ❌ Mixing refactoring with feature additions (confusing)
- ❌ Breaking backward compatibility unintentionally
- ❌ Optimizing prematurely (refactor for clarity first)

**When to Stop Refactoring**:
- Tests pass consistently
- Code smells eliminated
- Complexity reduced
- Duplication eliminated
- Good enough (don't pursue perfection)

---

**Template Version**: 1.0
**Last Updated**: October 2025
**Owner**: P&T Team / AI Approach Project
