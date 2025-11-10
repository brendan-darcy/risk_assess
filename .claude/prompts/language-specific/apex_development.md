# Skills: apex, salesforce, secure_coding, testing, bulkification
# SSDF Practice Group: PW (Produce Well-Secured Software), PS (Protect the Software)
# ARMATech Principles: Security, Cloud First, Modern
# Language: APEX (Salesforce)
# Context: Apprise Risk Solutions P&T Team - APEX Secure Development

## Security Reminder
⚠️ **CRITICAL**: APEX code runs on a multi-tenant platform with strict governor limits. All code must be bulkified, secure (SOQL injection prevention), and thoroughly tested (≥75% coverage).

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only (NOT Production)
- [ ] Using dummy test data (NO client/production data)
- [ ] Will delete Claude Code chat history after this session
- [ ] Pre-flight check passed (`./pre-flight-check.sh`)

## Placeholders
- `[CLASS_NAME]` - APEX class name (PascalCase, e.g., "SalesEvidenceRatingService")
- `[SOBJECT_TYPE]` - Salesforce object type (e.g., "Account", "Valuation__c")
- `[FUNCTIONALITY]` - Purpose of class (e.g., "Rate sales evidence quality", "Calculate valuation metrics")
- `[TRIGGER_EVENTS]` - Trigger events (before insert, after update, etc.)
- `[BATCH_SIZE]` - Batch processing size (default 200)
- `[EXTERNAL_API]` - External API name (e.g., "PropTrack API")

---

## Task: Secure APEX Development

You are a Salesforce developer at Apprise Risk Solutions developing APEX code for the ARMATech valuation platform. Generate production-ready, bulkified, secure APEX code following Salesforce best practices, OWASP controls, and Apprise coding standards.

### Context

**Company**: Apprise Risk Solutions
- Salesforce-based valuation platform (Lightning Platform)
- Multi-tenant environment with strict governor limits
- ISO 27001:2022 compliant, OWASP-based secure coding
- Minimum 75% test coverage required for production deployment

**Salesforce Platform**:
- **Governor Limits**: 100 SOQL queries, 150 DML statements, 6 MB heap size per transaction
- **Security**: FLS (Field-Level Security), CRUD (Object permissions), Sharing Rules
- **Architecture**: Triggers, Apex Classes, Batch Apex, Queueable Apex, REST APIs

**APEX Standards at Apprise**:
- **Naming**: PascalCase for classes, camelCase for methods/variables
- **Bulkification**: ALWAYS handle collections (Lists, Sets, Maps)
- **Security**: `with sharing` keyword, FLS/CRUD checks, SOQL injection prevention
- **Testing**: @TestSetup for data, @isTest for test classes, 75%+ coverage
- **Formatting**: SFDX Prettier configuration

---

## APEX Development Specification

**Class Name**: [CLASS_NAME]

**SObject Type**: [SOBJECT_TYPE]

**Functionality**: [FUNCTIONALITY]

**Type**: Service Class | Trigger Handler | Batch Class | Queueable Class | REST API | Utility Class

**Test Coverage Target**: 75% minimum

---

## Instructions

Follow this structured approach for APEX development:

### Phase 1: DESIGN (Architecture & Security)

**1. Class Structure**

Choose appropriate class pattern:

**Service Class** (business logic):
```apex
public with sharing class [ClassName]Service {
    // Public methods (business operations)
    // Private methods (helpers)
    // No SOQL/DML in constructors
}
```

**Trigger Handler** (trigger logic):
```apex
public with sharing class [SObjectName]TriggerHandler {
    // beforeInsert(List<SObject> newRecords)
    // afterInsert(Map<Id, SObject> newRecordsMap)
    // beforeUpdate(Map<Id, SObject> oldMap, Map<Id, SObject> newMap)
    // afterUpdate(Map<Id, SObject> oldMap, Map<Id, SObject> newMap)
    // beforeDelete(Map<Id, SObject> oldMap)
    // afterDelete(Map<Id, SObject> oldMap)
    // afterUndelete(List<SObject> newRecords)
}
```

