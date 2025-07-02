import logging
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.prompts.prompt import PromptMessage, TextContent
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from fastmcp.server.middleware.rate_limiting import (
    RateLimitingMiddleware,
)
from fastmcp.server.middleware.error_handling import (
    ErrorHandlingMiddleware,
    RetryMiddleware
)

load_dotenv()

# Import validation utilities
from validator import validate_stock_symbol, validator

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.environ.get("PORT", 9000))


mcp = FastMCP("nepseapi-mcp-server")

# --- Rate Limiting Middleware ---
mcp.add_middleware(RateLimitingMiddleware(
    max_requests_per_second=6/60,  # 6 per minute
    burst_capacity=6
))

mcp.add_middleware(ErrorHandlingMiddleware(
    include_traceback=True,
    transform_errors=True,
    error_callback=lambda request, exc: logger.error(f"Error in MCP server: {exc}"),
))

mcp.add_middleware(RetryMiddleware(
    max_retries=3,
    retry_exceptions=(ConnectionError, TimeoutError)
))

@mcp.prompt(
    name="stock-quick-lookup",
    description="Get a quick summary of a stock's current price, volume, and latest trades."
)
def stock_quick_lookup(symbol: str) -> PromptMessage:
    """Get a quick summary of a stock's current price, volume, and latest trades."""
    return PromptMessage(role="user", content=TextContent(type="text", text=f"Show me a quick summary for {symbol}."))

@mcp.prompt(
    name="market-sentiment-snapshot",
    description="Get a snapshot of today's top gainers, losers, and overall market mood."
)
def market_sentiment_snapshot() -> PromptMessage:
    """Get a snapshot of today's top gainers, losers, and overall market mood."""
    return PromptMessage(role="user", content=TextContent(type="text", text="Give me today's top gainers, losers, and a market summary."))

@mcp.prompt(
    name="sector-performance",
    description="Analyze the performance of a specific sector today."
)
def sector_performance(sector: str) -> PromptMessage:
    """Analyze the performance of a specific sector today."""
    return PromptMessage(role="user", content=TextContent(type="text", text=f"Analyze today's performance for the {sector} sector."))

@mcp.prompt(
    name="company-deep-dive",
    description="Get a detailed report on a company: profile, price history, and recent trades."
)
def company_deep_dive(symbol: str) -> PromptMessage:
    """Get a detailed report on a company: profile, price history, and recent trades."""
    return PromptMessage(role="user", content=TextContent(type="text", text=f"Give me a detailed report for {symbol}, including profile, price history, and recent trades."))

@mcp.prompt(
    name="live-market-watchlist",
    description="Monitor live prices and volumes for a custom list of stocks."
)
def live_market_watchlist(symbols: str) -> PromptMessage:
    """Monitor live prices and volumes for a custom list of stocks."""
    return PromptMessage(role="user", content=TextContent(type="text", text=f"Show me live prices and volumes for: {symbols}"))

@mcp.prompt(
    name="market-depth-analyzer",
    description="Analyze the current bid/ask depth for a stock (only when market is open)."
)
def market_depth_analyzer(symbol: str) -> PromptMessage:
    """Analyze the current bid/ask depth for a stock (only when market is open)."""
    return PromptMessage(role="user", content=TextContent(type="text", text=f"Analyze the current market depth for {symbol}."))

@mcp.prompt(
    name="post-market-trade-explorer",
    description="Explore all trades for a stock after market close (floorsheet)."
)
def post_market_trade_explorer(symbol: str) -> PromptMessage:
    """Explore all trades for a stock after market close (floorsheet)."""
    return PromptMessage(role="user", content=TextContent(type="text", text=f"Show me all trades for {symbol} after market close."))

@mcp.prompt(
    name="validate-stock-symbol",
    description="Check if a stock symbol is valid and get suggestions if not."
)
def validate_stock_symbol_prompt(symbol: str) -> PromptMessage:
    """Check if a stock symbol is valid and get suggestions if not."""
    return PromptMessage(role="user", content=TextContent(type="text", text=f"Validate the stock symbol: {symbol}"))

@mcp.prompt(
    name="market-open-status",
    description="Check if the NEPSE market is currently open or closed."
)
def market_open_status() -> PromptMessage:
    """Check if the NEPSE market is currently open or closed."""
    return PromptMessage(role="user", content=TextContent(type="text", text="Is the NEPSE market currently open or closed?"))

