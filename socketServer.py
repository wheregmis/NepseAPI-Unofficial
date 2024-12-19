import asyncio
import websockets
from nepse import AsyncNepse
import signal
import json

# Initialize Nepse Async
nepseAsync = AsyncNepse()
nepseAsync.setTLSVerification(False)

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

# WebSocket handler
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

# WebSocket listener
async def ws_listener(websocket, path=None):
    # Handle the WebSocket connection
    print(f"New connection from {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                # Parse the incoming message as JSON
                request = json.loads(message)
                route = request.get('route')
                params = request.get('params', {})
                message_id = request.get('messageId')
                print(f"Received request: {route} with params: {params}")

                # Handle the route
                response_data = await handle_route(route, params)

                # Structure response with messageId
                response = {
                    "messageId": message_id,
                    "data": response_data
                }

                # Send the response back to the client
                await websocket.send(json.dumps(response))
            except json.JSONDecodeError:
                # Handle invalid JSON
                await websocket.send(json.dumps({"error": "Invalid JSON"}))
            except Exception as route_error:
                await websocket.send(json.dumps({
                    "messageId": message_id,
                    "error": str(route_error)
                }))
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        await websocket.close()

# Start WebSocket server on all interfaces
async def start_ws_server():
    server = await websockets.serve(ws_listener, "0.0.0.0", 5555)
    print("WebSocket server started on ws://0.0.0.0:5555")
    await server.wait_closed()

# Running the WebSocket server
if __name__ == "__main__":
    asyncio.run(start_ws_server())