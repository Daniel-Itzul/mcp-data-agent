import logging
from teradatasql import TeradataConnection
from utilities import create_response, rows_to_json

logger = logging.getLogger("mcp-data-agent")

#------------------ Tool  ------------------#
# Read SQL execution tool
#     Arguments: 
#       conn (TeradataConnection) - Teradata connection object for executing SQL queries         
#       sql (str) - SQL query to execute
#     Returns: ResponseType - formatted response with query results or error message

def handle_get_base_readQuery(conn: TeradataConnection, sql: str, *args, **kwargs):
    logger.debug(f"Tool: handle_get_base_readQuery: Args: sql: {sql}")

    with conn.cursor() as cur:    
        rows = cur.execute(sql)  # type: ignore
        if rows is None:
            return create_response([])
            
        data = rows_to_json(cur.description, rows.fetchall())
        metadata = {
            "tool_name": "get_base_readQuery",
            "sql": sql,
            "columns": [
                {"name": col[0], "type": col[1].__name__ if hasattr(col[1], '__name__') else str(col[1])}
                for col in cur.description
            ] if cur.description else [],
            "row_count": len(data)
        }
        return create_response(data, metadata)