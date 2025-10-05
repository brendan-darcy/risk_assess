import requests
from typing import Optional, Dict, Any, List
from corelogic_auth import CoreLogicAuth


class GeospatialAPIClient(CoreLogicAuth):
    """Geospatial API client for CoreLogic geospatial services."""
    
    def __init__(self, client_id: str, client_secret: str, base_url: str = "https://api-uat.corelogic.asia"):
        """
        Initialize the Geospatial API client.
        
        Args:
            client_id: CoreLogic API client ID
            client_secret: CoreLogic API client secret
            base_url: The base URL for CoreLogic API
        """
        super().__init__(client_id, client_secret, base_url)
        self.geo_base_url = f"{self.base_url}/geospatial/au"
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> requests.Response:
        """
        Make authenticated request to geospatial API.
        
        Args:
            endpoint: API endpoint path
            params: Request parameters
            
        Returns:
            Response object
        """
        url = f"{self.geo_base_url}/{endpoint}"
        params['access_token'] = self.get_access_token()
        
        response = requests.get(url, params=params)
        return response
    
    def export_map(self, layer: str, bbox: str, format: str = "png32", 
                   size: str = "1200,1200", transparent: bool = True, 
                   layer_defs: Optional[str] = None) -> requests.Response:
        """
        Export map image from geospatial layer.
        
        Args:
            layer: Layer name (e.g., 'propertyOverlay/propertyAll')
            bbox: Bounding box coordinates as 'xmin,ymin,xmax,ymax'
            format: Image format (png32, png, jpg, etc.)
            size: Image size as 'width,height'
            transparent: Whether to use transparent background
            layer_defs: Layer definition filters
            
        Returns:
            Response containing map image
        """
        params = {
            'bbox': bbox,
            'format': format,
            'f': 'image',
            'size': size,
            'transparent': str(transparent).lower(),
            'dpi': '150'
        }
        
        if layer_defs:
            params['layerDefs'] = layer_defs
            
        endpoint = f"overlays/{layer}"
        return self._make_request(endpoint, params)
    
    def query(self, layer: str, where: str = "1=1", geometry: Optional[str] = None,
              geometry_type: str = "esriGeometryEnvelope", out_fields: str = "*",
              return_geometry: bool = True, format: str = "json") -> requests.Response:
        """
        Query geospatial layer for feature data.
        
        Args:
            layer: Layer name for querying
            where: WHERE clause for filtering
            geometry: Geometry for spatial filtering
            geometry_type: Type of geometry filter
            out_fields: Fields to return (* for all)
            return_geometry: Whether to include geometry in results
            format: Response format (json, html)
            
        Returns:
            Response containing query results
        """
        params = {
            'where': where,
            'outFields': out_fields,
            'returnGeometry': str(return_geometry).lower(),
            'f': format
        }
        
        if geometry:
            params['geometry'] = geometry
            params['geometryType'] = geometry_type
            
        endpoint = f"geometry/{layer}"
        return self._make_request(endpoint, params)
    
    def get_layer_info(self, layer: str) -> requests.Response:
        """
        Get layer configuration and metadata.
        
        Args:
            layer: Layer name
            
        Returns:
            Response containing layer information
        """
        params = {'f': 'json'}
        endpoint = f"info/{layer}"
        return self._make_request(endpoint, params)
    
    def get_property_boundaries(self, bbox: str, property_id: Optional[str] = None) -> requests.Response:
        """
        Get property boundaries for specified area or property.
        
        Args:
            bbox: Bounding box coordinates
            property_id: Specific property ID to filter (optional)
            
        Returns:
            Response containing property boundary data
        """
        layer = "propertyOverlay/propertyAll"
        layer_defs = None
        
        if property_id:
            layer = "propertyOverlay/propertySelect"
            layer_defs = f"0:property_id={property_id}"
            
        return self.export_map(layer, bbox, layer_defs=layer_defs)
    
    def get_property_data(self, property_id: str) -> requests.Response:
        """
        Query property data by property ID.
        
        Args:
            property_id: Property identifier
            
        Returns:
            Response containing property details
        """
        where_clause = f"property_id={property_id}"
        return self.query("propertyOverlay/propertyAll", where=where_clause)
    
    def get_hazard_data(self, bbox: str, hazard_type: str = "bushfire") -> requests.Response:
        """
        Get hazard overlay data (bushfire, flood, heritage).
        
        Args:
            bbox: Bounding box coordinates
            hazard_type: Type of hazard (bushfire, flood, heritage)
            
        Returns:
            Response containing hazard data
        """
        return self.export_map(hazard_type, bbox)
    
    def get_easement_data(self, bbox: str, state: str = "nsw") -> requests.Response:
        """
        Query easement data within a bounding box.
        
        Note: Easement data doesn't support property_id filtering, 
        so we query by spatial intersection instead.
        
        Args:
            bbox: Bounding box coordinates as 'xmin,ymin,xmax,ymax' 
            state: State code (nsw, vic, qld, etc.)
            
        Returns:
            Response containing easement data within the bbox
        """
        # Use spatial geometry filter instead of property_id
        params = {
            'where': '1=1',  # Get all records
            'geometry': bbox,
            'geometryType': 'esriGeometryEnvelope',
            'spatialRel': 'esriSpatialRelIntersects',
            'f': 'json',
            'outFields': '*',
            'returnGeometry': 'true'
        }
        
        endpoint = f"{state}/geometry/easements"
        return self._make_request(endpoint, params)
    
    def get_infrastructure_data(self, bbox: str, infrastructure_type: str, state: str = "nsw") -> requests.Response:
        """
        Get infrastructure overlay data.
        
        Args:
            bbox: Bounding box coordinates
            infrastructure_type: Type of infrastructure (electricTransmissionLines, railway, etc.)
            state: State code (nsw, vic, qld, etc.)
            
        Returns:
            Response containing infrastructure data
        """
        if infrastructure_type in ['streets', 'railway', 'railwayStations', 'ferry']:
            # These are national overlays
            return self.export_map(f"overlays/{infrastructure_type}", bbox)
        else:
            # State-specific infrastructure (like transmission lines)
            return self.export_map(f"overlays/{infrastructure_type}", bbox)
    
    def query_infrastructure_features(self, property_id: str, infrastructure_type: str, state: str = "nsw") -> requests.Response:
        """
        Query infrastructure features near a property.
        
        Args:
            property_id: Property identifier
            infrastructure_type: Type of infrastructure (electricTransmissionLines, etc.)
            state: State code (nsw, vic, qld, etc.)
            
        Returns:
            Response containing infrastructure feature data
        """
        where_clause = f"property_id={property_id}"
        return self.query(f"{state}/planningAggregations/{infrastructure_type}", where_clause)
    
    def get_parcel_polygon(self, property_id: str) -> Dict[str, Any]:
        """
        Get parcel polygon geometry for a property.

        Args:
            property_id: Property identifier

        Returns:
            Dictionary with parcel geometry and attributes

        Raises:
            ValueError: If no parcel found for property_id
            requests.HTTPError: If API request fails
        """
        layer = "propertyOverlay/propertyAll"
        where_clause = f"property_id={property_id}"

        response = self.query(
            layer=layer,
            where=where_clause,
            out_fields="*",
            return_geometry=True,
            format="json"
        )

        response.raise_for_status()
        data = response.json()

        if 'features' not in data or len(data['features']) == 0:
            raise ValueError(f"No parcel found for property_id: {property_id}")

        return data

    def format_parcel_result(self, property_id: str, address: str, parcel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format parcel polygon result with property information.

        Args:
            property_id: Property identifier
            address: Property address
            parcel_data: Raw parcel query response

        Returns:
            Formatted dictionary with property and geometry information
        """
        features = parcel_data.get('features', [])

        if not features:
            return {
                'property_id': property_id,
                'address': address,
                'error': 'No parcel geometry found'
            }

        feature = features[0]
        attributes = feature.get('attributes', {})
        geometry = feature.get('geometry', {})

        return {
            'property_id': property_id,
            'address': address,
            'parcel_attributes': attributes,
            'geometry': geometry,
            'geometry_type': parcel_data.get('geometryType'),
            'spatial_reference': parcel_data.get('spatialReference')
        }

    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection and authentication.

        Returns:
            Dictionary with connection test results
        """
        try:
            token = self.get_access_token()

            # Test with simple layer info request
            response = self.get_layer_info("propertyOverlay/propertyAll")

            return {
                'success': True,
                'status_code': response.status_code,
                'token_present': bool(token),
                'token_length': len(token) if token else 0,
                'response_size': len(response.content)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'token_present': bool(self._access_token),
            }