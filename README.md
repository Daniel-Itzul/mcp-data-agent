# MCP Data Agent

This repository contains the **MCP Data Agent**, a Python-based service for exposing database operations and metadata as tools and resources in an MCP server.

## Features

- Exposes database read/query operations as MCP tools
- Provides a resource endpoint for fetching database catalog/schema information
- Asynchronous server using FastMCP and asyncio
- Environment-based configuration for database and catalog paths

## Project Structure

```
mcp-data-agent/
├── src/
│   └── mcp-data-agent/
│       ├── server.py
│       ├── resources.py
│       ├── tools.py
│       └── prompts.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- [UV](https://github.com/astral-sh/uv) for dependency management

### Installation

1. Clone the repository:
    ```sh
    git clone <repo-url>
    cd mcp-data-agent
    ```

2. Create and activate a virtual environment:
    ```sh
    uv venv
    ```

3. Install dependencies using UV:
    ```sh
    uv pip install -r pyproject.toml
    ```


### Running the Agent

```sh
uv run src/mcp-data-agent/server.py
```


## Usage

- The agent exposes tools and resources for use by MCP agents.
- Configure your database and catalog paths in the `.env` file.

## Development

- Source code is in `src/mcp-data-agent/`.
- Add new tools or resources by decorating functions with `@mcp.tool` or `@mcp.resource`.

## License

MIT License

---

**Note:** This project is intended for use within the MCP ecosystem and may require MCP-specific infrastructure or