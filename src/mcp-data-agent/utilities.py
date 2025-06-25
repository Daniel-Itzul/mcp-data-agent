from typing import Optional, Any, Dict, List
import json
from datetime import date, datetime
from decimal import Decimal
import teradatasql
import logging

logger = logging.getLogger("teradata_mcp_server")

# This class is used to connect to Teradata database using teradatasql library

class TDConn:
    conn = None
    # Constructor
    def __init__(self, host: str, user: str, password: str):
        host = host
        user = user
        password = password
        try:
            self.conn = teradatasql.connect (
                host=host,
                user=user,
                password=password
            )
            logger.info(f"Connected to database: {host}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            self.conn = None

    # Method to return the cursor
    #     If the connection is not established, it will raise an exception
    #     If the connection is established, it will return the cursor
    #     The cursor can be used to execute SQL queries
    def cursor(self):
        if self.conn is None:
            logger.error("Error cursor is None")
            raise Exception("No connection to database")
        return self.conn.cursor()

    # Destructor
    #     It will close the connection to the database
    def close(self):
        if self.conn is not None:
            try:
                self.conn.close()
                logger.info("Connection to database closed")
            except Exception as e:
                logger.error(f"Error closing connection to database: {e}")
        else:
            logger.warning("Connection to database is already closed")

def serialize_teradata_types(obj: Any) -> Any:
    """Convert Teradata-specific types to JSON serializable formats"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)

def rows_to_json(cursor_description: Any, rows: List[Any]) -> List[Dict[str, Any]]:
    """Convert database rows to JSON objects using column names as keys"""
    if not cursor_description or not rows:
        return []
    
    columns = [col[0] for col in cursor_description]
    return [
        {
            col: serialize_teradata_types(value)
            for col, value in zip(columns, row)
        }
        for row in rows
    ]

def create_response(data: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Create a standardized JSON response structure"""
    if metadata:
        response = {
            "status": "success",
            "metadata": metadata,
            "results": data
        }
    else:
        response = {
            "status": "success",
            "results": data
        }

    return json.dumps(response, default=serialize_teradata_types)