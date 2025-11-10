# Skills: security, code_review, debugging
# SSDF Practice Group: PW (Produce Well-Secured Software)
# ARMATech Principles: Security
# Language: Multi (APEX, JavaScript, TypeScript, Python, SQL)
# Context: Apprise Risk Solutions P&T Team - Input Validation & Injection Prevention

## Security Reminder
⚠️ **CRITICAL**: Input validation is the first line of defense against injection attacks. All user inputs and API responses must be validated.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only
- [ ] Using dummy test data (NO client data)
- [ ] Will delete Claude Code chat history after this session

## Placeholders
- `[FUNCTION_NAME]` - Name of function to create/review (e.g., "validatePropertyAddress")
- `[INPUT_TYPE]` - Type of input (e.g., "property address", "email", "valuation amount")
- `[LANGUAGE]` - APEX | JavaScript | TypeScript | Python | SQL
- `[VALIDATION_RULES]` - Specific validation requirements
- `[ERROR_HANDLING]` - How to handle invalid input

---

## Task: Generate Input Validation Code

You are a security engineer at Apprise Risk Solutions implementing input validation to prevent injection attacks and ensure data integrity.

Create robust input validation code that protects against:
- **SQL Injection** (SOQL in APEX)
- **XSS** (Cross-Site Scripting)
- **Command Injection**
- **Path Traversal**
- **XML/JSON Injection**
- **Business Logic Bypass**

### Context
- **Requirement**: OWASP Top 10 - A03:2021 Injection
- **Compliance**: ISO 27001:2022, Apprise SEH Section 4.1 (Secure Coding Practices)
- **Risk**: Improper input validation leads to unauthorized data access, data corruption
- **Tech Stack**: APEX, LWC, Node.js, TypeScript, Python (Databricks), SQL
- **Data Types**: Property addresses, borrower information, valuation amounts, dates, IDs

---

## Instructions

### 1. PLAN
Outline your approach (4-6 bullets):
- Input sources to validate (user input, API responses, file uploads, database queries)
- Validation strategy (whitelist vs blacklist, type checking, range validation)
- Language-specific injection vectors to prevent
- Error handling approach (user-friendly messages, logging)
- Testing strategy (positive/negative test cases)

### 2. BUILD
Generate validation code with:

**Validation Types**:

1. **Type Validation**:
   - String, number, boolean, date, email, URL
   - Type coercion prevention
   - Null/undefined handling

2. **Format Validation**:
   - Regex patterns (email, phone, postcode)
   - Length constraints (min/max)
   - Character whitelisting
   - Australian formats (ABN, phone, postcode)

3. **Range Validation**:
   - Numeric ranges (valuation amounts, percentages)
   - Date ranges (past/future constraints)
   - String length limits

4. **Business Logic Validation**:
   - Property address format (street, suburb, state, postcode)
   - Valuation amount reasonableness (not $0, not negative)
   - Date logic (sale date not in future)
   - Referential integrity (valid IDs exist)

5. **Injection Prevention**:
   - **SQL/SOQL Injection**: Parameterized queries, no string concatenation
   - **XSS Prevention**: Output encoding, Content Security Policy
   - **Path Traversal**: Whitelist allowed paths, no ../ patterns
   - **Command Injection**: Avoid shell execution, whitelist commands

**Requirements**:
- **Fail Secure**: Reject invalid input by default
- **Clear Error Messages**: User-friendly but don't leak internals
- **Logging**: Log validation failures for security monitoring
- **Performance**: Efficient validation (avoid expensive regex on every input)
- **Maintainability**: Centralized validation functions, not scattered
- **Testing**: Unit tests for valid/invalid inputs

**Language-Specific Patterns**:

**APEX (Salesforce)**:
- Use bind variables for SOQL (`:variable`)
- Database.query() with String.escapeSingleQuotes()
- Field-Level Security (FLS) checks
- CRUD/FLS enforcement

**JavaScript/TypeScript (LWC, Node.js)**:
- Parameterized queries (avoid template literals in SQL)
- DOMPurify for HTML sanitization
- Input type enforcement (TypeScript types)
- Joi/Yup for schema validation

**Python (Databricks)**:
- Parameterized SQL queries (psycopg2, SQLAlchemy)
- Type hints + Pydantic for validation
- Input sanitization before Spark SQL

**SQL**:
- Parameterized queries only
- No dynamic SQL construction
- Stored procedures with parameters

### 3. EXPLAIN
Document:
- Which injection attacks this prevents
- How to use the validation functions
- How to handle validation errors
- How to test validation logic
- Common pitfalls to avoid
- Performance considerations

