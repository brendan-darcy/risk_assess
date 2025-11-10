# Property Images Fetcher

Fetches property images from CoreLogic Property Images API and generates comprehensive JSON reports with metadata and summary statistics.

## Overview

The Property Images script retrieves all available images for a property from CoreLogic API and creates a detailed JSON report including:
- **Metadata**: Property ID, address, timestamp, API status
- **Summary Statistics**: Total images, image types, available sizes, scan dates
- **Image Details**: URLs for all available sizes (original, large, medium, thumbnail)
- **Image Categories**: Default image, secondary images, floor plans

## Files

- **`scripts/fetch_property_images.py`** - Main script to fetch images and generate report
- **`scripts/utils/property_images_client.py`** - API client for CoreLogic Images endpoint
- **Output**: `data/property_reports/{property_id}_property_images.json`

## Requirements

### Environment Variables

```bash
export CORELOGIC_CLIENT_ID="your_client_id"
export CORELOGIC_CLIENT_SECRET="your_client_secret"
```

Or add to `.env` file:
```
CORELOGIC_CLIENT_ID="your_client_id"
CORELOGIC_CLIENT_SECRET="your_client_secret"
```

### Python Dependencies

```bash
pip install requests python-dotenv
```

## Usage

### Basic Usage

```bash
python3 scripts/fetch_property_images.py --property-id 13683380
```

### With Property Address (for metadata)

```bash
python3 scripts/fetch_property_images.py \
  --property-id 13683380 \
  --address "5 Settlers Court, Vermont South VIC 3133"
```

### Custom Output Directory

```bash
python3 scripts/fetch_property_images.py \
  --property-id 13683380 \
  --output-dir data/images
```

### Production API (vs Sandbox)

```bash
python3 scripts/fetch_property_images.py \
  --property-id 13683380 \
  --base-url https://api.corelogic.asia
```

## API Endpoint

```
GET /property-details/au/properties/{propertyId}/images
```

**Base URLs:**
- Sandbox (UAT): `https://api-sbox.corelogic.asia`
- Production: `https://api.corelogic.asia`

## Output Format

### Successful Response

```json
{
  "metadata": {
    "property_id": 13683380,
    "property_address": "5 Settlers Court, Vermont South VIC 3133",
    "extraction_timestamp": "2025-11-10T15:30:00.123456",
    "api_endpoint": "/property-details/au/properties/13683380/images",
    "status": "success"
  },
  "summary": {
    "total_images": 15,
    "has_default_image": true,
    "secondary_images_count": 12,
    "floor_plan_images_count": 2,
    "image_types": ["default", "secondary", "floor_plans"],
    "available_sizes": [
      "large_768x512",
      "medium_470x313",
      "original",
      "thumbnail_320x215"
    ],
    "oldest_scan_date": "2021-06-03",
    "newest_scan_date": "2023-08-15",
    "unique_scan_dates": 3
  },
  "default_image": {
    "digital_asset_type": "Image",
    "scan_date": "2021-06-03",
    "urls": {
      "original": {
        "url": "https://images.corelogic.asia/0x0/assets/perm/...",
        "size": "0x0 (original)"
      },
      "large": {
        "url": "https://images.corelogic.asia/768x512/...",
        "size": "768x512"
      },
      "medium": {
        "url": "https://images.corelogic.asia/470x313/...",
        "size": "470x313"
      },
      "thumbnail": {
        "url": "https://images.corelogic.asia/320x215/...",
        "size": "320x215"
      }
    }
  },
  "secondary_images": [
    {
      "digital_asset_type": "Image",
      "scan_date": "2021-06-03",
      "urls": {
        "original": {"url": "...", "size": "0x0 (original)"},
        "large": {"url": "...", "size": "768x512"},
        "medium": {"url": "...", "size": "470x313"},
        "thumbnail": {"url": "...", "size": "320x215"}
      }
    }
  ],
  "floor_plan_images": [
    {
      "digital_asset_type": "FloorPlan",
      "scan_date": "2022-03-15",
      "urls": {
        "original": {"url": "...", "size": "0x0 (original)"},
        "large": {"url": "...", "size": "768x512"}
      }
    }
  ],
  "raw_response": {
    "defaultImage": {...},
    "secondaryImageList": [...],
    "floorPlanImageList": [...]
  }
}
```

### Error Response