**Batch Class** (large data processing):
```apex
public with sharing class [ClassName]Batch implements Database.Batchable<SObject> {
    public Database.QueryLocator start(Database.BatchableContext bc) { }
    public void execute(Database.BatchableContext bc, List<SObject> scope) { }
    public void finish(Database.BatchableContext bc) { }
}
```

**Queueable Class** (asynchronous processing):
```apex
public with sharing class [ClassName]Queueable implements Queueable {
    public void execute(QueueableContext context) { }
}
```

**2. Security Design**

**Sharing Model**:
```apex
// DEFAULT: Use 'with sharing' (enforce sharing rules)
public with sharing class SecureService { }

// ONLY if intentional: Use 'without sharing'
// Document WHY sharing rules should be bypassed
public without sharing class ElevatedService {
    // Used for: System-level operations that need to access all records
    // Security: Additional authorization checks implemented manually
}

// INHERITED: Use 'inherited sharing' (respect caller's context)
public inherited sharing class FlexibleService { }
```

**FLS/CRUD Checks**:
```apex
// Check object CRUD permissions
if (!Schema.sObjectType.Account.isAccessible()) {
    throw new SecurityException('Insufficient permissions to access Account');
}
if (!Schema.sObjectType.Account.isCreateable()) {
    throw new SecurityException('Insufficient permissions to create Account');
}

// Check field-level security (FLS)
if (!Schema.sObjectType.Account.fields.AnnualRevenue.isAccessible()) {
    throw new SecurityException('Insufficient permissions to access AnnualRevenue field');
}

// Use Security.stripInaccessible() for automatic FLS enforcement
SObjectAccessDecision decision = Security.stripInaccessible(
    AccessType.READABLE,
    [SELECT Id, Name, AnnualRevenue FROM Account]
);
List<Account> sanitizedAccounts = decision.getRecords();
```

**3. Governor Limits Strategy**

**Bulkification Patterns**:
```apex
// ❌ BAD: SOQL in loop (governor limit violation)
for (Account acc : accounts) {
    List<Contact> contacts = [SELECT Id FROM Contact WHERE AccountId = :acc.Id];
    // Process contacts
}

// ✅ GOOD: Collect IDs, query once
Set<Id> accountIds = new Set<Id>();
for (Account acc : accounts) {
    accountIds.add(acc.Id);
}
Map<Id, List<Contact>> contactsByAccount = new Map<Id, List<Contact>>();
for (Contact con : [SELECT Id, AccountId FROM Contact WHERE AccountId IN :accountIds]) {
    if (!contactsByAccount.containsKey(con.AccountId)) {
        contactsByAccount.put(con.AccountId, new List<Contact>());
    }
    contactsByAccount.get(con.AccountId).add(con);
}

// Now process
for (Account acc : accounts) {
    List<Contact> contacts = contactsByAccount.get(acc.Id);
    // Process contacts
}
```

**DML Bulkification**:
```apex
// ❌ BAD: DML in loop
for (Account acc : accounts) {
    acc.AnnualRevenue = calculateRevenue(acc);
    update acc;  // DML in loop!
}

// ✅ GOOD: Collect changes, DML once
List<Account> accountsToUpdate = new List<Account>();
for (Account acc : accounts) {
    acc.AnnualRevenue = calculateRevenue(acc);
    accountsToUpdate.add(acc);
}
update accountsToUpdate;  // Single DML
```

---

### Phase 2: IMPLEMENT (Secure Code Generation)

**1. Service Class Pattern**