---

## Output Expected

1. **Validation Module**: `input_validation.[ext]`
   - Centralized validation functions
   - Language-specific best practices
   - Comprehensive error handling

2. **Test File**: `test_input_validation.[ext]`
   - Test valid inputs
   - Test invalid inputs (injection attempts)
   - Test edge cases (null, empty, very long strings)

3. **Usage Examples**: Code snippets showing:
   - How to validate user input
   - How to handle validation errors
   - Integration with existing code

4. **Security Documentation**:
   - Which OWASP vulnerabilities addressed
   - Apprise-specific validation rules
   - Compliance mapping (SSDF, ISO 27001)

---

## Example Usage

### APEX (Salesforce) - Property Address Validation

```apex
/**
 * Validates and sanitizes property address input
 * Prevents SOQL injection and ensures data integrity
 */
public class PropertyAddressValidator {

    // Validation result class
    public class ValidationResult {
        public Boolean isValid { get; set; }
        public String errorMessage { get; set; }
        public String sanitizedValue { get; set; }

        public ValidationResult(Boolean isValid, String errorMessage, String sanitizedValue) {
            this.isValid = isValid;
            this.errorMessage = errorMessage;
            this.sanitizedValue = sanitizedValue;
        }
    }

    /**
     * Validates property address
     * @param address Raw address input from user
     * @return ValidationResult
     */
    public static ValidationResult validateAddress(String address) {
        // Null check
        if (String.isBlank(address)) {
            return new ValidationResult(false, 'Address cannot be empty', null);
        }

        // Length check (prevent DOS attacks)
        if (address.length() > 200) {
            return new ValidationResult(false, 'Address too long (max 200 characters)', null);
        }

        // Sanitize input (escape single quotes for SOQL)
        String sanitized = String.escapeSingleQuotes(address.trim());

        // Character whitelist (alphanumeric, spaces, common punctuation)
        Pattern allowedPattern = Pattern.compile('^[a-zA-Z0-9\\s,\\.\\-\\/]+$');
        if (!allowedPattern.matcher(sanitized).matches()) {
            return new ValidationResult(false, 'Address contains invalid characters', null);
        }

        // Business logic: must contain at least street and suburb
        List<String> parts = sanitized.split(',');
        if (parts.size() < 2) {
            return new ValidationResult(false, 'Address must include street and suburb', null);
        }

        return new ValidationResult(true, null, sanitized);
    }

    /**
     * Safe SOQL query using validated address
     * @param address Validated address
     * @return List of Property__c records
     */
    public static List<Property__c> findPropertiesByAddress(String address) {
        // Validate input first
        ValidationResult result = validateAddress(address);
        if (!result.isValid) {
            throw new IllegalArgumentException(result.errorMessage);
        }

        // Use bind variable (prevents SOQL injection)
        String searchPattern = '%' + result.sanitizedValue + '%';
        return [
            SELECT Id, Address__c, Valuation__c
            FROM Property__c
            WHERE Address__c LIKE :searchPattern
            WITH SECURITY_ENFORCED
            LIMIT 100
        ];
    }
}

// Usage Example:
String userInput = getUserInput(); // From LWC or API
PropertyAddressValidator.ValidationResult result =
    PropertyAddressValidator.validateAddress(userInput);

if (result.isValid) {
    List<Property__c> properties =
        PropertyAddressValidator.findPropertiesByAddress(result.sanitizedValue);
} else {
    // Show error to user
    ApexPages.addMessage(new ApexPages.Message(
        ApexPages.Severity.ERROR,
        result.errorMessage
    ));
}
```

### JavaScript/TypeScript (LWC) - Valuation Amount Validation

