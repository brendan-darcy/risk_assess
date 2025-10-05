# Risk Assessment System

Australian property risk assessment system using CoreLogic APIs for property data, geospatial services, and market analysis.

## Quick Start

1. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your CoreLogic credentials
```

2. **Install dependencies:**
```bash
pip install requests pandas python-dotenv
```

3. **Run example script:**
```bash
python scripts/get_parcel_polygon.py --address "123 Main St, Sydney NSW" --pretty
```

## Project Structure

```
risk_assess/
├── pipelines/         # Reusable pipeline classes and utilities
├── scripts/           # Executable CLI scripts
├── documentation/     # API documentation and development guides
├── notebooks/         # Jupyter notebooks for exploration and analysis
├── data/
│   ├── raw/          # Input data (shapefiles, addresses, property lists)
│   └── outputs/      # Generated results (CSV, JSON, images)
└── README.md         # This file
```

## Documentation

- **[CLAUDE.md](documentation/CLAUDE.md)** - Comprehensive development guide for Claude Code
- **[geospatial_api.md](documentation/geospatial_api.md)** - Complete geospatial API reference
- **[claude_template.md](documentation/claude_template.md)** - Python API integration specialist template

## Key Features

- **Property Data Processing**: Address resolution, property details, sales history
- **Geospatial Analysis**: Property boundaries, hazard overlays, infrastructure mapping
- **Rental Analysis**: Locality rental listings with AVM indexation
- **Market Data**: Time series analysis, property value indexation
- **Pipeline Architecture**: Reusable classes with comprehensive error handling

## Environment Variables

Required in `.env` file:
```
CORELOGIC_CLIENT_ID=your_client_id
CORELOGIC_CLIENT_SECRET=your_client_secret
```

## Development

See [documentation/CLAUDE.md](documentation/CLAUDE.md) for detailed development guide including:
- Architecture overview
- Creating new scripts
- API integration patterns
- Testing and debugging

## License

Internal use - Apprise Risk Solutions Pty Ltd