```apex
/**
 * Service class for [FUNCTIONALITY]
 *
 * @author P&T Team
 * @date 2025-10-25
 */
public with sharing class [ClassName]Service {

    // Constants
    private static final Integer MAX_RECORDS = 200;
    private static final String DEFAULT_STATUS = 'Active';

    /**
     * [Method description]
     *
     * @param records List of records to process
     * @return Map of Id to result
     * @throws SecurityException if insufficient permissions
     * @throws ValidationException if input validation fails
     */
    public Map<Id, Decimal> processRecords(List<[SObjectType]> records) {
        // Input validation
        if (records == null || records.isEmpty()) {
            throw new IllegalArgumentException('Records list cannot be null or empty');
        }

        // Permission check
        if (!Schema.sObjectType.[SObjectType].isAccessible()) {
            throw new SecurityException('Insufficient permissions');
        }

        // Business logic (bulkified)
        Map<Id, Decimal> results = new Map<Id, Decimal>();
        Set<Id> recordIds = new Set<Id>();

        for ([SObjectType] record : records) {
            recordIds.add(record.Id);
        }

        // Query related data (single SOQL)
        Map<Id, [RelatedObject]> relatedMap = new Map<Id, [RelatedObject]>(
            [SELECT Id, [Fields] FROM [RelatedObject] WHERE [ForeignKey] IN :recordIds]
        );

        // Process each record
        for ([SObjectType] record : records) {
            [RelatedObject] related = relatedMap.get(record.[ForeignKey]);
            Decimal result = calculateValue(record, related);
            results.put(record.Id, result);
        }

        return results;
    }

    /**
     * Helper method for calculation
     *
     * @param record Main record
     * @param related Related record
     * @return Calculated value
     */
    private Decimal calculateValue([SObjectType] record, [RelatedObject] related) {
        // Calculation logic
        return 0.0;  // Placeholder
    }
}
```

**2. Trigger Handler Pattern**

