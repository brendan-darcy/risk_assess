# Import Structure Refactoring

**Date:** 2025-11-09 (Updated)
**Previous Issue:** `ModuleNotFoundError: No module named 'pipelines'`

## History

### Original Problem

Scripts in the `scripts/` directory had import errors trying to import from a separate `pipelines/` directory.

### Final Solution: Restructured to scripts/utils/

**Date:** 2025-11-09

All utility/pipeline modules have been moved from `pipelines/` → `scripts/utils/` for a cleaner, more intuitive project structure where utilities are co-located with the scripts that use them.

## Current Structure

```
risk_assess/
├── scripts/
│   ├── utils/                          # ← All utility modules here
│   │   ├── corelogic_auth.py
│   │   ├── geospatial_api_client.py
│   │   ├── property_data_processor.py
│   │   ├── pipeline_utils.py
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── gis_utils.py
│   │   ├── google_api_processor.py
│   │   ├── mesh_block_analysis_pipeline.py
│   │   ├── photo_location_processor.py
│   │   ├── photo_visualization_pipeline.py
│   │   └── spatial_visualization_pipeline.py
│   ├── get_parcel_polygon.py           # ← Scripts import from utils
│   ├── check_geospatial_layers.py
│   ├── run_places_analysis.py
│   ├── run_full_analysis.py
│   └── visualize_photo_locations.py
├── data/
└── notebooks/
```

## Import Pattern

### In Scripts (scripts/*.py)

Scripts import from the `utils` subdirectory:

```python
#!/usr/bin/env python3
import sys

# Import from utils subdirectory
from utils.property_data_processor import PropertyDataProcessor
from utils.geospatial_api_client import GeospatialAPIClient
from utils.pipeline_utils import ProgressReporter
```

**No need for sys.path manipulation!** Since utils is a subdirectory of scripts, Python finds it automatically.

### In Utils Modules (scripts/utils/*.py)

Utils modules use relative imports to import from each other:

```python
# In scripts/utils/property_data_processor.py
from .pipeline_utils import AuthenticatedPipeline, DataProcessor
from .corelogic_auth import CoreLogicAuth

# In scripts/utils/geospatial_api_client.py
from .corelogic_auth import CoreLogicAuth
```

## Running Scripts

From the project root:

```bash
# Run any script from project root
python3 scripts/get_parcel_polygon.py --address "..."
python3 scripts/check_geospatial_layers.py --address "..."
python3 scripts/run_full_analysis.py --address "..."
```

From the scripts directory:

```bash
cd scripts
python3 get_parcel_polygon.py --address "..."
python3 check_geospatial_layers.py --address "..."
```

## Testing Imports

Test that imports work correctly:

```bash
# From project root
python3 -c "import sys; sys.path.insert(0, 'scripts'); from utils.pipeline_utils import ProgressReporter; print('✅ Imports work')"

# Or run a script's help
python3 scripts/get_parcel_polygon.py --help
python3 scripts/check_geospatial_layers.py --help
```

## Benefits of New Structure

1. **Simpler imports** - No sys.path manipulation needed in scripts
2. **Better organization** - Utilities are co-located with scripts that use them
3. **Clearer hierarchy** - scripts/ is the top-level for all runnable code
4. **Easier to understand** - New developers immediately see scripts and their utils together

## Migration Summary

**What Changed:**
- Moved all files from `pipelines/` to `scripts/utils/`
- Updated all script imports from `from pipelines.xxx` to `from utils.xxx`
- Updated all utils internal imports to use relative imports (`from .xxx`)
- Removed sys.path manipulation from scripts

**Scripts Updated:**
- ✅ scripts/get_parcel_polygon.py
- ✅ scripts/check_geospatial_layers.py
- ✅ scripts/run_places_analysis.py
- ✅ scripts/run_full_analysis.py
- ✅ scripts/visualize_photo_locations.py

**Utils Modules Updated:**
- ✅ All relative imports fixed in utils modules
- ✅ Dynamic imports (try/except blocks) updated

## Best Practices Going Forward

### For New Scripts

Place new scripts in `scripts/` directory and import from utils:

```python
#!/usr/bin/env python3
"""My new script"""

# Import from utils subdirectory
from utils.pipeline_utils import ProgressReporter
from utils.property_data_processor import PropertyDataProcessor

def main():
    # Your code here
    pass

if __name__ == "__main__":
    main()
```

### For New Utils Modules

Place new utilities in `scripts/utils/` and use relative imports:

```python
"""My new utility module"""

# Import from other utils using relative imports
from .pipeline_utils import DataProcessor
from .config import config

class MyNewUtil(DataProcessor):
    def __init__(self):
        super().__init__()
```

### Alternative: Module Execution

You can also run scripts as modules (though not required):

```bash
# From project root
python3 -m scripts.get_parcel_polygon --address "..."
```

## Related Files

- [scripts/utils/pipeline_utils.py](scripts/utils/pipeline_utils.py) - Core pipeline utilities
- [scripts/utils/config.py](scripts/utils/config.py) - Configuration module
- [scripts/utils/exceptions.py](scripts/utils/exceptions.py) - Exception hierarchy
- [scripts/utils/gis_utils.py](scripts/utils/gis_utils.py) - GIS utilities

## See Also

- [LAYER_CHECK_IMPROVEMENTS.md](LAYER_CHECK_IMPROVEMENTS.md) - Geospatial layer checking improvements
- [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) - Phase 1 refactoring summary
- [README.md](README.md) - Project README
