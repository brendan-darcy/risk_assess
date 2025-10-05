import os
import requests
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class CoreLogicAuth:
    """
    Handles CoreLogic API authentication and token management.
    get auth details:
    grep -E "CLIENT_ID|CLIENT_SECRET" .env | cut -d'"' -f2

    """
    
    def __init__(self, client_id: str, client_secret: str, base_url: str = "https://api-uat.corelogic.asia"):
        """
        Initialize the CoreLogic authentication handler.
        
        Args:
            client_id: CoreLogic API client ID
            client_secret: CoreLogic API client secret
            base_url: The base URL for CoreLogic API
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self._access_token: Optional[str] = None
    
    def get_access_token(self) -> str:
        """
        Get or refresh the access token.
        
        Returns:
            The access token
        """
        if self._access_token is None:
            self._access_token = self._fetch_new_token()
        
        return self._access_token
    
    def _fetch_new_token(self) -> str:
        """
        Fetch a new access token from CoreLogic API.
        
        Returns:
            The new access token
        """
        url = f"{self.base_url}/access/as/token.oauth2"
        
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(url, data=payload, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('access_token')
        else:
            raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")
    
    def refresh_token(self) -> str:
        """
        Force refresh the access token.
        
        Returns:
            The new access token
        """
        self._access_token = self._fetch_new_token()
        return self._access_token
    
    @classmethod
    def from_env(cls) -> 'CoreLogicAuth':
        """
        Create an instance using environment variables.
        
        Returns:
            CoreLogicAuth instance
        """
        client_id = os.getenv('CORELOGIC_CLIENT_ID')
        client_secret = os.getenv('CORELOGIC_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("CORELOGIC_CLIENT_ID and CORELOGIC_CLIENT_SECRET must be set in environment variables")
        
        return cls(client_id=client_id, client_secret=client_secret)