@mcp.prompt(
    name="setup-alert",
    description="Set up a price or volume alert for a stock (UI clients can use this to trigger notifications)."
)
def setup_alert(symbol: str, type: str, threshold: str) -> PromptMessage:
    """Set up a price or volume alert for a stock (UI clients can use this to trigger notifications)."""
    return PromptMessage(role="user", content=TextContent(type="text", text=f"Set up an alert for {symbol} when {type} crosses {threshold}."))

# Pydantic Models for Type Validation
class Summary(BaseModel):
    totalTurnoverRs: float = Field(..., alias="Total Turnover Rs:")
    totalTradedShares: float = Field(..., alias="Total Traded Shares")
    totalTransactions: float = Field(..., alias="Total Transactions")
    totalScripsTraded: float = Field(..., alias="Total Scrips Traded")

class PriceVolumeItem(BaseModel):
    securityId: str
    securityName: str
    symbol: str
    indexId: int
    totalTradeQuantity: int
    lastTradedPrice: float
    percentageChange: float
    previousClose: float
    closePrice: Optional[float] = None

class SupplyDemand(BaseModel):
    symbol: str
    totalOrder: int
    totalQuantity: int
    quantityPerOrder: Optional[float] = None
    orderSide: Optional[str] = None
    securityId: Optional[str] = None

class SupplyDemandData(BaseModel):
    supplyList: List[SupplyDemand]
    demandList: List[SupplyDemand]

class TopGainerLoser(BaseModel):
    symbol: str
    ltp: float
    pointChange: float
    percentageChange: float
    securityName: str
    securityId: int

class TopTradeScrip(BaseModel):
    symbol: str
    shareTraded: int
    closingPrice: float
    securityName: str
    securityId: int

class TopTurnover(BaseModel):
    symbol: str
    turnover: float
    closingPrice: float
    securityName: str
    securityId: int

class TopTransaction(BaseModel):
    securityId: int
    totalTrades: int
    lastTradedPrice: float
    securityName: str
    symbol: str

class MarketStatus(BaseModel):
    isOpen: str
    asOf: str
    id: int

class CompanyInfo(BaseModel):
    id: int
    companyName: str
    symbol: str
    securityName: str
    status: str
    companyEmail: str
    website: str
    sectorName: str
    regulatoryBody: str
    instrumentType: str

class LiveMarketItem(BaseModel):
    securityId: str
    securityName: str
    symbol: str
    indexId: int
    openPrice: float
    highPrice: float
    lowPrice: float
    totalTradeQuantity: int
    totalTradeValue: float
    lastTradedPrice: float
    percentageChange: float
    lastUpdatedDateTime: str
    lastTradedVolume: int
    previousClose: float
    averageTradedPrice: float
    totalTradedVolume: int
    numberOfTrades: int

# Additional Pydantic Models for remaining tools
class MarketIndex(BaseModel):
    id: int
    auditId: Optional[int] = None
    exchangeIndexId: Optional[int] = None
    generatedTime: str
    index: str
    close: float
    high: float
    low: float
    previousClose: float
    change: float
    perChange: float
    fiftyTwoWeekHigh: float
    fiftyTwoWeekLow: float
    currentValue: float

class SubIndex(BaseModel):
    id: int
    index: str
    change: float
    perChange: float
    currentValue: float

class TradeContract(BaseModel):
    contractId: int
    stockSymbol: str
    buyerMemberId: str
    sellerMemberId: str
    contractQuantity: int
    contractRate: float
    contractAmount: float
    businessDate: str
    tradeBookId: int
    stockId: int
    buyerBrokerName: str
    sellerBrokerName: str
    tradeTime: str
    securityName: str

class HistoricalTradeEntry(BaseModel):
    businessDate: str
    totalTrades: int
    totalTradedQuantity: int
    totalTradedValue: float
    highPrice: float
    lowPrice: float
    closePrice: float

class MarketDepthItem(BaseModel):
    stockId: int
    orderBookOrderPrice: float
    quantity: int
    orderCount: int
    isBuy: int  # 1 or 2
    buy: bool
    sell: bool

class MarketDepthData(BaseModel):
    buyMarketDepthList: List[MarketDepthItem]
    sellMarketDepthList: List[MarketDepthItem]

class MarketDepthResponse(BaseModel):
    symbol: str
    totalBuyQty: int
    marketDepth: MarketDepthData
    totalSellQty: int
    timeStamp: Optional[int] = None

