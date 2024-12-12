import asyncio
import zmq.asyncio
from nepse import AsyncNepse
from asyncio import WindowsSelectorEventLoopPolicy
import signal

nepseAsync = AsyncNepse()
nepseAsync.setTLSVerification(False)
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

routes = {
    "PriceVolume": "/PriceVolume",
    "Summary": "/Summary",
    "SupplyDemand": "/SupplyDemand",
    "TopGainers": "/TopGainers",
    "TopLosers": "/TopLosers",
    "TopTenTradeScrips": "/TopTenTradeScrips",
    "TopTenTurnoverScrips": "/TopTenTurnoverScrips",
    "TopTenTransactionScrips": "/TopTenTransactionScrips",
    "IsNepseOpen": "/IsNepseOpen",
    "NepseIndex": "/NepseIndex",
    "NepseSubIndices": "/NepseSubIndices",
    "DailyScripPriceGraph": "/DailyScripPriceGraph",
    "CompanyList": "/CompanyList",
    "SectorScrips": "/SectorScrips",
    "CompanyDetails": "/CompanyDetails",
    "Floorsheet": "/Floorsheet",
    "FloorsheetOf": "/FloorsheetOf",
    "PriceVolumeHistory": "/PriceVolumeHistory",
    "SecurityList": "/SecurityList",
    "TradeTurnoverTransactionSubindices": "/TradeTurnoverTransactionSubindices",
    "LiveMarket": "/LiveMarket",
    "DailyNepseIndexGraph": "/DailyNepseIndexGraph",
    "DailySensitiveIndexGraph": "/DailySensitiveIndexGraph",
    "DailyFloatIndexGraph": "/DailyFloatIndexGraph",
    "DailySensitiveFloatIndexGraph": "/DailySensitiveFloatIndexGraph",
    "DailyBankSubindexGraph": "/DailyBankSubindexGraph",
    "DailyDevelopmentBankSubindexGraph": "/DailyDevelopmentBankSubindexGraph",
    "DailyFinanceSubindexGraph": "/DailyFinanceSubindexGraph",
    "DailyHotelTourismSubindexGraph": "/DailyHotelTourismSubindexGraph",
    "DailyHydroPowerSubindexGraph": "/DailyHydroPowerSubindexGraph",
    "DailyInvestmentSubindexGraph": "/DailyInvestmentSubindexGraph",
    "DailyLifeInsuranceSubindexGraph": "/DailyLifeInsuranceSubindexGraph",
    "DailyManufacturingProcessingSubindexGraph": "/DailyManufacturingProcessingSubindexGraph",
    "DailyMicrofinanceSubindexGraph": "/DailyMicrofinanceSubindexGraph",
    "DailyMutualFundSubindexGraph": "/DailyMutualFundSubindexGraph",
    "DailyNonLifeInsuranceSubindexGraph": "/DailyNonLifeInsuranceSubindexGraph",
    "DailyOthersSubindexGraph": "/DailyOthersSubindexGraph",
    "DailyTradingSubindexGraph": "/DailyTradingSubindexGraph",
}

async def _get_summary():
    response = {obj["detail"]: obj["value"] for obj in await nepseAsync.getSummary()}
    return response

async def _get_nepse_index():
    response = {obj["index"]: obj for obj in await nepseAsync.getNepseIndex()}
    return response

async def _get_nepse_subindices():
    response = {obj["index"]: obj for obj in await nepseAsync.getNepseSubIndices()}
    return response

