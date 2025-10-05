# CoreLogic Address Match API

**Base URL:** `api-sbox.corelogic.asia`  
**OAS Version:** 2.0

## Overview

Locate a property and its corresponding CoreLogic identifier for use in subsequent calls to our APIs with this simple tool. Our address matcher takes a single supplied address string and matches it to a valid property from our dataset.

Our ability to find an address supplied by you and match it to what we have in our datasets is vital to our success as a business in enabling you to discover more about a property or find more property-related information. This service utilizes AddressRight, our industry-leading address matching algorithm, and takes our ability to find addresses for you to a new level.

### Recommended Address Format

We recommend providing the address in the following format to get the best chance for a match:

```
[unitNumber] / [streetNumber] [streetName] [streetType] [suburb] [stateCode] [postcode]
```

**Examples:**
- `1A/10 Smith St Smithville QLD 4000`
- `U 1 10 Smith St Smithville QLD 4000`

## API Endpoint

### Address Matcher (AU)

```
GET /search/au/matcher/address
```

**Authorization:** Bearer token required

## Match Code Definition

Each record processed will be output with a **Match Code**. You can use this code to understand the level of matching performed, what processes the record went through, and any alterations to the record that have been made.

The code consists of **13 alphanumeric characters**, split into 4 sections with each section defining a particular part of the processing.

## Address Match Types

The following table lists the definitions for the first character output as part of the Match Code. The codes are mutually exclusive and are executed in the order indicated by the hierarchy.

| Hierarchy | Code | Definition |
|-----------|------|------------|
| 1 | **E** | Exact match to property found |
| 2 | **A** | Alias match to property found |
| 3 | **P** | Partial match to property found |
| 4 | **F** | Fuzzy match to property found |
| 5 | **B** | Building level match found |
| 6 | **S** | Street level match found |
| 7 | **X** | Input address represents a postal record |
| 8 | **D** | Duplicate record found - no result possible |
| 9 | **N** | Non-Match |
| 10 | **M** | Input address elements missing / no match could be performed |
| 11 | **Q** | Input used for parsing - batch mode only |

## Address Match Rules

The Address Match Rule is a more granular view of the Address Match Type and you can use it to understand the exact rule that the API used to recognize the match. You may wish to use this level of granularity to decide what constitutes a match and what doesn't.

Where a match could not be found and the API returns the record with an unmatched address match rule, the API will return no `property_ID` with the record.

### Match Rule Mapping

*Note: this is a reduced rule set available via the API only. Please request a copy of the AddressRightAU Technical Guide for the full rule set returned in batch processing.*

| Match Rule ID | Match Type Rule | Rule Description |
|---------------|-----------------|------------------|
| 000 | Match Type = 'N' | No match was found to any of the listed rules but a match was attempted |
| 001 | When Address Update Indicator = 'O' then 'E' Else 'P' | Match on DPID |
| 002 | When Address Update Indicator = 'O' then 'E' Else 'P' | Match on full address |
| 039 | When Address Update Indicator = 'O' then 'E' Else 'P' | DPID match on house or unit |
| 040 | When Address Update Indicator = 'O' then 'E' Else 'P' | Match on trusted DPIDs only, based on GeoResult codes |
| 003 | Match Type = 'P' | Match on full address ignoring the end house number when in a range |
| 004 | Match Type = 'P' | Match on full address ignoring the start house number when in a range |
| 005 | Match Type = 'P' | Match on full address where source house number 1 matches target house number 2 |
| 006 | Match Type = 'P' | Match on full address matching source end number to target start number |
| 007 | Match Type = 'P' | Match on full address ignoring postcode |
| 008 | Match Type = 'P' | Match on full address ignoring locality |
| 010 | Match Type = 'P' | Match on full address ignoring house number 2 and locality |
| 017 | Match Type = 'P' | Match on full address ignoring lot number |
| 018 | Match Type = 'P' | Match on full address ignoring lot number and house number 2 |
| 028 | Match Type = 'P' | Match unit number to lot number |
| 030 | Match Type = 'P' | Match on full address ignoring st type |
| 070 | Match Type = 'P' | Match on full address ignoring house number suffixes |
| 102 | Match Type = 'P' | Match on Alternate lot number |
| 046 | Match Type = 'P' | Match unit number to lot number ignoring house number 2 |
| 048 | Match Type = 'P' | Match lot number to house number |
| 024 | Match Type = 'F' | Fuzzy match |
| 038 | Match Type = 'B' | Match DPID to PDPID where DPID > 30000000 and DPID is unique |
| 049 | 'E' or 'P' | Straight match on a full lot address |
| 060 | 'X' | PO Box address has been found - no match attempted |
| 061 | Match Type = 'M' | Address information missing - no match attempted |
| 062 | Match Type = 'M' | Address parse critical failure - no match attempted |
| 063 | Match Type = 'M' | Empty street name - no match attempted |
| 064 | Match Type = 'M' | State is missing - no match attempted |
| 075 | Match Type = 'P' | Straight match on full address using standardized street name |
| 241 | Match Type = 'S' | Suburb & Street Match |
| 242 | Match Type = 'B' | Match building on full address excluding unit |
| 243 | Match Type = 'S' | Postcode & Street Match |
| 255 | Match Type = 'D' | Duplicate found - the API does not return a property ID for rules that do not allow the return of duplicates |

## Address Update Indicator

The purpose of the Address Update Indicator is to identify whether the original input record has been altered, either by pre-parse cleansing or by geocoder. Address updates account for any human or input errors by reformatting or updating an address with any missing elements. The API was designed in this way to improve match rates. However, the address update indicator gives you the option to discard matches that have been updated.

| Address Update Indicator | Business Rule |
|--------------------------|---------------|
| **O (Original)** | The source property record has had no significant changes made to it before matching. The API will also return a value of 'O' when the record has not been matched due to missing address elements (MatchType = M) |
| **U (Updated)** | The source property record may have been updated from its original |

*Note: the API will never class altered address records as an Exact Match as they will always differ from the original source record provided.*

## Address Update Detail

The Address Update Detail section of the match code provides information on what changes (if any) were made to the original source record. Use this information to decide whether you want to accept the match or not.

Multiple changes can be made to a record. Codes are therefore concatenated with the maximum being an 8-digit number and the minimum being a 2-digit number. For example, the code `1322` would indicate that a locality correction (13) and a postcode correction/change (22) has occurred on the record.

| Detail Code | Description |
|-------------|-------------|
| 00000000 | No significant changes made |
| 10 | Address field(s) appear to contain non-address data |
| 13 | Locality Correction |
| 21 | State change/correction |
| 22 | Postcode change/correction |
| 24 | Street Name correction |
| 25 | Street Type change/correction |
| 33 | Street number range incorrect |
| 34 | Ambiguous street number match |
| 36 | Lot number and street number ambiguity, street number used to match |
| 59 | Unable to Geocode and/or GeoURN record |
| 99 | Remaining GeoCode Results |

## Security

- **Protocol:** HTTPS only
- **Authentication:** OAuth2 Bearer token required

## Summary of Components

The matching solution for our APIs is made up of 4 main components:

1. **Address Match Type** - High-level classification of match quality
2. **Address Match Rule** - Granular rule that determined the match
3. **Address Update Indicator** - Whether the address was modified
4. **Address Update Detail** - Specific changes made to the original address

This comprehensive matching system ensures high-quality address resolution while providing transparency into the matching process and any modifications made to achieve a match.

---

*© RP Data Pty Limited trading as CoreLogic (ABN 67 087 759 171) and CoreLogic NZ Limited trading as CoreLogic (NZCN 1129102) 2025. All rights reserved.*