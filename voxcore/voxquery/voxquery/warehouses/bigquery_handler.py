"""Google BigQuery connection handler"""

import logging
from typing import Dict, List, Optional, Any

from google.cloud import bigquery
from google.cloud.bigquery import QueryJob

from .base import BaseConnection

logger = logging.getLogger(__name__)


class BigQueryConnection(BaseConnection):
    """Google BigQuery data warehouse connection"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project = kwargs.get("project_id", self.database)
    
    def connect(self) -> None:
        """Establish BigQuery connection"""
        try:
            self.connection = bigquery.Client(project=self.project)
            logger.info(f"Connected to BigQuery project: {self.project}")
        except Exception as e:
            logger.error(f"Failed to connect to BigQuery: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close BigQuery connection"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from BigQuery")
    
    def test_connection(self) -> bool:
        """Test BigQuery connection"""
        try:
            self.connection.get_dataset(self.schema or "information_schema")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def execute_query(
        self,
        sql: str,
        dry_run: bool = False,
    ) -> List[Dict[str, Any]]:
        """Execute query on BigQuery"""
        try:
            job_config = bigquery.QueryJobConfig(dry_run=dry_run)
            
            query_job = self.connection.query(sql, job_config=job_config)
            
            if dry_run:
                logger.info(f"Estimated bytes: {query_job.total_bytes_processed}")
                return []
            
            # Fetch results
            results = query_job.result()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_schema(self) -> Dict[str, Any]:
        """Get BigQuery schema information"""
        try:
            dataset_id = self.schema or self.database
            dataset = self.connection.get_dataset(dataset_id)
            
            tables = {}
            for table in self.connection.list_tables(dataset):
                table_obj = self.connection.get_table(table.reference)
                
                columns = {
                    field.name: {
                        "type": field.field_type,
                        "nullable": field.mode == "NULLABLE",
                    }
                    for field in table_obj.schema
                }
                
                tables[table.table_id] = {
                    "columns": columns,
                    "row_count": table_obj.num_rows,
                }
            
            return tables
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            return {}
    
    def get_cost_estimate(self, sql: str) -> Optional[float]:
        """Get BigQuery query cost estimate using dry-run"""
        try:
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = self.connection.query(sql, job_config=job_config)
            
            bytes_processed = query_job.total_bytes_processed
            # BigQuery pricing: ~$6.25 per 1TB = $6.25 / 1e12 bytes
            cost = (bytes_processed / 1e12) * 6.25
            return cost
        except Exception as e:
            logger.warning(f"Failed to get cost estimate: {e}")
            return None
