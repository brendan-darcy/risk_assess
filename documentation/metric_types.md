# CoreLogic Metric Types

Learn all about the different metric types we provide for Market Trends & Census data.

## Overview

Market Trends is an essential tool for anyone that wants to truly understand the housing market at a micro level across Australia and New Zealand, including any business involved in the housing market.

Our Market Trends data is available via our Statistics service and Charts service. These services allow you to view time series (or trend) data for one or more metrics, locations and property types in order to understand the trend and historical performance of the metric.

## Market Trends API Request Format

### Example Request

```json
{
  "locationId": "14489",
  "locationTypeId": 8,
  "propertyTypeId": 1,
  "fromDate": "2019-02-01",
  "toDate": "2020-02-01",
  "metricTypeId": 21,
  "interval": 1
}
```

### Request Parameters

| Field | Required? | Type | Description | Example |
|-------|-----------|------|-------------|---------|
| `fromDate` | No | Date | The start date for the data required in the series in format YYYY-MM-DD. This is mandatory if toDate is entered. Defaults to return most recent available data. | `"fromDate": "2012-02-29"` |
| `toDate` | No | Date | The end date for the data required in the series in format YYYY-MM-DD. Defaults to fromDate + 12 months (or today's date whichever is lesser). | `"toDate": "2013-03-31"` |
| `interval` | No | Integer | Determines the intervals for the data returned and are calculated from the recent date which has metric values in a requested range. For example, 1 = monthly, 2 = every two months, 3 = quarterly, 6 = half yearly, 12 = yearly, 24= 2 years, etc. Defaults to 1. | `"interval": 1` |
| `locationId` | Yes | Integer | A unique identifier for the location in a given location type. | `"locationId": 7926` |
| `locationTypeId` | Yes | Integer | A unique identifier for the location or area type. | `"locationTypeId": 8` |
| `chartType` | No | Integer | The chartType can override any chartType from sN.cTId and default chartType from metric type group. | `"chartType": 5` |
| `metricTypeGroupId` | No | Integer | Returns all metric types for a requested metric type group. Only required if metricTypeId is not passed and cannot be passed in conjunction with metricTypeId. | `"metricTypeGroupId": 1` |
| `metricTypeId` | No | Integer | A unique identifier for the metric. Only required if metricGroupId is not passed and cannot be passed in conjunction with metricGroupId. | `"metricTypeId": 21` |
| `propertyTypeId` | Yes | Integer | A unique identifier for the type of property. | `"propertyTypeId": 1` |

### Location Type IDs

- **2** = Country (AU/NZ)
- **3** = Council Area (AU only)
- **4** = Postcode (AU only)
- **7** = State (AU only)
- **8** = Locality (Suburb) (AU/NZ)
- **9** = Territorial Authority (NZ only)

### Chart Type IDs

- **1** = SPLINE
- **2** = LINE
- **3** = COLUMN
- **4** = AREA
- **5** = PIE
- **6** = BAR

### Metric Type Group IDs

- **1** = Number Sold by Price (12 months)
- **2** = Median Price by Price (12 months)
- **3** = Percentile Sale Price (12 months)

### Property Type IDs

**Australia specific property types:**
- **1** = Houses
- **2** = Units
- **3** = Land

**New Zealand specific property types:**
- **4** = Apartments
- **5** = Flats
- **6** = Residential dwellings (Houses, Apartments, Flats)

## Market Trends Metrics

### Sold Metrics

The Sold metrics provide statistics based off property sales.

*Sales-based metrics are lagged. Meaning they are current as of the latest reporting period minus 3 months.*

| ID | Display Name | Definition | AU Data | NZ Data |
|----|--------------|------------|---------|---------|
| 3 | Average GPO Distance | The average distance from the GPO of those properties that transacted over the last 12 months. | ✓ | |
| 4 | Average Hold Period (years) | The average number of years a property has been held between sales. | ✓ | |
| 5 | Average Land Area | The average size of land of those properties that transacted over the last 12 months. | ✓ | |
| 12 | Annual Change in Median Price (10 years) | The compounding annual change in median sale price based on the current period compared with the same period 10 years ago. | ✓ | |
| 13 | Annual Change in Median Price (20 years) | The compounding annual change in median sale price based on the current period compared with the same period 20 years ago. | ✓ | |
| 14 | Annual Change in Median Price (5 years) | The compounding annual change in median sale price based on the current period compared with the same period 5 years ago. | ✓ | |
| 19 | Change in Median Price (5 years) | The difference between the median sale prices in the current period (last 12 months) compared to the same period five years ago. | ✓ | |
| 20 | Median Vendor Discount (12 months) | The median difference between the contract price on a property and the first advertised price. | ✓ | |
| 21 | Median Sale Price (12 months) | The middle sale price of all transactions recorded during the 12 month period. | ✓ | |
| 22 | Median Sale Price (350K to 750K) | The middle price of all transactions above $350,000 and under $750,000 recorded during the 12 month period. | ✓ | |
| 23 | Median Sale Price (6 months) | The middle sale price of all transactions recorded during the 6 month period. | ✓ | |
| 24 | Median Sale Price (over 750K) | The middle price of all transactions above $750,000 recorded during the 12 month period. | ✓ | |
| 25 | Median Sale Price (past 3 months) | The middle sale price of all transactions recorded during the 3 month period. | ✓ | |
| 26 | Median Sale Price (under 350K) | The middle price of all transactions under $350,000 recorded during the 12 month period. | ✓ | |
| 28 | Median Land Size (12 months) | The median size in square meters of all blocks of vacant land that have sold over the past year. | ✓ | |
| 29 | Median Land Size (3 months) | The median size in square meters of all blocks of vacant land that have sold over the past three months. | ✓ | |
| 30 | Median Land Price per SQM (12 months) | The median price per square meter for vacant land sold over the past 12 months. | ✓ | |
| 31 | Median Land Price per SQM (3 months) | The median price per square meter for vacant land sold over the past 3 months. | ✓ | |
| 32 | Median Days on Market (12 months) | The median number of days it has taken to sell those properties sold by private treaty sale during the last 12 months. | ✓ | |
| 35 | Change in Sales Volumes (monthly) | The percentage change in sales volumes within the specified region in the current period compared to the same period 1 month ago. | ✓ | |
| 37 | Number Sold (12 months) | A count of all transactions within the specified region over the last 12 months. | ✓ | |
| 38 | Number Sold (6 Months) | A count of all transactions within the specified region over the last 6 months. | ✓ | |
| 39 | Number Sold (monthly) | A count of all transactions within the specified region over the last month. | ✓ | |
| 40 | Number Sold (past 3 months) | A count of all transactions within the specified region over the last 3 months. | ✓ | |
| 42 | Lower Quartile (12 months) | The 25th percentile sale price of sales over the past 12 months within the geography. | ✓ | |
| 43 | Upper Quartile (12 months) | The 75th percentile sale price of sales over the past 12 months within the geography. | ✓ | |
| 45 | Change in Sales Volumes (3 months) | The percentage change in sales volumes within the specified region in the current period compared to the same period 3 months ago. | ✓ | |
| 46 | Change in Median Price (quarter) | The difference between the median sale price in the current period (last 12 months) compared to the same period 3 months ago. | ✓ | |

### Price Bracket Metrics

| ID | Display Name | Definition | AU Data | NZ Data |
|----|--------------|------------|---------|---------|
| 51 | Number Sold between $1m and $2m (12 months) | A count of all transactions within the specified region over the last 12 months that have sold for between $1,000,000 and $1,999,999.99. | ✓ | |
| 52 | Number Sold between $200k and $400k (12 months) | A count of all transactions within the specified region over the last 12 months that have sold for between $200,000 and $399,999.99. | ✓ | |
| 53 | Number Sold above $2m (12 months) | A count of all transactions within the specified region over the last 12 months that have sold for more than $2,000,000. | ✓ | |
| 54 | Number Sold for less than $200k (12 months) | A count of all transactions within the specified region over the last 12 months that have sold for less than $200,000. | ✓ | |
| 55 | Number Sold between $400k and $600k (12 months) | A count of all transactions within the specified region over the last 12 months that have sold for between $400,000 and $599,999.99. | ✓ | |
| 56 | Number Sold between $600k and $800k (12 months) | A count of all transactions within the specified region over the last 12 months that have sold for between $600,000 and $899,999.99. | ✓ | |
| 57 | Number Sold between $800k and $1m (12 months) | A count of all transactions within the specified region over the last 12 months that have sold for between $800,000 and $999,999.99. | ✓ | |

### Additional Sales Metrics

| ID | Display Name | Definition | AU Data | NZ Data |
|----|--------------|------------|---------|---------|
| 61 | Change in Median Price (3 years) | The difference between the median sale prices in the current period (last 12 months) compared to the same period three years ago. | ✓ | |
| 66 | Total Value of Sales (12 months) | The total value of all property transactions recorded over the past year within the geography. | ✓ | |
| 67 | Total Value of Sales (monthly) | The total value of all property transactions recorded over the past month within the geography. | ✓ | |
| 68 | Stock Turnover (12 months) | The percentage of total dwellings within the specified region that have sold over the last 12 months. | ✓ | |
| 69 | Change in Median Price (12 months) | The difference between the median sale prices in the current period (last 12 months) compared to the same period 12 months ago. | ✓ | |
| 71 | Change in Sales Volumes (12 months) | The percentage change in sales volumes within the specified region in the current period compared to the same period 12 months ago. | ✓ | |
| 75 | Median Days on Market (12 months) | The median number of days it has taken to sell all properties during the last 12 months. | ✓ | |
| 82 | Sale price / CV ratio (3 months) | The percentage difference between sale price and CV over the past 3 months. | | ✓ |

### CoreLogic RP Data Mortgage Index (RMI)

| ID | Display Name | Definition | AU Data | NZ Data |
|----|--------------|------------|---------|---------|
| 95 | CoreLogic RP Data Mortgage Index (RMI) | CoreLogic systems monitor more than 100,000 mortgage activity events every month across our four main finance industry platforms. | ✓ | |
| 96 | CoreLogic RP Data Mortgage Index (RMI) Change (12 months) | The 12 month change compares the change in the index value over the last 12 months. | ✓ | |
| 97 | Total CoreLogic RP Data Mortgage Index (RMI) Events (per client) | The total count over the past four weeks of valuations run across CoreLogic's four main finance industry platforms divided by total clients. *Unavailable geographies: National, State, Suburb* | ✓ | |
| 98 | Total CoreLogic RP Data Mortgage Index (RMI) Events | The total count over the past four weeks of valuations run across CoreLogic's four main finance industry platforms. *Unavailable geographies: National, State, Suburb* | ✓ | |

## For Sale Metrics

The For Sale metrics provide statistics based off property's for sale advertisement campaigns.

| ID | Display Name | Definition | AU Data | NZ Data |
|----|--------------|------------|---------|---------|
| 1 | Total Auction Listings (12 months) | The total number of auction listings that have been observed over the past year within the geography. | ✓ | |
| 34 | Change in Listings (monthly) | The percentage change in listings within the specified region in the current period compared to the same period 1 month ago. | ✓ | |
| 36 | Total New Listings (12 months) | The total number of new listings recorded across the Geography over the past year. | ✓ | |
| 44 | Change in Listings (3 months) | The percentage change in listings within the specified region in the current period compared to the same period 3 months ago. | ✓ | |
| 58 | % Stock on Market (12 months) | The percentage of dwellings within the suburb that have been listed for sale over the past year. | ✓ | |
| 64 | Total Listings (12 months) | The total unique number of properties that have been advertised for sale and captured by CoreLogic over the past year. | ✓ | |
| 65 | Total Listings (monthly) | The total unique number of properties that have been advertised for sale and captured by CoreLogic over the past month. | ✓ | |
| 70 | Change in Listings (12 months) | The percentage change in listings within the specified region in the current period compared to the same period 12 months ago. | ✓ | |

## Rental Metrics

The Rental metrics provide statistics based off property's rental advertisement campaigns.

| ID | Display Name | Definition | AU Data | NZ Data |
|----|--------------|------------|---------|---------|
| 10 | Value based Gross Rental Yield | Is calculated based on the annualised rent (Median Asking Rent x 52 weeks), divided by the median value of those properties advertised for rent. *Unavailable geographies: Postcode* | ✓ | |
| 47 | Change in Rental Rate (12 months) | The difference between the median weekly advertised rental rate in the current period compared to the same period 12 months ago. | ✓ | |
| 48 | Change in Rental Rate (5 years) | The difference between the median weekly advertised rental rate in the current period compared to the same period 5 years ago. | ✓ | |
| 49 | Median Asking Rent (12 months) | The middle value of advertised weekly rents captured by CoreLogic during the 12 month period. | ✓ | |
| 50 | Rental Rate Observations (12 months) | The number of observations that have been used to calculate the 'Median Asking Rent' figure. | ✓ | |
| 77 | Median Asking Rent (quarterly) | The middle value of weekly rents captured by NZ Government during the last quarter. | | ✓ |
| 78 | Rental Rate Observations (quarterly) | The number of observations that have been used to calculate the Median Asking Rent figure. | | ✓ |
| 79 | Change in Rental Rate (12 months) | The difference between the median rental rate in the current period compared to the same period 12 months ago. | | ✓ |
| 80 | Value Based Gross Rental Yield | Is calculated based on the annualised rent (Median Asking Rent x 52 weeks), divided by the median value of properties within the geography. | | ✓ |

## Valuation Metrics

The Valuation metrics provide statistics based off property's valuation amounts.

| ID | Display Name | Definition | AU Data | NZ Data |
|----|--------------|------------|---------|---------|
| 8 | Automated Valuation Observations | The total number of Automated Valuations that have been run within the geography. *Unavailable geographies: Council* | ✓ | |
| 9 | AVM Value Change (3 months) | The difference between the current median value and the median value three months prior. *Unavailable geographies: Council, Postcode* | ✓ | |
| 11 | Median Value (monthly) | The middle value of all properties across the geography based on the Automated Valuation Model. *Unavailable geographies: Council* | ✓ | |
| 17 | Median Value Accumulation (monthly) | Growth between the last sale price and the current AVM value expressed in dollar terms. *Unavailable geographies: Council* | ✓ | |
| 18 | Median Value Accumulation (%) | Growth between the last sale price and the current AVM value expressed as a percentage. *Unavailable geographies: Council* | ✓ | |
| 72 | AVM Value Change (5 years) | The difference between the current median value and the median value five years prior. | ✓ | |
| 73 | Stratified Median Value (monthly) | The stratified median value of all properties across the geography based on the Automated Valuation Model. | ✓ | |
| 83 | AVM Value Change (3 months) | The difference between the current median value and the median value three months prior. | | ✓ |
| 84 | AVM Value Change (12 months) | The difference between the current median value and the median value one year prior. | | ✓ |
| 85 | AVM Value Change (3 years) | The difference between the current median value and the median value three years prior. | | ✓ |
| 86 | Average Value | The average value of all developed residential properties in the area based on the latest monthly property value index. | | ✓ |
| 87 | Annual Property Value Change | The difference between the current average value and the average value one year prior. | | ✓ |
| 88 | Change in Median Value (12 months) | The difference between the median value in the current period compared to the same period 12 months ago. *Unavailable geographies: Council, Postcode* | ✓ | |
| 89 | Change in Median Value (3 years) | The difference between the median value in the current period compared to the same period three years ago. *Unavailable geographies: Council, Postcode* | ✓ | |
| 90 | Change in Median Value (5 years) | The difference between the median value in the current period compared to the same period five years ago. *Unavailable geographies: Council, Postcode* | ✓ | |

## Property Metrics

The Property metrics provide statistics based off property's attributes.

| ID | Display Name | Definition | AU Data | NZ Data |
|----|--------------|------------|---------|---------|
| 63 | Total Dwellings | The number of dwelling located within the defined area. | ✓ | |
| 81 | Average Land Area | The average size of land of all properties. | | ✓ |

---

# Census Data

Our census data is available via our Census Statistics and Charts services. The Census metrics available contain census data as gathered by the Australian Bureau of Statistics (ABS) and Statistics New Zealand.

## Country of Birth Metrics

The Country of Birth Metrics relate to the countries of birth for the residents in a particular location.

| Group Metric ID | Metric ID | Display Name | Definition |
|-----------------|-----------|--------------|------------|
| 102 | 1046 | Country of Birth: Australia | The percentage breakdown of residents born in Australia in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1047 | Country of Birth: Canada | The percentage breakdown of residents born in Canada in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1048 | Country of Birth: China | The percentage breakdown of residents born in China in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1049 | Country of Birth: Croatia | The percentage breakdown of residents born in Croatia in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1050 | Country of Birth: Egypt | The percentage breakdown of residents born in Egypt in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1051 | Country of Birth: Fiji | The percentage breakdown of residents born in Fiji in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1052 | Country of Birth: France | The percentage breakdown of residents born in France in the geographical area. Available: 2016, 2021. |
| | 1053 | Country of Birth: Germany | The percentage breakdown of residents born in Germany in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1054 | Country of Birth: Greece | The percentage breakdown of residents born in Greece in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1055 | Country of Birth: Hong Kong | The percentage breakdown of residents born in Hong Kong in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1056 | Country of Birth: India | The percentage breakdown of residents born in India in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1057 | Country of Birth: Indonesia | The percentage breakdown of residents born in Indonesia in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1058 | Country of Birth: Ireland | The percentage breakdown of residents born in Ireland in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1059 | Country of Birth: Italy | The percentage breakdown of residents born in Italy in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1060 | Country of Birth: Korea | The percentage breakdown of residents born in Korea in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1061 | Country of Birth: Lebanon | The percentage breakdown of residents born in Lebanon in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1062 | Country of Birth: Macedonia | The percentage breakdown of residents born in Macedonia in the geographical area. Available: 2006, 2011, 2016. |
| | 1063 | Country of Birth: Malaysia | The percentage breakdown of residents born in Malaysia in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1064 | Country of Birth: Malta | The percentage breakdown of residents born in Malta in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1065 | Country of Birth: Netherlands | The percentage breakdown of residents born in Netherlands in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1066 | Country of Birth: New Zealand | The percentage breakdown of residents born in New Zealand in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1067 | Country of Birth: Philippines | The percentage breakdown of residents born in Philippines in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1068 | Country of Birth: Poland | The percentage breakdown of residents born in Poland in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1069 | Country of Birth: Singapore | The percentage breakdown of residents born in Singapore in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1070 | Country of Birth: South Africa | The percentage breakdown of residents born in South Africa in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1071 | Country of Birth: Sri Lanka | The percentage breakdown of residents born in Sri Lanka in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1072 | Country of Birth: Turkey | The percentage breakdown of residents born in Turkey in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1073 | Country of Birth: UK | The percentage breakdown of residents born in UK in the geographical area. Available: 2006, 2011. |
| | 1074 | Country of Birth: USA | The percentage breakdown of residents born in USA in the geographical area. Available: 2006, 2011, 2016, 2021. |
| | 1075 | Country of Birth: Vietnam | The percentage breakdown of residents born in Vietnam in the geographical area. Available: 2006, 2011, 2016, 2021. |

*[Additional census metrics continue with Education, Employment & Occupation, Household, Population, Religion, and Suburb Information sections...]*

---

*© RP Data Pty Limited trading as CoreLogic (ABN 67 087 759 171) and CoreLogic NZ Limited trading as CoreLogic (NZCN 1129102) 2025. All rights reserved.*