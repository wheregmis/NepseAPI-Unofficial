
# NEPSE MCP Server Usage Examples (FastMCP Version)

This document provides examples of how to use the NEPSE MCP server (using FastMCP, not the official MCP Python library) with AI models.

## Setup Instructions


### 1. Claude Desktop Integration

Add this configuration to your Claude Desktop settings (use `mcp_server copy.py` for FastMCP):

**Location**:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Configuration**:
```json
{
  "mcpServers": {
    "nepse-stock-data": {
      "command": "python",
      "args": ["mcp_server copy.py"],
      "cwd": "C:\\Users\\Admin\\Desktop\\Work\\NepseAPI",
      "env": {
        "NEPSE_API_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

### 2. Starting the Services

**Option 1: Use the startup script (Windows)**
```powershell
.\start_servers.ps1
```

**Option 2: Start manually**
```bash
# Terminal 1: Start FastAPI server
python server.py

# Terminal 2: MCP server will be auto-started by Claude
# No manual start needed for MCP server
```


## Available MCP Tools

The MCP server provides 17+ tools for accessing Nepal stock market data. Prompts and tools are defined using FastMCP decorators (`@mcp.prompt`, `@mcp.tool`).

### Market Overview Tools
- `get_market_summary` - Current market summary with key metrics
- `get_live_market` - Real-time market data
- `check_market_status` - Check if NEPSE is open
- `get_nepse_index` - Main NEPSE index information
- `get_sector_indices` - Sub-indices for all sectors

### Company-Specific Tools
- `get_company_details` - Detailed company information (requires symbol)
- `get_company_list` - List of all listed companies
- `get_price_volume` - Price and volume data for all stocks
- `get_price_history` - Historical data for a company (requires symbol)

### Trading Data Tools
- `get_top_gainers` - Best performing stocks
- `get_top_losers` - Worst performing stocks
- `get_top_turnover` - Highest turnover companies
- `get_floorsheet` - All today's transactions
- `get_company_floorsheet` - Company-specific transactions (requires symbol)

### Advanced Tools
- `get_market_depth` - Bid/ask data for a stock (requires symbol)
- `get_supply_demand` - Market supply and demand data
- `get_comprehensive_market_data` - Complete market analysis with sectors


## Prompt Structure (FastMCP)

Prompts are defined using the `@mcp.prompt` decorator. Example:

```python
@mcp.prompt(
    name="stock-quick-lookup",
    description="Get a quick summary of a stock's current price, volume, and latest trades."
)
def stock_quick_lookup(symbol: str) -> PromptMessage:
    return PromptMessage(role="user", content=TextContent(type="text", text=f"Show me a quick summary for {symbol}."))
```

See `mcp_server copy.py` for all available prompt definitions.

## Rate Limiting (FastMCP)

Rate limiting is enforced using FastMCP's built-in middleware. Default: 80 requests/minute (see `mcp_server copy.py`).
If you exceed the limit, you will receive an error like:

```
Rate limit exceeded for MCP tool 'get_market_summary'.
Limit: 80 requests per minute. Try again in 25 seconds.
```

You can adjust the rate limit in the code by changing the `RateLimitingMiddleware` settings.

## Example AI Interactions

### Market Analysis Query
**User**: "What's the current state of the Nepal stock market?"

**AI Response** (using MCP tools):
- Calls `get_market_summary` for overview
- Calls `check_market_status` to see if market is open
- Calls `get_nepse_index` for index information
- Provides comprehensive market analysis

### Company Research Query
**User**: "Tell me about NABIL bank's performance"

**AI Response** (using MCP tools):
- Calls `get_company_details` with symbol="NABIL"
- Calls `get_price_history` for historical data
- Calls `get_company_floorsheet` for recent transactions
- Provides detailed company analysis

### Investment Strategy Query
**User**: "Which stocks are performing well today?"

**AI Response** (using MCP tools):
- Calls `get_top_gainers` for best performers
- Calls `get_top_turnover` for most active stocks
- Calls `get_live_market` for current prices
- Provides investment insights

## Testing Your Setup

1. **Test FastAPI server**:
   ```
   curl http://localhost:8000/health
   ```

2. **Test MCP server**:
   ```
   python test_mcp.py
   ```

3. **Test in Claude Desktop**:
   - Restart Claude Desktop after adding configuration
   - Ask: "What tools do you have available?"
   - You should see the NEPSE tools listed

## Troubleshooting

### Common Issues

1. **"FastAPI server not running"**
   - Make sure to start `python server.py` first
   - Check if port 8000 is available

2. **"MCP server not found in Claude"**
   - Verify the config file path is correct
   - Restart Claude Desktop completely
   - Check Python path in the configuration

3. **"Module not found errors"**
   - Run `pip install -r requirements.txt`
   - Ensure you're in the correct directory

### Verification Steps

```bash
# 1. Check Python environment
python --version

# 2. Check dependencies
python -c "import fastapi, mcp, httpx; print('All dependencies OK')"

# 3. Test FastAPI
curl http://localhost:8000/docs

# 4. Test MCP functionality
python test_mcp.py
```

## Advanced Usage

### Custom MCP Client
You can also create your own MCP client to interact with the server:

```python
import asyncio
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client(["python", "mcp_server.py"]) as (read, write):
        # Your MCP client code here
        pass

asyncio.run(main())
```

### Environment Variables
You can customize the behavior using environment variables:

```bash
export NEPSE_API_BASE_URL="http://localhost:8000"
python mcp_server.py
```

## Support

For issues or questions:
1. Check the test script output: `python test_mcp.py`
2. Verify FastAPI server logs
3. Check Claude Desktop logs (if using Claude)

The MCP server provides a powerful interface for AI models to access real-time Nepal stock market data, enabling sophisticated financial analysis and investment research capabilities.
