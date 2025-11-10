# Skills: lwc, lightning_web_components, javascript, salesforce, testing, accessibility
# SSDF Practice Group: PW (Produce Well-Secured Software)
# ARMATech Principles: Security, Cloud First, Modern, Distributed Computing
# Language: JavaScript (Lightning Web Components)
# Context: Apprise Risk Solutions P&T Team - LWC Development

## Security Reminder
⚠️ **CRITICAL**: LWC components run in the browser and must handle user input securely. Use Lightning Data Service for automatic FLS/CRUD enforcement, validate all inputs, and ensure accessibility (WCAG 2.1 AA compliance).

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only (NOT Production)
- [ ] Using dummy test data (NO client/production data)
- [ ] Will delete Claude Code chat history after this session
- [ ] Pre-flight check passed (`./pre-flight-check.sh`)

## Placeholders
- `[COMPONENT_NAME]` - Component name (kebab-case, e.g., "sales-evidence-rating")
- `[SOBJECT_TYPE]` - Salesforce object type (e.g., "Account", "Valuation__c")
- `[FUNCTIONALITY]` - Component purpose (e.g., "Display and rate sales evidence")
- `[FIELDS]` - SObject fields to display (comma-separated)

---

## Task: Lightning Web Component Development

You are a Salesforce developer at Apprise Risk Solutions developing Lightning Web Components for the ARMATech valuation platform. Generate production-ready, accessible, secure LWC components following Salesforce best practices and Apprise coding standards.

### Context

**Company**: Apprise Risk Solutions
- Salesforce Lightning Platform (LWC framework)
- Modern web components using standard JavaScript
- ISO 27001:2022 compliant, WCAG 2.1 AA accessible
- Minimum 80% test coverage required for production deployment

**Lightning Web Components**:
- **Architecture**: Web Components standard (HTML, CSS, JavaScript)
- **Data Access**: Lightning Data Service (automatic FLS/CRUD enforcement)
- **Security**: Shadow DOM encapsulation, secure communication patterns
- **Testing**: Jest framework with @salesforce/sfdx-lwc-jest

**LWC Standards at Apprise**:
- **Naming**: kebab-case for component folders, camelCase for JavaScript
- **Structure**: HTML template, JavaScript class, CSS stylesheet, XML metadata
- **Decorators**: @api (public properties), @wire (reactive data), @track (deprecated, use fields)
- **Accessibility**: ARIA labels, semantic HTML, keyboard navigation
- **Testing**: Jest tests, 80%+ coverage, DOM testing

---

## LWC Development Specification

**Component Name**: [COMPONENT_NAME]

**SObject Type**: [SOBJECT_TYPE]

**Functionality**: [FUNCTIONALITY]

**Fields**: [FIELDS]

**Test Coverage Target**: 80% minimum

---

## Instructions

### Phase 1: DESIGN (Component Architecture)

**1. Component Structure**

Every LWC component has 4 files:

```
[componentName]/
├── [componentName].html          # Template (markup)
├── [componentName].js            # JavaScript class (logic)
├── [componentName].css           # Styles (scoped)
└── [componentName].js-meta.xml   # Metadata (configuration)
```

**2. Component Type Selection**

**Display Component** (read-only):
- Shows data from records
- Uses Lightning Data Service (@wire getRecord)
- No user input

**Form Component** (read-write):
- Edits record data
- Uses lightning-record-form or lightning-record-edit-form
- Input validation

**Action Component** (interactive):
- Performs operations (button clicks, calculations)
- Calls APEX methods
- Shows toast notifications

**Container Component** (composition):
- Combines multiple child components
- Manages state across children
- Event handling (pub/sub or custom events)

**3. Data Access Pattern**

**Option A: Lightning Data Service (Preferred)**
```javascript
// Automatic FLS/CRUD enforcement, caching, change notifications
import { LightningElement, wire, api } from 'lwc';
import { getRecord } from 'lightning/uiRecordApi';

export default class MyComponent extends LightningElement {
    @api recordId;

    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    record;
}
```

**Option B: APEX Imperative (when LDS insufficient)**
```javascript
// Manual calls, more control
import { LightningElement, api } from 'lwc';
import getRecordData from '@salesforce/apex/MyController.getRecordData';

export default class MyComponent extends LightningElement {
    @api recordId;

    async loadData() {
        try {
            const data = await getRecordData({ recordId: this.recordId });
            this.processData(data);
        } catch (error) {
            this.handleError(error);
        }
    }
}
```