```apex
/**
 * Trigger Handler for [SObjectName]
 *
 * Handles all trigger events for [SObjectName] object
 *
 * @author P&T Team
 * @date 2025-10-25
 */
public with sharing class [SObjectName]TriggerHandler {

    // Prevent recursion
    private static Boolean isExecuting = false;

    /**
     * Main entry point from trigger
     */
    public static void handle() {
        if (isExecuting) {
            return;  // Prevent recursion
        }
        isExecuting = true;

        if (Trigger.isBefore) {
            if (Trigger.isInsert) {
                beforeInsert(Trigger.new);
            } else if (Trigger.isUpdate) {
                beforeUpdate(Trigger.oldMap, Trigger.newMap);
            } else if (Trigger.isDelete) {
                beforeDelete(Trigger.oldMap);
            }
        } else if (Trigger.isAfter) {
            if (Trigger.isInsert) {
                afterInsert(Trigger.newMap);
            } else if (Trigger.isUpdate) {
                afterUpdate(Trigger.oldMap, Trigger.newMap);
            } else if (Trigger.isDelete) {
                afterDelete(Trigger.oldMap);
            } else if (Trigger.isUndelete) {
                afterUndelete(Trigger.new);
            }
        }

        isExecuting = false;
    }

    /**
     * Before Insert logic
     */
    private static void beforeInsert(List<[SObjectName]> newRecords) {
        // Validation
        validateRecords(newRecords);

        // Set default values
        setDefaultValues(newRecords);

        // Calculate fields
        calculateFields(newRecords);
    }

    /**
     * Before Update logic
     */
    private static void beforeUpdate(
        Map<Id, [SObjectName]> oldMap,
        Map<Id, [SObjectName]> newMap
    ) {
        // Identify changed records
        List<[SObjectName]> changedRecords = new List<[SObjectName]>();
        for (Id recordId : newMap.keySet()) {
            [SObjectName] oldRecord = oldMap.get(recordId);
            [SObjectName] newRecord = newMap.get(recordId);

            if (hasRelevantChanges(oldRecord, newRecord)) {
                changedRecords.add(newRecord);
            }
        }

        if (!changedRecords.isEmpty()) {
            // Recalculate fields for changed records
            calculateFields(changedRecords);
        }
    }

    /**
     * After Insert logic
     */
    private static void afterInsert(Map<Id, [SObjectName]> newRecordsMap) {
        // Create related records
        createRelatedRecords(newRecordsMap.values());

        // Send notifications (async)
        System.enqueueJob(new NotificationQueueable(newRecordsMap.keySet()));
    }

    /**
     * After Update logic
     */
    private static void afterUpdate(
        Map<Id, [SObjectName]> oldMap,
        Map<Id, [SObjectName]> newMap
    ) {
        // Update related records
        updateRelatedRecords(oldMap, newMap);
    }

    /**
     * Validation helper
     */
    private static void validateRecords(List<[SObjectName]> records) {
        for ([SObjectName] record : records) {
            if (String.isBlank(record.[RequiredField])) {
                record.addError('[RequiredField] is required');
            }
            // Add more validation
        }
    }

    /**
     * Set default values
     */
    private static void setDefaultValues(List<[SObjectName]> records) {
        for ([SObjectName] record : records) {
            if (record.[Field] == null) {
                record.[Field] = 'Default Value';
            }
        }
    }

    /**
     * Calculate derived fields
     */
    private static void calculateFields(List<[SObjectName]> records) {
        // Bulkified calculation logic
    }

    /**
     * Check if record has relevant changes
     */
    private static Boolean hasRelevantChanges(
        [SObjectName] oldRecord,
        [SObjectName] newRecord
    ) {
        return oldRecord.[Field] != newRecord.[Field];
    }

    /**
     * Create related records
     */
    private static void createRelatedRecords(List<[SObjectName]> records) {
        List<[RelatedObject]> relatedToInsert = new List<[RelatedObject]>();

        for ([SObjectName] record : records) {
            [RelatedObject] related = new [RelatedObject](
                [ForeignKey] = record.Id,
                [OtherField] = 'Value'
            );
            relatedToInsert.add(related);
        }

        if (!relatedToInsert.isEmpty()) {
            insert relatedToInsert;
        }
    }

    /**
     * Update related records
     */
    private static void updateRelatedRecords(
        Map<Id, [SObjectName]> oldMap,
        Map<Id, [SObjectName]> newMap
    ) {
        // Query related records
        List<[RelatedObject]> relatedToUpdate = [
            SELECT Id, [Fields]
            FROM [RelatedObject]
            WHERE [ForeignKey] IN :newMap.keySet()
        ];

        // Update related records
        for ([RelatedObject] related : relatedToUpdate) {
            [SObjectName] parent = newMap.get(related.[ForeignKey]);
            related.[Field] = parent.[Field];
        }

        if (!relatedToUpdate.isEmpty()) {
            update relatedToUpdate;
        }
    }
}
```

**Trigger Definition**:
```apex
trigger [SObjectName]Trigger on [SObjectName] (
    before insert, before update, before delete,
    after insert, after update, after delete, after undelete
) {
    [SObjectName]TriggerHandler.handle();
}
```

**3. Batch Class Pattern**

