"""Base warehouse connection class"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class BaseConnection(ABC):
    """Abstract base class for warehouse connections"""
    
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: Optional[int] = None,
        schema: Optional[str] = None,
        **kwargs
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.schema = schema
        self.extra_params = kwargs
        self.connection = None
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to warehouse"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to warehouse"""
        pass
    
    @abstractmethod
    def execute_query(self, sql: str, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if connection is valid"""
        pass
    
    @abstractmethod
    def get_cost_estimate(self, sql: str) -> Optional[float]:
        """Get estimated cost of query (if supported)"""
        pass