**Option C: Wire APEX (reactive)**
```javascript
@wire(getRecordData, { recordId: '$recordId' })
wiredData({ error, data }) {
    if (data) {
        this.processData(data);
    } else if (error) {
        this.handleError(error);
    }
}
```

---

### Phase 2: IMPLEMENT (Component Generation)

**1. HTML Template** (`[componentName].html`)

```html
<template>
    <!-- Loading State -->
    <template if:true={isLoading}>
        <lightning-spinner alternative-text="Loading" size="medium"></lightning-spinner>
    </template>

    <!-- Error State -->
    <template if:true={error}>
        <div class="slds-box slds-theme_error">
            <p class="slds-text-heading_small">Error loading data</p>
            <p>{error}</p>
        </div>
    </template>

    <!-- Data Loaded State -->
    <template if:true={data}>
        <lightning-card title={cardTitle} icon-name="standard:account">
            <!-- Accessibility: Use semantic HTML -->
            <div slot="actions">
                <lightning-button
                    label="Refresh"
                    onclick={handleRefresh}
                    icon-name="utility:refresh"
                    aria-label="Refresh data"
                ></lightning-button>
            </div>

            <!-- Body Content -->
            <div class="slds-p-around_medium">
                <!-- Display Fields -->
                <template for:each={fields} for:item="field">
                    <div key={field.name} class="slds-m-bottom_small">
                        <span class="slds-text-title">{field.label}:</span>
                        <span class="slds-m-left_x-small">{field.value}</span>
                    </div>
                </template>

                <!-- Action Buttons -->
                <div class="slds-m-top_medium">
                    <lightning-button
                        variant="brand"
                        label="Calculate Rating"
                        onclick={handleCalculateRating}
                        disabled={isProcessing}
                        aria-label="Calculate sales evidence rating"
                    ></lightning-button>
                </div>

                <!-- Results Display -->
                <template if:true={rating}>
                    <div class="slds-box slds-m-top_medium" role="region" aria-label="Rating results">
                        <p class="slds-text-heading_small">Rating: {rating.value} stars</p>
                        <p>Confidence: {rating.confidence}%</p>
                    </div>
                </template>
            </div>
        </lightning-card>
    </template>

    <!-- Empty State -->
    <template if:false={hasData}>
        <div class="slds-text-align_center slds-p-around_large">
            <p class="slds-text-heading_medium">No data available</p>
        </div>
    </template>
</template>
```

**Accessibility Best Practices**:
- Use semantic HTML (`<button>`, `<nav>`, `<main>`, `<article>`)
- Add ARIA labels (`aria-label`, `aria-describedby`)
- Ensure keyboard navigation (focusable elements, tab order)
- Use `role` attributes when needed
- Provide alternative text for icons/images

**2. JavaScript Class** (`[componentName].js`)