class SecurityDailyTradeDto(BaseModel):
    securityId: str
    openPrice: float
    highPrice: float
    lowPrice: float
    totalTradeQuantity: int
    totalTrades: int
    lastTradedPrice: float
    previousClose: float
    businessDate: str
    closePrice: float
    fiftyTwoWeekHigh: float
    fiftyTwoWeekLow: float
    lastUpdatedDateTime: str

class InstrumentType(BaseModel):
    id: int
    code: str
    description: str
    activeStatus: str

class ShareGroup(BaseModel):
    id: int
    name: str
    description: str
    capitalRangeMin: int
    modifiedBy: Optional[str] = None
    modifiedDate: Optional[str] = None
    activeStatus: str
    isDefault: str

class SectorMaster(BaseModel):
    id: int
    sectorDescription: str
    activeStatus: str
    regulatoryBody: str

class CompanyId(BaseModel):
    id: int
    companyShortName: str
    companyName: str
    email: str
    companyWebsite: str
    companyContactPerson: str
    sectorMaster: SectorMaster
    companyRegistrationNumber: str
    activeStatus: str

class Security(BaseModel):
    id: int
    symbol: str
    isin: str
    permittedToTrade: str
    listingDate: str
    creditRating: Optional[str] = None
    tickSize: float
    instrumentType: InstrumentType
    capitalGainBaseDate: str
    faceValue: float
    highRangeDPR: float
    issuerName: Optional[str] = None
    meInstanceNumber: int
    parentId: Optional[int] = None
    recordType: int
    schemeDescription: Optional[str] = None
    schemeName: Optional[str] = None
    secured: Optional[str] = None
    series: Optional[str] = None
    shareGroupId: ShareGroup
    activeStatus: str
    divisor: int
    cdsStockRefId: int
    securityName: str
    tradingStartDate: str
    networthBasePrice: float
    securityTradeCycle: int
    isPromoter: str
    companyId: CompanyId

class SecurityOverview(BaseModel):
    securityDailyTradeDto: SecurityDailyTradeDto
    security: Security
    stockListedShares: float
    paidUpCapital: float
    issuedCapital: float
    marketCapitalization: float
    publicShares: int
    publicPercentage: float
    promoterShares: float
    promoterPercentage: float
    updatedDate: str
    securityId: int

class TurnoverIndex(BaseModel):
    id: int
    index: str
    change: float
    perChange: float
    currentValue: float

class ScripDetail(BaseModel):
    symbol: str
    sector: str
    Turnover: float
    transaction: int
    volume: int
    previousClose: float
    lastUpdatedDateTime: int
    name: str
    category: str
    pointChange: float
    percentageChange: float
    ltp: float

class SectorDetail(BaseModel):
    transaction: int
    volume: int
    totalTurnover: float
    turnover: TurnoverIndex
    sectorName: str

class MarketSummary(BaseModel):
    scripsDetails: Dict[str, ScripDetail]
    sectorsDetails: Dict[str, SectorDetail]

def fetch_nepse_api(endpoint: str) -> Dict[str, Any]:
    """Fetch data from the NEPSE API and return parsed JSON."""
    url = f"{BASE_URL}{endpoint}"
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    return response.json()

def validate_and_return(data: Any, model_class: BaseModel, is_list: bool = False):
    """Validate data against Pydantic model and return validated result."""
    try:
        if is_list:
            return [model_class(**item) for item in data]
        else:
            return model_class(**data)
    except ValidationError as e:
        logger.error(f"Validation error for {model_class.__name__}: {e}")
        return data  # Return raw data if validation fails

def check_market_open() -> bool:
    """Check if the NEPSE market is currently open. Returns True if open, False if closed."""
    try:
        market_status_response = fetch_nepse_api("/IsNepseOpen")
        market_status = validate_and_return(market_status_response, MarketStatus)

        # Check if market is open using both validated model and raw response
        if hasattr(market_status, 'isOpen'):
            return market_status.isOpen == 'OPEN'
        else:
            return market_status_response.get('isOpen') == 'OPEN'
    except Exception as e:
        logger.error(f"Error checking market status: {e}")
        return False  # Assume market is closed if we can't check