```json
{
  "property_id": 13683380,
  "property_address": "5 Settlers Court, Vermont South VIC 3133",
  "extraction_timestamp": "2025-11-10T15:15:38.778507",
  "status": "error",
  "error": "API error: 401",
  "message": "Unauthorized: Invalid API call as no apiproduct match found",
  "summary": {
    "total_images": 0,
    "has_default_image": false,
    "secondary_images_count": 0,
    "floor_plan_images_count": 0
  }
}
```

## Console Output

```
🔄 Fetching images for property 13683380...
✅ Report saved: data/property_reports/13683380_property_images.json

======================================================================
📸 PROPERTY IMAGES REPORT SUMMARY
======================================================================

🏠 Property: 13683380
   Address: 5 Settlers Court, Vermont South VIC 3133
   Status: SUCCESS

📊 Image Statistics:
   Total Images: 15
   Default Image: ✓ Yes
   Secondary Images: 12
   Floor Plans: 2

📐 Available Sizes:
   • large_768x512
   • medium_470x313
   • original
   • thumbnail_320x215

📅 Scan Dates:
   Oldest: 2021-06-03
   Newest: 2023-08-15
   Unique Dates: 3

🖼️  Image Types:
   • default
   • secondary
   • floor_plans

======================================================================

📁 Full report: data/property_reports/13683380_property_images.json
```

## Image Sizes

The API provides images in multiple sizes:

| Size | Dimensions | Description |
|------|------------|-------------|
| **Original** | 0x0 | Full resolution original image |
| **Large** | 768x512 | Large display size |
| **Medium** | 470x313 | Medium display size |
| **Thumbnail** | 320x215 | Small thumbnail |

## Image Types

1. **Default Image** - Primary property photo
2. **Secondary Images** - Additional property photos
3. **Floor Plan Images** - Floor plan diagrams

## Integration with PDF Generator

To integrate property images into the PDF report:

```python
from scripts.utils.property_images_client import PropertyImagesClient

# Initialize client
client = PropertyImagesClient.from_env()

# Generate images report
images_report = client.generate_images_report(
    property_id=13683380,
    property_address="5 Settlers Court, Vermont South VIC 3133"
)

# Access image URLs
if images_report['summary']['has_default_image']:
    default_img = images_report['default_image']
    thumbnail_url = default_img['urls']['thumbnail']['url']
    # Use thumbnail_url in PDF
```

## Error Handling

The script handles various error scenarios:

1. **401 Unauthorized** - Invalid credentials or insufficient API access
2. **404 Not Found** - Property doesn't exist or has no images
3. **Network Errors** - Connection issues with API
4. **Missing Credentials** - Environment variables not set

All errors are logged in the JSON report with full details.

## Troubleshooting

### 401 Unauthorized Error

```
error: "API error: 401"
message: "Unauthorized: Invalid API call as no apiproduct match found"
```

**Possible Causes:**
1. API credentials don't have access to Property Images endpoint
2. Using wrong base URL (sandbox vs production)
3. Images API product not enabled for your account

**Solutions:**
- Verify credentials have images API access
- Try production URL: `--base-url https://api.corelogic.asia`
- Contact CoreLogic to enable images API product

### No Images Found (404)

```
error: "Property not found or no default image"
```

**Possible Causes:**
- Property has no images in database
- Property ID is invalid

## API Documentation Reference

See [documentation/property_data_api.md](../documentation/property_data_api.md) lines 348-371 for full API specification.

## Examples

### Generate Report for Multiple Properties

```bash
#!/bin/bash
# Fetch images for multiple properties

PROPERTY_IDS=(13683380 11234567 98765432)

for id in "${PROPERTY_IDS[@]}"; do
  echo "Fetching images for property $id..."
  python3 scripts/fetch_property_images.py --property-id "$id"
done
```

### Use in Python Script

```python
from scripts.utils.property_images_client import PropertyImagesClient

# Initialize
client = PropertyImagesClient.from_env()

# Fetch and generate report
report = client.generate_images_report(
    property_id=13683380,
    property_address="5 Settlers Court, Vermont South VIC 3133"
)

# Check status
if report['metadata']['status'] == 'success':
    print(f"Found {report['summary']['total_images']} images")

    # Get default image thumbnail
    if report['default_image']:
        thumb_url = report['default_image']['urls']['thumbnail']['url']
        print(f"Thumbnail: {thumb_url}")
else:
    print(f"Error: {report['error']}")
```

---

**Author:** Property Images Report Generator
**Date:** 2025-11-10
**API:** CoreLogic Property Details - Images Endpoint