```apex
/**
 * Batch class for [FUNCTIONALITY]
 *
 * Processes large volumes of [SObjectName] records
 *
 * @author P&T Team
 * @date 2025-10-25
 */
public with sharing class [ClassName]Batch implements Database.Batchable<SObject>, Database.Stateful {

    // Stateful counters (persist across batches)
    public Integer recordsProcessed = 0;
    public Integer recordsFailed = 0;

    // Query filter criteria
    private String queryFilter;

    /**
     * Constructor
     */
    public [ClassName]Batch(String queryFilter) {
        this.queryFilter = queryFilter;
    }

    /**
     * Start method - return query locator
     */
    public Database.QueryLocator start(Database.BatchableContext bc) {
        String query = 'SELECT Id, [Fields] FROM [SObjectName]';
        if (String.isNotBlank(queryFilter)) {
            query += ' WHERE ' + queryFilter;
        }
        return Database.getQueryLocator(query);
    }

    /**
     * Execute method - process each batch
     */
    public void execute(Database.BatchableContext bc, List<[SObjectName]> scope) {
        try {
            // Process records
            List<[SObjectName]> recordsToUpdate = new List<[SObjectName]>();

            for ([SObjectName] record : scope) {
                try {
                    // Business logic
                    record.[Field] = calculateValue(record);
                    recordsToUpdate.add(record);
                    recordsProcessed++;
                } catch (Exception e) {
                    // Log error (don't stop batch)
                    System.debug(LoggingLevel.ERROR,
                        'Error processing record ' + record.Id + ': ' + e.getMessage());
                    recordsFailed++;
                }
            }

            // Bulk DML
            if (!recordsToUpdate.isEmpty()) {
                Database.SaveResult[] results = Database.update(recordsToUpdate, false);

                // Check results
                for (Integer i = 0; i < results.size(); i++) {
                    if (!results[i].isSuccess()) {
                        recordsFailed++;
                        System.debug(LoggingLevel.ERROR,
                            'Failed to update record: ' + results[i].getErrors());
                    }
                }
            }
        } catch (Exception e) {
            // Log batch-level error
            System.debug(LoggingLevel.ERROR, 'Batch execute error: ' + e.getMessage());
            recordsFailed += scope.size();
        }
    }

    /**
     * Finish method - send summary email
     */
    public void finish(Database.BatchableContext bc) {
        // Get batch job info
        AsyncApexJob job = [
            SELECT Id, Status, NumberOfErrors, JobItemsProcessed, TotalJobItems
            FROM AsyncApexJob
            WHERE Id = :bc.getJobId()
        ];

        // Send completion email
        String emailBody = 'Batch Job completed\n\n';
        emailBody += 'Status: ' + job.Status + '\n';
        emailBody += 'Total Batches: ' + job.TotalJobItems + '\n';
        emailBody += 'Batches Processed: ' + job.JobItemsProcessed + '\n';
        emailBody += 'Records Processed Successfully: ' + recordsProcessed + '\n';
        emailBody += 'Records Failed: ' + recordsFailed + '\n';

        Messaging.SingleEmailMessage email = new Messaging.SingleEmailMessage();
        email.setToAddresses(new String[] { 'team@apprise.com.au' });
        email.setSubject('[ClassName]Batch Completed');
        email.setPlainTextBody(emailBody);

        Messaging.sendEmail(new Messaging.SingleEmailMessage[] { email });
    }

    /**
     * Helper method
     */
    private Decimal calculateValue([SObjectName] record) {
        // Calculation logic
        return 0.0;
    }

    /**
     * Schedule method (for scheduling batch)
     */
    public static void schedule(String cronExpression) {
        [ClassName]Batch batch = new [ClassName]Batch('Status = \'Active\'');
        System.schedule('[ClassName]Batch', cronExpression, new [ClassName]Schedulable());
    }
}

/**
 * Schedulable wrapper for batch
 */
public class [ClassName]Schedulable implements Schedulable {
    public void execute(SchedulableContext sc) {
        [ClassName]Batch batch = new [ClassName]Batch('Status = \'Active\'');
        Database.executeBatch(batch, 200);  // Batch size 200
    }
}
```

**4. SOQL Injection Prevention**