@mcp.tool()
def get_market_summary() -> Dict[str, float]:
    """Get the latest live NEPSE market summary including key metrics."""
    try:
        response = fetch_nepse_api("/Summary")
        validated_data = validate_and_return(response, Summary)
        return validated_data.model_dump() if hasattr(validated_data, 'model_dump') else response
    except Exception as e:
        logger.error(f"Error fetching market summary: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_live_market() -> List[Dict]:
    """Get real-time live market data for all securities."""
    try:
        # Check if market is open first
        if not check_market_open():
            return [{"error": "Market is closed. This tool only works when the market is open."}]

        response = fetch_nepse_api("/LiveMarket")
        validated_data = validate_and_return(response, LiveMarketItem, is_list=True)
        return [item.model_dump() if hasattr(item, 'model_dump') else item for item in validated_data]
    except Exception as e:
        logger.error(f"Error fetching live market: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def get_price_volume() -> List[Dict]:
    """Get price and volume data for all stocks."""
    try:
        response = fetch_nepse_api("/PriceVolume")
        validated_data = validate_and_return(response, PriceVolumeItem, is_list=True)
        return [item.model_dump() if hasattr(item, 'model_dump') else item for item in validated_data]
    except Exception as e:
        logger.error(f"Error fetching price volume: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def get_top_gainers() -> List[Dict]:
    """Get list of top gaining stocks."""
    try:
        response = fetch_nepse_api("/TopGainers")
        validated_data = validate_and_return(response, TopGainerLoser, is_list=True)
        return [item.model_dump() if hasattr(item, 'model_dump') else item for item in validated_data]
    except Exception as e:
        logger.error(f"Error fetching top gainers: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def get_top_losers() -> List[Dict]:
    """Get list of top losing stocks."""
    try:
        response = fetch_nepse_api("/TopLosers")
        validated_data = validate_and_return(response, TopGainerLoser, is_list=True)
        return [item.model_dump() if hasattr(item, 'model_dump') else item for item in validated_data]
    except Exception as e:
        logger.error(f"Error fetching top losers: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def get_nepse_index() -> Dict[str, Dict]:
    """Get NEPSE index information."""
    try:
        response = fetch_nepse_api("/NepseIndex")
        # Validate each index in the response
        validated_data = {}
        for key, value in response.items():
            validated_item = validate_and_return(value, MarketIndex)
            validated_data[key] = validated_item.model_dump() if hasattr(validated_item, 'model_dump') else validated_item
        return validated_data
    except Exception as e:
        logger.error(f"Error fetching NEPSE index: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_sector_indices() -> Dict[str, Dict]:
    """Get sub-indices for all sectors."""
    try:
        response = fetch_nepse_api("/NepseSubIndices")
        # Validate each sub-index in the response
        validated_data = {}
        for key, value in response.items():
            validated_item = validate_and_return(value, SubIndex)
            validated_data[key] = validated_item.model_dump() if hasattr(validated_item, 'model_dump') else validated_item
        return validated_data
    except Exception as e:
        logger.error(f"Error fetching sector indices: {e}")
        return {"error": str(e)}

@mcp.tool()
def check_market_status() -> Dict:
    """Check if NEPSE market is currently open."""
    try:
        response = fetch_nepse_api("/IsNepseOpen")
        validated_data = validate_and_return(response, MarketStatus)
        return validated_data.model_dump() if hasattr(validated_data, 'model_dump') else response
    except Exception as e:
        logger.error(f"Error checking market status: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_company_list() -> List[Dict]:
    """Get list of all companies listed in NEPSE."""
    try:
        response = fetch_nepse_api("/CompanyList")
        validated_data = validate_and_return(response, CompanyInfo, is_list=True)
        return [item.model_dump() if hasattr(item, 'model_dump') else item for item in validated_data]
    except Exception as e:
        logger.error(f"Error fetching company list: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def get_supply_demand() -> Dict:
    """Get supply and demand data for the market."""
    try:
        # Check if market is open first
        if not check_market_open():
            return {"error": "Market is closed. This tool only works when the market is open."}

        response = fetch_nepse_api("/SupplyDemand")
        validated_data = validate_and_return(response, SupplyDemandData)
        return validated_data.model_dump() if hasattr(validated_data, 'model_dump') else response
    except Exception as e:
        logger.error(f"Error fetching supply demand: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_top_turnover() -> List[Dict]:
    """Get top companies by turnover."""
    try:
        response = fetch_nepse_api("/TopTenTurnoverScrips")
        validated_data = validate_and_return(response, TopTurnover, is_list=True)
        return [item.model_dump() if hasattr(item, 'model_dump') else item for item in validated_data]
    except Exception as e:
        logger.error(f"Error fetching top turnover: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def get_comprehensive_market_data() -> Dict:
    """Get comprehensive market data including scrips and sectors details."""
    try:
        response = fetch_nepse_api("/TradeTurnoverTransactionSubindices")
        validated_data = validate_and_return(response, MarketSummary)
        return validated_data.model_dump() if hasattr(validated_data, 'model_dump') else response
    except Exception as e:
        logger.error(f"Error fetching comprehensive market data: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_floorsheet() -> List[Dict]:
    """Get today's floorsheet data (all transactions)."""
    try:
        # Check if market is closed - floorsheet only works when market is closed
        if check_market_open():
            return [{"error": "Market is open. This tool works when the market is closed, it does not work when the market is open."}]

        response = fetch_nepse_api("/Floorsheet")
        validated_data = validate_and_return(response, TradeContract, is_list=True)
        return [item.model_dump() if hasattr(item, 'model_dump') else item for item in validated_data]
    except Exception as e:
        logger.error(f"Error fetching floorsheet: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def get_company_details(symbol: str) -> Dict:
    """Get detailed information about a specific company."""
    try:
        # Validate symbol
        validation_result = validate_stock_symbol(symbol)
        if not validation_result["valid"]:
            return {"error": validation_result["error"]}

        validated_symbol = validation_result["symbol"]
        response = fetch_nepse_api(f"/CompanyDetails?symbol={validated_symbol}")

        validated_data = validate_and_return(response, SecurityOverview)
        return validated_data.model_dump() if hasattr(validated_data, 'model_dump') else response
    except Exception as e:
        logger.error(f"Error fetching company details for {symbol}: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_company_floorsheet(symbol: str) -> List[Dict]:
    """Get floorsheet data for a specific company."""
    try:
        # Check if market is closed - floorsheet only works when market is closed
        if check_market_open():
            return [{"error": "Market is open. This tool works when the market is closed, it does not work when the market is open."}]

        # Validate symbol
        validation_result = validate_stock_symbol(symbol)
        if not validation_result["valid"]:
            return [{"error": validation_result["error"]}]

        validated_symbol = validation_result["symbol"]
        response = fetch_nepse_api(f"/FloorsheetOf?symbol={validated_symbol}")
        validated_data = validate_and_return(response, TradeContract, is_list=True)
        return [item.model_dump() if hasattr(item, 'model_dump') else item for item in validated_data]
    except Exception as e:
        logger.error(f"Error fetching company floorsheet for {symbol}: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def get_price_history(symbol: str) -> List[Dict]:
    """Get historical price and volume data for a company."""
    try:
        # Validate symbol
        validation_result = validate_stock_symbol(symbol)
        if not validation_result["valid"]:
            return [{"error": validation_result["error"]}]

        validated_symbol = validation_result["symbol"]
        response = fetch_nepse_api(f"/PriceVolumeHistory?symbol={validated_symbol}")
        validated_data = validate_and_return(response, HistoricalTradeEntry, is_list=True)
        return [item.model_dump() if hasattr(item, 'model_dump') else item for item in validated_data]
    except Exception as e:
        logger.error(f"Error fetching price history for {symbol}: {e}")
        return [{"error": str(e)}]

@mcp.tool()
def get_market_depth(symbol: str) -> Dict:
    """Get market depth (bid/ask) for a specific stock."""
    try:
        # Check if market is open first
        if not check_market_open():
            return {"error": "Market is closed. This tool only works when the market is open."}

        # Validate symbol
        validation_result = validate_stock_symbol(symbol)
        if not validation_result["valid"]:
            return {"error": validation_result["error"]}

        validated_symbol = validation_result["symbol"]
        response = fetch_nepse_api(f"/MarketDepth?symbol={validated_symbol}")
        validated_data = validate_and_return(response, MarketDepthResponse)
        return validated_data.model_dump() if hasattr(validated_data, 'model_dump') else response
    except Exception as e:
        logger.error(f"Error fetching market depth for {symbol}: {e}")
        return {"error": str(e)}

@mcp.tool()
def validate_stock_symbol_tool(symbol: str) -> Dict:
    """Validate if a stock symbol exists in NEPSE."""
    try:
        validation_result = validate_stock_symbol(symbol)
        return {"validation_result": validation_result}
    except Exception as e:
        logger.error(f"Error validating stock symbol {symbol}: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_validation_stats() -> Dict:
    """Get validation statistics and available stocks/indices."""
    try:
        stats = validator.get_stats()
        return {"stats": stats}
    except Exception as e:
        logger.error(f"Error getting validation stats: {e}")
        return {"error": str(e)}

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=PORT)
