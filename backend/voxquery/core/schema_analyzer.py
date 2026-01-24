"""Schema analysis and context enrichment for SQL generation"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from sqlalchemy import inspect, MetaData, Table as SQLTable, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


@dataclass
class Column:
    """Represents a database column"""
    name: str
    type: str
    nullable: bool = True
    description: Optional[str] = None
    sample_values: Optional[List[Any]] = None


@dataclass
class TableSchema:
    """Represents a table schema"""
    name: str
    columns: Dict[str, Column]
    description: Optional[str] = None
    row_count: Optional[int] = None
    primary_keys: List[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for LLM context"""
        return {
            "name": self.name,
            "description": self.description,
            "columns": {
                col.name: {
                    "type": col.type,
                    "nullable": col.nullable,
                    "description": col.description,
                }
                for col in self.columns.values()
            },
            "row_count": self.row_count,
            "primary_keys": self.primary_keys or [],
        }


class SchemaAnalyzer:
    """Analyzes warehouse schema for SQL generation context"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.metadata = MetaData()
        self.schema_cache: Dict[str, TableSchema] = {}
    
    def analyze_all_tables(self) -> Dict[str, TableSchema]:
        """Analyze all tables in the connected database"""
        try:
            # Reflect database schema
            self.metadata.reflect(bind=self.engine)
            
            inspector = inspect(self.engine)
            schemas = {}
            
            for table_name in inspector.get_table_names():
                schemas[table_name] = self.analyze_table(table_name)
            
            self.schema_cache = schemas
            logger.info(f"Analyzed {len(schemas)} tables")
            return schemas
        except Exception as e:
            logger.error(f"Error analyzing schema: {e}")
            return {}
    
    def analyze_table(self, table_name: str) -> TableSchema:
        """Analyze a single table"""
        try:
            inspector = inspect(self.engine)
            columns_info = inspector.get_columns(table_name)
            primary_keys = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
            
            columns = {}
            for col_info in columns_info:
                col = Column(
                    name=col_info["name"],
                    type=str(col_info["type"]),
                    nullable=col_info.get("nullable", True),
                    description=None,  # Can be enhanced with custom metadata
                )
                columns[col_info["name"]] = col
            
            # Try to get row count
            try:
                with self.engine.connect() as conn:
                    # Use proper SQL for different databases
                    result = conn.execute(text(f"SELECT COUNT(*) FROM [{table_name}]"))
                    row_count = result.scalar()
            except Exception as count_error:
                logger.debug(f"Could not get row count for {table_name}: {count_error}")
                row_count = None
            
            return TableSchema(
                name=table_name,
                columns=columns,
                row_count=row_count,
                primary_keys=primary_keys,
            )
        except Exception as e:
            logger.error(f"Error analyzing table {table_name}: {e}")
            return TableSchema(name=table_name, columns={})
    
    def get_schema_context(self) -> str:
        """Generate schema context string for LLM prompt"""
        if not self.schema_cache:
            self.analyze_all_tables()
        
        context = "# Database Schema\n\n"
        for table_name, schema in self.schema_cache.items():
            context += f"## Table: {table_name}\n"
            context += f"Rows: {schema.row_count}\n"
            context += "Columns:\n"
            for col_name, col in schema.columns.items():
                context += f"  - {col_name}: {col.type}"
                if col.description:
                    context += f" ({col.description})"
                context += "\n"
            context += "\n"
        
        return context
    
    def get_column_suggestions(self, partial: str) -> List[str]:
        """Get column name suggestions for autocomplete"""
        suggestions = []
        partial_lower = partial.lower()
        
        if not self.schema_cache:
            self.analyze_all_tables()
        
        for table in self.schema_cache.values():
            for col_name in table.columns.keys():
                if partial_lower in col_name.lower():
                    suggestions.append(f"{table.name}.{col_name}")
        
        return suggestions[:10]  # Limit to 10 suggestions