```apex
// ❌ BAD: SOQL Injection vulnerability
public List<Account> searchAccounts(String accountName) {
    String query = 'SELECT Id, Name FROM Account WHERE Name = \'' + accountName + '\'';
    return Database.query(query);  // SOQL Injection risk!
}

// ✅ GOOD: Bind variables (parameterized)
public List<Account> searchAccounts(String accountName) {
    // Escape single quotes (additional defense)
    accountName = String.escapeSingleQuotes(accountName);

    // Use bind variable (preferred)
    return [SELECT Id, Name FROM Account WHERE Name = :accountName];
}

// ✅ ALSO GOOD: For dynamic SOQL, validate input
public List<SObject> searchRecords(String objectType, String fieldName, String searchValue) {
    // Validate object type (whitelist)
    Set<String> allowedObjects = new Set<String> { 'Account', 'Contact', 'Lead' };
    if (!allowedObjects.contains(objectType)) {
        throw new SecurityException('Invalid object type');
    }

    // Validate field name (against schema)
    Map<String, Schema.SObjectField> fieldMap =
        Schema.getGlobalDescribe().get(objectType).getDescribe().fields.getMap();
    if (!fieldMap.containsKey(fieldName)) {
        throw new SecurityException('Invalid field name');
    }

    // Escape search value
    searchValue = String.escapeSingleQuotes(searchValue);

    // Build safe query
    String query = 'SELECT Id, ' + fieldName + ' FROM ' + objectType +
                   ' WHERE ' + fieldName + ' = :searchValue';
    return Database.query(query);
}
```

**5. External API Integration (Named Credentials)**

```apex
/**
 * Callout to external API using Named Credential
 */
public class [APIName]Service {

    // Named Credential (configured in Salesforce Setup)
    private static final String NAMED_CREDENTIAL = 'callout:[CredentialName]';

    /**
     * Make API call
     */
    public static Map<String, Object> callAPI(String endpoint, Map<String, String> params) {
        // Build request
        HttpRequest req = new HttpRequest();
        req.setEndpoint(NAMED_CREDENTIAL + endpoint);  // Named Credential handles auth
        req.setMethod('GET');
        req.setTimeout(30000);  // 30 seconds
        req.setHeader('Content-Type', 'application/json');

        // Add query parameters
        if (params != null && !params.isEmpty()) {
            String queryString = buildQueryString(params);
            req.setEndpoint(req.getEndpoint() + '?' + queryString);
        }

        // Make callout
        Http http = new Http();
        HttpResponse res = http.send(req);

        // Handle response
        if (res.getStatusCode() == 200) {
            return (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        } else {
            throw new CalloutException('API call failed: ' + res.getStatus());
        }
    }

    /**
     * Build query string from params
     */
    private static String buildQueryString(Map<String, String> params) {
        List<String> parts = new List<String>();
        for (String key : params.keySet()) {
            parts.add(EncodingUtil.urlEncode(key, 'UTF-8') + '=' +
                     EncodingUtil.urlEncode(params.get(key), 'UTF-8'));
        }
        return String.join(parts, '&');
    }
}
```

---

### Phase 3: TEST (75% Coverage Target)

**Test Class Structure**:

```apex
/**
 * Test class for [ClassName]
 *
 * @author P&T Team
 * @date 2025-10-25
 */
@isTest
private class [ClassName]Test {

    /**
     * Test data setup (runs once per test class)
     */
    @TestSetup
    static void setup() {
        // Create test data (dummy data only)
        List<Account> accounts = new List<Account>();
        for (Integer i = 0; i < 200; i++) {
            accounts.add(new Account(
                Name = 'Test Account ' + i,
                Industry = 'Technology',
                AnnualRevenue = 1000000
            ));
        }
        insert accounts;

        List<Contact> contacts = new List<Contact>();
        for (Account acc : accounts) {
            contacts.add(new Contact(
                FirstName = 'Test',
                LastName = 'Contact ' + acc.Name,
                AccountId = acc.Id,
                Email = 'test' + acc.Id + '@example.com'
            ));
        }
        insert contacts;
    }

    /**
     * Test positive scenario (happy path)
     */
    @isTest
    static void testProcessRecords_Success() {
        // Setup
        List<Account> accounts = [SELECT Id, Name FROM Account LIMIT 10];

        // Execute
        Test.startTest();
        Map<Id, Decimal> results = new [ClassName]Service().processRecords(accounts);
        Test.stopTest();

        // Assert
        System.assertEquals(10, results.size(), 'Should process all 10 accounts');
        for (Decimal result : results.values()) {
            System.assert(result != null, 'Result should not be null');
        }
    }

    /**
     * Test bulk processing (governor limits)
     */
    @isTest
    static void testProcessRecords_Bulk() {
        // Setup
        List<Account> accounts = [SELECT Id, Name FROM Account];  // 200 records

        // Execute
        Test.startTest();
        Map<Id, Decimal> results = new [ClassName]Service().processRecords(accounts);
        Test.stopTest();

        // Assert
        System.assertEquals(200, results.size(), 'Should process all 200 accounts');
        System.assert(Limits.getQueries() < 100, 'Should not exceed SOQL limit');
        System.assert(Limits.getDMLStatements() < 150, 'Should not exceed DML limit');
    }

    /**
     * Test negative scenario (error handling)
     */
    @isTest
    static void testProcessRecords_NullInput() {
        // Execute & Assert
        try {
            new [ClassName]Service().processRecords(null);
            System.assert(false, 'Should have thrown exception');
        } catch (IllegalArgumentException e) {
            System.assert(e.getMessage().contains('null'), 'Should mention null');
        }
    }

    /**
     * Test security scenario (insufficient permissions)
     */
    @isTest
    static void testProcessRecords_InsufficientPermissions() {
        // Create user with limited permissions
        Profile prof = [SELECT Id FROM Profile WHERE Name = 'Standard User' LIMIT 1];
        User testUser = new User(
            FirstName = 'Test',
            LastName = 'User',
            Email = 'testuser@example.com',
            Username = 'testuser' + System.now().getTime() + '@example.com',
            Alias = 'tuser',
            TimeZoneSidKey = 'America/Los_Angeles',
            LocaleSidKey = 'en_US',
            EmailEncodingKey = 'UTF-8',
            ProfileId = prof.Id,
            LanguageLocaleKey = 'en_US'
        );
        insert testUser;

        // Execute as test user
        System.runAs(testUser) {
            List<Account> accounts = [SELECT Id FROM Account LIMIT 1];

            try {
                new [ClassName]Service().processRecords(accounts);
                // May succeed or fail depending on permissions
            } catch (SecurityException e) {
                System.assert(e.getMessage().contains('permissions'));
            }
        }
    }

    /**
     * Test batch class
     */
    @isTest
    static void testBatchExecution() {
        // Execute
        Test.startTest();
        [ClassName]Batch batch = new [ClassName]Batch('Industry = \'Technology\'');
        Database.executeBatch(batch, 200);
        Test.stopTest();

        // Assert
        AsyncApexJob job = [
            SELECT Status, NumberOfErrors
            FROM AsyncApexJob
            WHERE JobType = 'BatchApex'
            AND ApexClass.Name = '[ClassName]Batch'
            LIMIT 1
        ];
        System.assertEquals('Completed', job.Status, 'Batch should complete');
        System.assertEquals(0, job.NumberOfErrors, 'Should have no errors');
    }
}
```

**Test Coverage Tips**:
- Use @TestSetup for data creation (shared across tests, faster)
- Test.startTest() / Test.stopTest() reset governor limits
- Test bulk scenarios (200+ records) to catch bulkification issues
- Test security with System.runAs()
- Test error handling (try/catch assertions)
- Mock callouts with Test.setMock()

---

## Output Expected

1. **Implementation File**: `[ClassName].cls`
   - Production-ready APEX code
   - Bulkified (handles collections)
   - Secure (with sharing, FLS/CRUD checks, SOQL injection prevention)
   - Well-documented (docstrings)

2. **Test File**: `[ClassName]Test.cls`
   - ≥75% test coverage
   - @TestSetup for data
   - Positive, negative, security, bulk scenarios
   - Assertions with clear messages

3. **Trigger** (if applicable): `[SObjectName]Trigger.trigger`

---

## Related Templates

- Use `../core-workflows/secure_feature_development.md` for overall feature development
- Use `../core-workflows/code_review_request.md` for code review
- Use `../security/security_review.md` for security audit

---

**Template Version**: 1.0
**Last Updated**: October 2025
**Owner**: P&T Team / AI Approach Project