async def _get_trade_turnover_transaction_subindices():
    companies = {company["symbol"]: company for company in await nepseAsync.getCompanyList()}
    turnover = {obj["symbol"]: obj for obj in await nepseAsync.getTopTenTurnoverScrips()}
    transaction = {obj["symbol"]: obj for obj in await nepseAsync.getTopTenTransactionScrips()}
    trade = {obj["symbol"]: obj for obj in await nepseAsync.getTopTenTradeScrips()}
    gainers = {obj["symbol"]: obj for obj in await nepseAsync.getTopGainers()}
    losers = {obj["symbol"]: obj for obj in await nepseAsync.getTopLosers()}
    price_vol_info = {obj["symbol"]: obj for obj in await nepseAsync.getPriceVolume()}
    sector_sub_indices = await _get_nepse_subindices()
    sector_mapper = {
        "Commercial Banks": "Banking SubIndex",
        "Development Banks": "Development Bank Index",
        "Finance": "Finance Index",
        "Hotels And Tourism": "Hotels And Tourism Index",
        "Hydro Power": "HydroPower Index",
        "Investment": "Investment Index",
        "Life Insurance": "Life Insurance",
        "Manufacturing And Processing": "Manufacturing And Processing",
        "Microfinance": "Microfinance Index",
        "Mutual Fund": "Mutual Fund",
        "Non Life Insurance": "Non Life Insurance",
        "Others": "Others Index",
        "Tradings": "Trading Index",
    }

    scrips_details = {}
    for symbol, company in companies.items():
        company_details = {
            "symbol": symbol,
            "sector": company["sectorName"],
            "Turnover": turnover.get(symbol, {}).get("turnover", 0),
            "transaction": transaction.get(symbol, {}).get("totalTrades", 0),
            "volume": trade.get(symbol, {}).get("shareTraded", 0),
            "previousClose": price_vol_info.get(symbol, {}).get("previousClose", 0),
            "lastUpdatedDateTime": price_vol_info.get(symbol, {}).get("lastUpdatedDateTime", 0),
            "name": company.get("securityName", ""),
            "category": company.get("instrumentType"),
        }

        if symbol in gainers:
            company_details.update({
                "pointChange": gainers[symbol]["pointChange"],
                "percentageChange": gainers[symbol]["percentageChange"],
                "ltp": gainers[symbol]["ltp"],
            })
        elif symbol in losers:
            company_details.update({
                "pointChange": losers[symbol]["pointChange"],
                "percentageChange": losers[symbol]["percentageChange"],
                "ltp": losers[symbol]["ltp"],
            })
        else:
            company_details.update({
                "pointChange": 0,
                "percentageChange": 0,
                "ltp": 0,
            })

        if company_details["ltp"] == 0 or company_details["previousClose"] == 0:
            continue
        scrips_details[symbol] = company_details

    sector_details = {}
    sectors = {company["sectorName"] for company in companies.values()}
    for sector in sectors:
        total_trades, total_trade_quantity, total_turnover = 0, 0, 0
        for scrip_details in scrips_details.values():
            if scrip_details["sector"] == sector:
                total_trades += scrip_details["transaction"]
                total_trade_quantity += scrip_details["volume"]
                total_turnover += scrip_details["Turnover"]

        sector_details[sector] = {
            "transaction": total_trades,
            "volume": total_trade_quantity,
            "totalTurnover": total_turnover,
            "turnover": sector_sub_indices[sector_mapper.get(sector, sector)],
            "sectorName": sector,
        }

    return {"scripsDetails": scrips_details, "sectorsDetails": sector_details}