```javascript
import { LightningElement, api, wire, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';
import { refreshApex } from '@salesforce/apex';

// Import APEX methods
import calculateRating from '@salesforce/apex/RatingController.calculateRating';

// Import fields
import NAME_FIELD from '@salesforce/schema/[SObjectName].Name';
import STATUS_FIELD from '@salesforce/schema/[SObjectName].Status__c';
import DATE_FIELD from '@salesforce/schema/[SObjectName].Date__c';

const FIELDS = [NAME_FIELD, STATUS_FIELD, DATE_FIELD];

/**
 * Component for [FUNCTIONALITY]
 *
 * @author P&T Team
 * @date 2025-10-25
 */
export default class [ComponentName] extends LightningElement {
    // Public properties (accessible from parent or record page)
    @api recordId;
    @api cardTitle = 'Default Title';

    // Private reactive properties (no @track needed in modern LWC)
    isLoading = false;
    isProcessing = false;
    error = null;
    rating = null;

    // Wire to get record data (Lightning Data Service)
    @wire(getRecord, { recordId: '$recordId', fields: FIELDS })
    wiredRecord({ error, data }) {
        if (data) {
            this.record = data;
            this.error = null;
            this.processRecord(data);
        } else if (error) {
            this.record = null;
            this.error = this.extractErrorMessage(error);
            this.showToast('Error', this.error, 'error');
        }
    }

    /**
     * Process record data
     */
    processRecord(record) {
        // Extract field values
        this.name = getFieldValue(record, NAME_FIELD);
        this.status = getFieldValue(record, STATUS_FIELD);
        this.date = getFieldValue(record, DATE_FIELD);

        // Format for display
        this.fields = [
            { name: 'name', label: 'Name', value: this.name },
            { name: 'status', label: 'Status', value: this.status },
            { name: 'date', label: 'Date', value: this.formatDate(this.date) }
        ];
    }

    /**
     * Computed properties (getters)
     */
    get hasData() {
        return this.record != null;
    }

    get data() {
        return this.record;
    }

    /**
     * Handle refresh button click
     */
    async handleRefresh() {
        this.isLoading = true;
        try {
            // Refresh data from server
            await refreshApex(this.wiredRecord);
            this.showToast('Success', 'Data refreshed', 'success');
        } catch (error) {
            this.showToast('Error', 'Failed to refresh data', 'error');
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Handle calculate rating button click
     */
    async handleCalculateRating() {
        this.isProcessing = true;
        this.error = null;

        try {
            // Input validation
            if (!this.recordId) {
                throw new Error('Record ID is required');
            }

            // Call APEX method
            const result = await calculateRating({ recordId: this.recordId });

            // Update UI
            this.rating = {
                value: result.rating,
                confidence: Math.round(result.confidence * 100)
            };

            this.showToast('Success', 'Rating calculated successfully', 'success');
        } catch (error) {
            this.error = this.extractErrorMessage(error);
            this.showToast('Error', this.error, 'error');
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Show toast notification
     */
    showToast(title, message, variant) {
        const event = new ShowToastEvent({
            title: title,
            message: message,
            variant: variant  // success | error | warning | info
        });
        this.dispatchEvent(event);
    }

    /**
     * Extract error message from error object
     */
    extractErrorMessage(error) {
        if (Array.isArray(error.body)) {
            return error.body.map(e => e.message).join(', ');
        } else if (error.body && error.body.message) {
            return error.body.message;
        } else if (typeof error === 'string') {
            return error;
        }
        return 'Unknown error occurred';
    }

    /**
     * Format date for display
     */
    formatDate(dateValue) {
        if (!dateValue) return '';
        const date = new Date(dateValue);
        return date.toLocaleDateString('en-AU', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    /**
     * Lifecycle hooks
     */
    connectedCallback() {
        // Component inserted into DOM
        console.log('[ComponentName] connected');
    }

    disconnectedCallback() {
        // Component removed from DOM
        console.log('[ComponentName] disconnected');
    }

    errorCallback(error, stack) {
        // Error boundary - catches errors from child components
        console.error('[ComponentName] error:', error);
        console.error('Stack:', stack);
        this.error = error.message;
    }
}
```

**JavaScript Best Practices**:
- Use `const`/`let` (not `var`)
- Use arrow functions for callbacks
- Use async/await (not promises .then())
- Handle errors with try/catch
- Validate inputs before APEX calls
- Use getters for computed properties
- Don't mutate @wire data (copy it first)

**3. CSS Stylesheet** (`[componentName].css`)

```css
/* Component-scoped styles (Shadow DOM) */

:host {
    /* Host element styles */
    display: block;
}

/* Card styles */
.slds-card__header {
    background-color: var(--lwc-colorBackground);
}

/* Error message styling */
.slds-theme_error {
    border-left: 4px solid #c23934;
}

/* Custom rating display */
.rating-display {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border-radius: 0.25rem;
    background-color: #f4f6f9;
}

.rating-value {
    font-size: 2rem;
    font-weight: bold;
    color: #0070d2;
}

.rating-label {
    font-size: 0.875rem;
    color: #706e6b;
}

/* Responsive design */
@media (max-width: 768px) {
    .slds-card__body {
        padding: 0.5rem;
    }

    .rating-display {
        flex-direction: column;
        text-align: center;
    }
}

/* Focus states for accessibility */
button:focus,
lightning-button:focus-within {
    outline: 2px solid #0070d2;
    outline-offset: 2px;
}

/* Loading spinner positioning */
lightning-spinner {
    position: relative;
    z-index: 1000;
}
```

**CSS Best Practices**:
- Use SLDS (Salesforce Lightning Design System) classes
- Scope custom styles to component
- Use CSS variables for theming
- Ensure focus states for accessibility
- Responsive design with media queries
- Don't use !important (breaks encapsulation)