```typescript
/**
 * Validates valuation amount input
 * Prevents XSS and ensures business logic compliance
 */

interface ValidationResult {
    isValid: boolean;
    errorMessage?: string;
    sanitizedValue?: number;
}

/**
 * Validates valuation amount
 * @param input Raw input from user (string or number)
 * @returns ValidationResult
 */
export function validateValuationAmount(input: any): ValidationResult {
    // Type validation
    if (input === null || input === undefined) {
        return { isValid: false, errorMessage: 'Valuation amount is required' };
    }

    // Convert to number if string
    const amount = typeof input === 'string' ? parseFloat(input) : input;

    // Check if valid number
    if (isNaN(amount) || !isFinite(amount)) {
        return { isValid: false, errorMessage: 'Valuation amount must be a valid number' };
    }

    // Range validation (business logic)
    if (amount <= 0) {
        return { isValid: false, errorMessage: 'Valuation amount must be greater than zero' };
    }

    if (amount > 100000000) { // $100M limit (unreasonably high)
        return { isValid: false, errorMessage: 'Valuation amount exceeds maximum allowed' };
    }

    // Precision validation (max 2 decimal places)
    if (!Number.isInteger(amount * 100)) {
        return { isValid: false, errorMessage: 'Valuation amount must have at most 2 decimal places' };
    }

    return { isValid: true, sanitizedValue: amount };
}

/**
 * Validates and sanitizes HTML input (prevent XSS)
 * @param input Raw HTML string
 * @returns Sanitized HTML
 */
export function sanitizeHTML(input: string): string {
    // Create a temporary element
    const temp = document.createElement('div');
    temp.textContent = input; // textContent automatically escapes
    return temp.innerHTML;
}

// LWC Component Usage:
import { LightningElement, track } from 'lwc';
import { validateValuationAmount, sanitizeHTML } from 'c/inputValidation';

export default class ValuationForm extends LightningElement {
    @track valuationAmount;
    @track errorMessage;

    handleValuationChange(event) {
        const input = event.target.value;
        const result = validateValuationAmount(input);

        if (result.isValid) {
            this.valuationAmount = result.sanitizedValue;
            this.errorMessage = null;
        } else {
            this.errorMessage = sanitizeHTML(result.errorMessage);
        }
    }
}
```

### Python (Databricks) - SQL Injection Prevention

```python
"""
Input validation for Databricks SQL queries
Prevents SQL injection and ensures data integrity
"""

import re
from typing import Optional, List, Tuple
from pydantic import BaseModel, validator, Field

class PropertySearchInput(BaseModel):
    """Validated property search input"""
    suburb: str = Field(..., min_length=2, max_length=50)
    postcode: str = Field(..., regex=r'^\d{4}$')  # Australian postcode
    min_valuation: Optional[float] = Field(None, ge=0, le=100000000)
    max_valuation: Optional[float] = Field(None, ge=0, le=100000000)

    @validator('suburb')
    def suburb_must_be_alphanumeric(cls, v):
        """Validate suburb contains only letters and spaces"""
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Suburb must contain only letters and spaces')
        return v.strip().title()

    @validator('max_valuation')
    def max_must_exceed_min(cls, v, values):
        """Validate max > min"""
        if 'min_valuation' in values and v is not None:
            if v < values['min_valuation']:
                raise ValueError('Maximum valuation must be greater than minimum')
        return v

def search_properties_safe(search_input: PropertySearchInput) -> List[dict]:
    """
    Safely search properties using parameterized query
    Prevents SQL injection

    Args:
        search_input: Validated search criteria

    Returns:
        List of property records
    """
    # Validated input is now safe to use
    # Use parameterized query (NOT string concatenation)
    query = """
        SELECT
            property_id,
            address,
            suburb,
            postcode,
            valuation_amount
        FROM properties
        WHERE suburb = :suburb
          AND postcode = :postcode
          AND valuation_amount BETWEEN :min_val AND :max_val
        LIMIT 1000
    """

    params = {
        'suburb': search_input.suburb,
        'postcode': search_input.postcode,
        'min_val': search_input.min_valuation or 0,
        'max_val': search_input.max_valuation or 100000000
    }

    # Execute with parameters (prevents injection)
    return spark.sql(query, params).collect()

# Usage Example:
try:
    # Validate input using Pydantic
    search_criteria = PropertySearchInput(
        suburb="Melbourne",  # User input
        postcode="3000",     # User input
        min_valuation=500000
    )

    # If validation passed, safely query
    results = search_properties_safe(search_criteria)
    print(f"Found {len(results)} properties")

except ValueError as e:
    # Handle validation error
    print(f"Invalid input: {e}")
    # Log for security monitoring
    log_validation_failure(str(e), user_input)
```

---

## Apprise-Specific Validation Rules

### Property Address Validation
```
- Must contain street number, street name, suburb
- Suburb must be alphanumeric (no special chars except spaces)
- Postcode must be 4 digits (Australian format)
- State must be: VIC, NSW, QLD, SA, WA, TAS, NT, ACT
- Max length: 200 characters
- No HTML tags, no script tags
```

### Valuation Amount Validation
```
- Must be positive number
- Range: $1 to $100,000,000
- Max 2 decimal places
- Currency symbol optional (strip if present)
```

### Borrower Email Validation
```
- Standard email format (RFC 5322)
- Max length: 254 characters
- Domain whitelist for corporate emails (optional)
- No disposable email providers (optional)
```

