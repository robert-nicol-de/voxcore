"""
Semantic Model Handler
Connects to semantic layers/models for AI-enhanced query generation
"""

import requests
import json
from typing import Dict, List, Any, Optional
from .base import BaseWarehouse


class SemanticHandler(BaseWarehouse):
    """Handler for semantic model connections"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize semantic model handler"""
        super().__init__(config)
        self.endpoint = config.get('endpoint', 'http://localhost:9000/api/semantic')
        self.api_key = config.get('api_key', '')
        self.api_secret = config.get('api_secret', '')
        self.model_id = config.get('model_id', 'default_model')
        self.model_type = config.get('type', 'custom_api')
        self.cache_enabled = config.get('cache_enabled', True)
        self.semantic_cache = {}
        
    def connect(self) -> bool:
        """Test connection to semantic model"""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.endpoint}/health",
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Semantic model connection failed: {e}")
            return False
    
    def get_schema(self) -> Dict[str, Any]:
        """Get semantic model schema/metadata"""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.endpoint}/models/{self.model_id}/schema",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get semantic schema: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error fetching semantic schema: {e}")
            return {}
    
    def get_entities(self) -> List[Dict[str, Any]]:
        """Get semantic entities (tables/dimensions)"""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.endpoint}/models/{self.model_id}/entities",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('entities', [])
            return []
        except Exception as e:
            print(f"Error fetching entities: {e}")
            return []
    
    def get_relationships(self) -> List[Dict[str, Any]]:
        """Get semantic relationships between entities"""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.endpoint}/models/{self.model_id}/relationships",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('relationships', [])
            return []
        except Exception as e:
            print(f"Error fetching relationships: {e}")
            return []
    
    def get_measures(self) -> List[Dict[str, Any]]:
        """Get semantic measures (calculated fields)"""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.endpoint}/models/{self.model_id}/measures",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('measures', [])
            return []
        except Exception as e:
            print(f"Error fetching measures: {e}")
            return []
    
    def resolve_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Resolve entity name to semantic definition"""
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.endpoint}/models/{self.model_id}/resolve-entity",
                headers=headers,
                json={"entity_name": entity_name},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error resolving entity: {e}")
            return None
    
    def infer_relationships(self, entities: List[str]) -> List[Dict[str, Any]]:
        """Infer relationships between entities"""
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.endpoint}/models/{self.model_id}/infer-relationships",
                headers=headers,
                json={"entities": entities},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('relationships', [])
            return []
        except Exception as e:
            print(f"Error inferring relationships: {e}")
            return []
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute query through semantic model"""
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.endpoint}/models/{self.model_id}/query",
                headers=headers,
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                print(f"Query execution failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    
    def get_semantic_context(self) -> Dict[str, Any]:
        """Get complete semantic context for LLM"""
        context = {
            'model_id': self.model_id,
            'model_type': self.model_type,
            'entities': self.get_entities(),
            'relationships': self.get_relationships(),
            'measures': self.get_measures(),
            'schema': self.get_schema()
        }
        return context
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        if self.api_secret:
            headers['X-API-Secret'] = self.api_secret
            
        return headers
    
    def disconnect(self) -> bool:
        """Disconnect from semantic model"""
        self.semantic_cache.clear()
        return True