**4. Metadata XML** (`[componentName].js-meta.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>59.0</apiVersion>
    <isExposed>true</isExposed>

    <!-- Description -->
    <masterLabel>[Component Name]</masterLabel>
    <description>[FUNCTIONALITY] - Developed by P&T Team</description>

    <!-- Targets (where component can be used) -->
    <targets>
        <target>lightning__RecordPage</target>
        <target>lightning__AppPage</target>
        <target>lightning__HomePage</target>
        <!-- <target>lightningCommunity__Page</target> -->
    </targets>

    <!-- Target Configs (layout configurations) -->
    <targetConfigs>
        <!-- Record Page Configuration -->
        <targetConfig targets="lightning__RecordPage">
            <!-- Object filter (which objects) -->
            <objects>
                <object>[SObjectName]</object>
            </objects>

            <!-- Property exposed to App Builder -->
            <property name="cardTitle" type="String" label="Card Title" description="Title displayed on the card" default="[Default Title]" />
        </targetConfig>

        <!-- App Page Configuration -->
        <targetConfig targets="lightning__AppPage">
            <property name="recordId" type="String" label="Record ID" description="ID of record to display" required="true" />
            <property name="cardTitle" type="String" label="Card Title" description="Title displayed on the card" default="[Default Title]" />
        </targetConfig>
    </targetConfigs>
</LightningComponentBundle>
```

---

### Phase 3: TEST (80% Coverage Target)

**Jest Test File** (`__tests__/[componentName].test.js`)

```javascript
import { createElement } from 'lwc';
import [ComponentName] from 'c/[componentName]';
import { getRecord } from 'lightning/uiRecordApi';
import calculateRating from '@salesforce/apex/RatingController.calculateRating';

// Mock APEX methods
jest.mock(
    '@salesforce/apex/RatingController.calculateRating',
    () => {
        return {
            default: jest.fn()
        };
    },
    { virtual: true }
);

// Mock Lightning Data Service
const mockGetRecord = require('./data/getRecordSample.json');

describe('c-[component-name]', () => {
    afterEach(() => {
        // Reset DOM after each test
        while (document.body.firstChild) {
            document.body.removeChild(document.body.firstChild);
        }

        // Clear mocks
        jest.clearAllMocks();
    });

    /**
     * Test: Component renders successfully
     */
    it('renders component with record data', async () => {
        // Arrange
        const element = createElement('c-[component-name]', {
            is: [ComponentName]
        });
        element.recordId = '001XXXXXXXXXXXXXXX';

        // Act
        document.body.appendChild(element);

        // Emit mock record data
        getRecord.emit(mockGetRecord);

        // Wait for promises to resolve
        await Promise.resolve();

        // Assert
        const card = element.shadowRoot.querySelector('lightning-card');
        expect(card).not.toBeNull();

        const fields = element.shadowRoot.querySelectorAll('.slds-m-bottom_small');
        expect(fields.length).toBeGreaterThan(0);
    });

    /**
     * Test: Loading state shows spinner
     */
    it('shows loading spinner initially', () => {
        // Arrange
        const element = createElement('c-[component-name]', {
            is: [ComponentName]
        });
        element.recordId = '001XXXXXXXXXXXXXXX';

        // Act
        document.body.appendChild(element);

        // Assert - component should be in loading state initially
        // (This depends on your implementation)
    });

    /**
     * Test: Error handling
     */
    it('displays error message when record loading fails', async () => {
        // Arrange
        const element = createElement('c-[component-name]', {
            is: [ComponentName]
        });
        element.recordId = '001XXXXXXXXXXXXXXX';

        // Act
        document.body.appendChild(element);

        // Emit error
        getRecord.error({ body: { message: 'Record not found' } });

        await Promise.resolve();

        // Assert
        const errorDiv = element.shadowRoot.querySelector('.slds-theme_error');
        expect(errorDiv).not.toBeNull();
        expect(errorDiv.textContent).toContain('Record not found');
    });

    /**
     * Test: Calculate rating button click
     */
    it('calls APEX method when calculate button clicked', async () => {
        // Arrange
        const element = createElement('c-[component-name]', {
            is: [ComponentName]
        });
        element.recordId = '001XXXXXXXXXXXXXXX';
        document.body.appendChild(element);

        // Emit mock record data
        getRecord.emit(mockGetRecord);
        await Promise.resolve();

        // Mock APEX response
        calculateRating.mockResolvedValue({
            rating: 4.5,
            confidence: 0.85
        });

        // Act
        const button = element.shadowRoot.querySelector('lightning-button[label="Calculate Rating"]');
        button.click();

        await Promise.resolve();

        // Assert
        expect(calculateRating).toHaveBeenCalledWith({
            recordId: '001XXXXXXXXXXXXXXX'
        });

        const ratingDiv = element.shadowRoot.querySelector('.slds-box');
        expect(ratingDiv).not.toBeNull();
    });

    /**
     * Test: APEX call error handling
     */
    it('handles APEX error gracefully', async () => {
        // Arrange
        const element = createElement('c-[component-name]', {
            is: [ComponentName]
        });
        element.recordId = '001XXXXXXXXXXXXXXX';
        document.body.appendChild(element);

        getRecord.emit(mockGetRecord);
        await Promise.resolve();

        // Mock APEX error
        calculateRating.mockRejectedValue({
            body: { message: 'Calculation failed' }
        });

        // Act
        const button = element.shadowRoot.querySelector('lightning-button[label="Calculate Rating"]');
        button.click();

        await Promise.resolve();

        // Assert - error should be displayed (check your error UI)
        expect(element.error).toContain('Calculation failed');
    });

    /**
     * Test: Accessibility - ARIA labels present
     */
    it('has proper ARIA labels for accessibility', async () => {
        // Arrange
        const element = createElement('c-[component-name]', {
            is: [ComponentName]
        });
        element.recordId = '001XXXXXXXXXXXXXXX';
        document.body.appendChild(element);

        getRecord.emit(mockGetRecord);
        await Promise.resolve();

        // Assert
        const buttons = element.shadowRoot.querySelectorAll('lightning-button');
        buttons.forEach(button => {
            expect(button.getAttribute('aria-label')).toBeTruthy();
        });
    });

    /**
     * Test: Refresh button functionality
     */
    it('refreshes data when refresh button clicked', async () => {
        // Arrange
        const element = createElement('c-[component-name]', {
            is: [ComponentName]
        });
        element.recordId = '001XXXXXXXXXXXXXXX';
        document.body.appendChild(element);

        getRecord.emit(mockGetRecord);
        await Promise.resolve();

        // Act
        const refreshButton = element.shadowRoot.querySelector('lightning-button[label="Refresh"]');
        refreshButton.click();

        await Promise.resolve();

        // Assert - verify refresh was called
        // (You may need to spy on refreshApex)
    });
});
```

**Mock Data File** (`__tests__/data/getRecordSample.json`)

```json
{
    "apiName": "[SObjectName]",
    "fields": {
        "Id": {
            "value": "001XXXXXXXXXXXXXXX"
        },
        "Name": {
            "value": "Test Record"
        },
        "Status__c": {
            "value": "Active"
        },
        "Date__c": {
            "value": "2025-10-25"
        }
    }
}
```

**Jest Configuration** (`jest.config.js` - project level)

```javascript
const { jestConfig } = require('@salesforce/sfdx-lwc-jest/config');

module.exports = {
    ...jestConfig,
    moduleNameMapper: {
        '^@salesforce/apex$': '<rootDir>/force-app/test/jest-mocks/apex',
        '^@salesforce/schema$': '<rootDir>/force-app/test/jest-mocks/schema',
        '^lightning/platformShowToastEvent$': '<rootDir>/force-app/test/jest-mocks/lightning/platformShowToastEvent'
    },
    coverageThreshold: {
        global: {
            branches: 80,
            functions: 80,
            lines: 80,
            statements: 80
        }
    }
};
```

**Run Tests**:
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test [componentName].test

# Watch mode
npm test -- --watch
```

---

## Output Expected

1. **HTML Template**: `[componentName].html`
2. **JavaScript Class**: `[componentName].js`
3. **CSS Stylesheet**: `[componentName].css`
4. **Metadata XML**: `[componentName].js-meta.xml`
5. **Jest Test**: `__tests__/[componentName].test.js`
6. **Mock Data**: `__tests__/data/*.json`

---

## Related Templates

- Use `apex_development.md` for APEX controllers
- Use `../core-workflows/secure_feature_development.md` for overall feature development
- Use `../core-workflows/code_review_request.md` for code review

---

**Template Version**: 1.0
**Last Updated**: October 2025
**Owner**: P&T Team / AI Approach Project
