"""
Database configuration and connection management for ZXY Business Intelligence Dashboard
"""

import os
import pyodbc
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        # Database connection parameters
        self.server = "52.220.68.78"
        self.port = "1433"
        self.database = "zinfotrek"
        self.username = "zxydbowner"
        self.password = "8CY@SsHg%T!"
        
        # Connection string for pyodbc
        self.connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={self.server};'
            f'Port={self.port};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'TrustServerCertificate=yes;'
        )
        
        # SQLAlchemy connection string
        self.sqlalchemy_url = (
            f'mssql+pyodbc://{self.username}:{self.password}@'
            f'{self.server}:{self.port}/{self.database}?'
            f'driver=ODBC+Driver+17+for+SQL+Server&'
            f'TrustServerCertificate=yes'
        )
        
        # Initialize SQLAlchemy engine
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with connection pooling"""
        try:
            self.engine = create_engine(
                self.sqlalchemy_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False  # Set to True for SQL debugging
            )
            logger.info("Database engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = self.engine.connect()
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                if test_value == 1:
                    logger.info("Database connection test successful")
                    return True
                else:
                    logger.error("Database connection test failed")
                    return False
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame"""
        try:
            with self.get_connection() as conn:
                if params:
                    result = pd.read_sql(text(query), conn, params=params)
                else:
                    result = pd.read_sql(text(query), conn)
                logger.info(f"Query executed successfully, returned {len(result)} rows")
                return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_scalar(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute a query and return a single scalar value"""
        try:
            with self.get_connection() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                value = result.scalar()
                logger.info(f"Scalar query executed successfully")
                return value
        except Exception as e:
            logger.error(f"Scalar query execution failed: {e}")
            raise

# Global database instance
db_config = DatabaseConfig()

def get_database() -> DatabaseConfig:
    """Get the global database configuration instance"""
    return db_config

def test_database_connection() -> bool:
    """Test the database connection"""
    return db_config.test_connection()