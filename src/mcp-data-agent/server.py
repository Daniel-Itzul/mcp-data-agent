import os
import asyncio
import logging
import json
from typing import Any, List
from pydantic import Field
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import UserMessage, TextContent
from dotenv import load_dotenv

# Import the ai_tools module, clone-and-run friendly

import tools
import prompts 
import resources
import utilities

load_dotenv()

# Constants
host = os.environ.get("TD_HOST")
user = os.environ.get("TD_USER")
password = os.environ.get("TD_PASSWORD")
catalog = os.environ.get("CATALOG_PATH")


os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(),
              logging.FileHandler(os.path.join("logs", "mcp-data-agent.log"))],
)
logger = logging.getLogger("mcp-data-agent")    
logger.info("Starting MCP Data Agent")

# initialize MCP server
mcp = FastMCP("mcp-data-agent")

#global shutdown flag
shutdown_in_progress = False

# Initiate connection to Teradata
_tdconn = utilities.TDConn(host=host, user=user, password=password)

#------------------ Tool utilies  ------------------#
ResponseType = List[types.TextContent | types.ImageContent | types.EmbeddedResource]

def format_text_response(text: Any) -> ResponseType:
    """Format a text response."""
    if isinstance(text, str):
        try:
            # Try to parse as JSON if it's a string
            parsed = json.loads(text)
            return [types.TextContent(
                type="text", 
                text=json.dumps(parsed, indent=2, ensure_ascii=False)
            )]
        except json.JSONDecodeError:
            # If not JSON, return as plain text
            return [types.TextContent(type="text", text=str(text))]
    # For non-string types, convert to string
    return [types.TextContent(type="text", text=str(text))]

def format_error_response(error: str) -> ResponseType:
    """Format an error response."""
    return format_text_response(f"Error: {error}")

def execute_db_tool(tool, *args, **kwargs):
    """Execute a database tool with the given connection and arguments."""
    global _tdconn
    try:
        if not _tdconn.conn:
            logger.info("Reinitializing TDConn")
            _tdconn = tools.TDConn()  # Reinitialize connection if not connected
        return format_text_response(tool(_tdconn, *args, **kwargs))
    except Exception as e:
        logger.error(f"Error sampling object: {e}")
        return format_error_response(str(e))
    
#------------------ Tools  ------------------#

@mcp.tool(description="Executes a SQL query to read from the database.")
async def get_read_query(
    sql: str = Field(description="SQL that reads from the database", default=""),
    ) -> ResponseType:
    """Executes a SQL query to read from the database."""
    return execute_db_tool( tools.handle_get_base_readQuery, sql=sql) 

@mcp.resource("http://localhost/get_database_catalog", description="Fetches the database schema and table information.")
async def get_database_catalog() -> ResponseType:
    """Fetches the database schema and table information."""
    try:
        catalog_data = resources.get_catalog_data(catalog_path=catalog)
        if not catalog_data:
            return format_error_response("Unable to fetch catalog data.")
        return format_text_response(catalog_data)
    except Exception as e:
        logger.error(f"Error fetching database catalog: {e}")
        return format_error_response(str(e))

@mcp.prompt()
async def base_query(qry: str) -> UserMessage:
    """Create a SQL query against the database"""
    return UserMessage(role="user", content=TextContent(type="text", text=prompts.handle_base_query.format(qry=qry)))


#------------------ Main ------------------#
# Main function to start the MCP server
#     Description: Initializes the MCP server.
#         It creates a connection to the Teradata database and starts the server to listen for incoming requests.
#         The function uses asyncio to manage asynchronous operations.

async def main():
    global _tdconn
    
    logger.info("Starting MCP server on stdin/stdout")
    await mcp.run_stdio_async()    


#------------------ Shutdown ------------------#
# Shutdown function to handle cleanup and exit
#     Description: Cleans up resources and exits the server gracefully.
#         It sets a flag to indicate that shutdown is in progress.
#         If the shutdown is already in progress, it forces an immediate exit.
#         The function uses os._exit to terminate the process with a specific exit code.

async def shutdown():
    """Clean shutdown of the server."""
    global shutdown_in_progress, _tdconn
    
    logger.info("Shutting down server")
    if shutdown_in_progress:
        logger.info("Forcing immediate exit")
        os._exit(1)  # Use immediate process termination instead of sys.exit
    
    _tdconn.close()
    shutdown_in_progress = True

#------------------ Entry Point ------------------#
# Entry point for the script
#     Description: This script is designed to be run as a standalone program.
#         It loads environment variables, initializes logging, and starts the MCP server.
#         The main function is called to start the server and handle incoming requests.
#         If an error occurs during execution, it logs the error and exits with a non-zero status code.

if __name__ == "__main__":
    asyncio.run(main())