### Date Validation (Sale Date, Valuation Date)
```
- Valid ISO 8601 date format
- Sale date: Must be in past (not future)
- Valuation date: Within last 12 months (configurable)
- Not before 1900 (data quality check)
```

### Australian Phone Number Validation
```
- Format: +61 X XXXX XXXX or 0X XXXX XXXX
- Landline: starts with 02, 03, 07, 08
- Mobile: starts with 04
- Remove spaces/dashes before storing
```

---

## OWASP Top 10 Coverage

| OWASP Risk | Prevention Method |
|------------|-------------------|
| **A03:2021 - Injection** | Parameterized queries, input sanitization, whitelist validation |
| **A04:2021 - Insecure Design** | Business logic validation, fail-secure defaults |
| **A05:2021 - Security Misconfiguration** | Centralized validation, secure defaults |
| **A07:2021 - Identification and Authentication Failures** | Input validation prevents auth bypass |

---

## Testing Checklist

### Positive Test Cases (Valid Input)
- [ ] Valid property address formats
- [ ] Valid valuation amounts (range of values)
- [ ] Valid dates (past, present)
- [ ] Valid email addresses
- [ ] Valid phone numbers (Australian format)
- [ ] Unicode characters (émoji, accents)
- [ ] Boundary values (min, max lengths)

### Negative Test Cases (Invalid Input)
- [ ] SQL injection attempts (`' OR '1'='1`)
- [ ] XSS attempts (`<script>alert('xss')</script>`)
- [ ] Path traversal (`../../etc/passwd`)
- [ ] Command injection (`; rm -rf /`)
- [ ] Null/undefined/empty values
- [ ] Extremely long strings (DOS attempt)
- [ ] Invalid types (string when number expected)
- [ ] Out-of-range values
- [ ] Special characters in unexpected fields
- [ ] HTML entities (`&lt;script&gt;`)

### Edge Cases
- [ ] Leading/trailing whitespace
- [ ] Multiple spaces
- [ ] Case sensitivity
- [ ] International characters
- [ ] Emoji in text fields
- [ ] Very large numbers (overflow)
- [ ] Negative numbers where not allowed
- [ ] Decimal places where integers expected

---

## Common Pitfalls to Avoid

❌ **DON'T**: Validate on client-side only
```javascript
// BAD: Client-side validation can be bypassed
if (amount > 0) {
    submitForm();
}
```
✅ **DO**: Validate on both client and server
```javascript
// GOOD: Validate on client for UX, validate on server for security
// Client: Immediate feedback
if (amount > 0) { submitForm(); }

// Server: Security enforcement (APEX, Node.js backend)
public static void processValuation(Decimal amount) {
    if (amount == null || amount <= 0) {
        throw new IllegalArgumentException('Invalid amount');
    }
    // ...
}
```

❌ **DON'T**: Use string concatenation for SQL
```apex
// BAD: SOQL injection vulnerability
String query = 'SELECT Id FROM Property__c WHERE Address__c = \'' + userInput + '\'';
List<Property__c> results = Database.query(query);
```
✅ **DO**: Use bind variables
```apex
// GOOD: Prevents SOQL injection
String address = String.escapeSingleQuotes(userInput);
List<Property__c> results = [
    SELECT Id FROM Property__c WHERE Address__c = :address
];
```

❌ **DON'T**: Trust API responses without validation
```javascript
// BAD: Assume API returns valid data
const amount = apiResponse.valuation;
saveToDatabase(amount);
```
✅ **DO**: Validate all external data
```javascript
// GOOD: Validate even trusted sources
const result = validateValuationAmount(apiResponse.valuation);
if (result.isValid) {
    saveToDatabase(result.sanitizedValue);
} else {
    logError('Invalid API response', result.errorMessage);
}
```

---

## Integration with Apprise SDLC

**Design Phase** (Technical Design Card):
- [ ] Identify all user input points
- [ ] Document validation rules for each input
- [ ] Specify error handling approach

**Development Phase**:
- [ ] Implement validation functions
- [ ] Write unit tests for validation
- [ ] Integrate with existing code

**Code Review Phase**:
- [ ] Verify parameterized queries used
- [ ] Check validation on all user inputs
- [ ] Confirm error messages don't leak sensitive info

**Testing Phase**:
- [ ] Run validation test suite
- [ ] Security testing (injection attempts)
- [ ] UAT with edge cases

---

**Remember**:
- ⚠️ ALWAYS validate on server-side (client validation is for UX only)
- ⚠️ NEVER use string concatenation for SQL/SOQL queries
- ⚠️ USE parameterized queries with bind variables
- ⚠️ FAIL SECURE: Reject invalid input by default
- ⚠️ DELETE chat history after this session