# ZMQ route handler
async def handle_route(route: str, params: dict):
    route_handlers = {
        "Summary": lambda: _get_summary(),
        "NepseIndex": lambda: _get_nepse_index(),
        "LiveMarket": lambda: nepseAsync.getLiveMarket(),
        "TopTenTradeScrips": lambda: nepseAsync.getTopTenTradeScrips(),
        "TopTenTransactionScrips": lambda: nepseAsync.getTopTenTransactionScrips(),
        "TopTenTurnoverScrips": lambda: nepseAsync.getTopTenTurnoverScrips(),
        "TopGainers": lambda: nepseAsync.getTopGainers(),
        "TopLosers": lambda: nepseAsync.getTopLosers(),
        "IsNepseOpen": lambda: nepseAsync.isNepseOpen(),
        "DailyNepseIndexGraph": lambda: nepseAsync.getDailyNepseIndexGraph(),
        "DailySensitiveIndexGraph": lambda: nepseAsync.getDailySensitiveIndexGraph(),
        "DailyFloatIndexGraph": lambda: nepseAsync.getDailyFloatIndexGraph(),
        "DailySensitiveFloatIndexGraph": lambda: nepseAsync.getDailySensitiveFloatIndexGraph(),
        "DailyBankSubindexGraph": lambda: nepseAsync.getDailyBankSubindexGraph(),
        "DailyDevelopmentBankSubindexGraph": lambda: nepseAsync.getDailyDevelopmentBankSubindexGraph(),
        "DailyFinanceSubindexGraph": lambda: nepseAsync.getDailyFinanceSubindexGraph(),
        "DailyHotelTourismSubindexGraph": lambda: nepseAsync.getDailyHotelTourismSubindexGraph(),
        "DailyHydroPowerSubindexGraph": lambda: nepseAsync.getDailyHydroSubindexGraph(),
        "DailyInvestmentSubindexGraph": lambda: nepseAsync.getDailyInvestmentSubindexGraph(),
        "DailyLifeInsuranceSubindexGraph": lambda: nepseAsync.getDailyLifeInsuranceSubindexGraph(),
        "DailyManufacturingProcessingSubindexGraph": lambda: nepseAsync.getDailyManufacturingSubindexGraph(),
        "DailyMicrofinanceSubindexGraph": lambda: nepseAsync.getDailyMicrofinanceSubindexGraph(),
        "DailyMutualFundSubindexGraph": lambda: nepseAsync.getDailyMutualfundSubindexGraph(),
        "DailyNonLifeInsuranceSubindexGraph": lambda: nepseAsync.getDailyNonLifeInsuranceSubindexGraph(),
        "DailyOthersSubindexGraph": lambda: nepseAsync.getDailyOthersSubindexGraph(),
        "DailyTradingSubindexGraph": lambda: nepseAsync.getDailyTradingSubindexGraph(),
        "DailyScripPriceGraph": lambda: nepseAsync.getDailyScripPriceGraph(params.get("symbol")),
        "CompanyList": lambda: nepseAsync.getCompanyList(),
        "SectorScrips": lambda: nepseAsync.getSectorScrips(),
        "CompanyDetails": lambda: nepseAsync.getCompanyDetails(params.get("symbol")),
        "PriceVolume": lambda: nepseAsync.getPriceVolume(),
        "PriceVolumeHistory": lambda: nepseAsync.getCompanyPriceVolumeHistory(params.get("symbol")),
        "Floorsheet": lambda: nepseAsync.getFloorSheet(),
        "FloorsheetOf": lambda: nepseAsync.getFloorSheetOf(params.get("symbol")),
        "SecurityList": lambda: nepseAsync.getSecurityList(),
        "TradeTurnoverTransactionSubindices": lambda: _get_trade_turnover_transaction_subindices(),
        "SupplyDemand": lambda: nepseAsync.getSupplyDemand(),
        "NepseSubIndices": lambda: _get_nepse_subindices()
    }

    handler = route_handlers.get(route)
    if handler:
        return await handler()
    return {"error": "Route not found"}

# ZMQ listener
async def zmq_listener():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://0.0.0.0:5555")
    print("ZMQ listener started on tcp://0.0.0.0:5555")

    loop = asyncio.get_running_loop()
    shutdown_event = asyncio.Event()

    def cleanup():
        print("\nCleaning up resources...")
        socket.close(linger=0)
        context.term()

    def signal_handler(*args):
        print("\nShutting down gracefully...")
        shutdown_event.set()
        loop.call_soon_threadsafe(loop.stop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        while not shutdown_event.is_set():
            try:
                message = await asyncio.wait_for(socket.recv_json(), timeout=1.0)
                route = message.get("route")
                params = message.get("params", {})
                response = await handle_route(route, params)
                await socket.send_json(response)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error handling route {route}: {e}")
                await socket.send_json({})

    finally:
        cleanup()

if __name__ == "__main__":
    asyncio.run(zmq_listener())