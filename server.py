import asyncio
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from nepse import AsyncNepse
import os
import sys
import platform

app = FastAPI()

RESTART_SECRET = "459590b22a2e786209ac3c1aea5a1882"

#pip install --upgrade git+https://github.com/basic-bgnr/NepseUnofficialApi.git

#onrender - pip3 install --upgrade git+https://github.com/surajrimal07/NepseAPI.git@dev
nepseAsync = AsyncNepse()
nepseAsync.setTLSVerification(False)

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
    "MarketDepth": "/MarketDepth",
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

async def restart_app():
    await asyncio.sleep(1)
    os.execv(sys.executable, [sys.executable] + sys.argv)

@app.post("/restart")
async def restart_server(secret: str, background_tasks: BackgroundTasks):
    if secret != RESTART_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret key")

    try:
        background_tasks.add_task(restart_app)
        return JSONResponse({"message": "Server restarting..."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restart failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def get_index():
    content = "<ul>" + "".join([f"<li><a href={value}>{key}</a></li>" for key, value in routes.items()]) + "</ul>"
    html_content = f"<h1>Serving hot stock data using FastAPI</h1>{content}"
    return Response(content=html_content, media_type="text/html")

@app.get(routes["Summary"])
async def get_summary():
    data = await _get_summary()
    return JSONResponse(content= data, headers={"Access-Control-Allow-Origin": "*"})


async def _get_summary():
    response = dict()
    for obj in await nepseAsync.getSummary():
        response[obj["detail"]] = obj["value"]
    return response

@app.get(routes["NepseIndex"])
async def get_nepse_index():
    return JSONResponse(content= await _get_nepse_index(), headers={"Access-Control-Allow-Origin": "*"})


async def _get_nepse_index():
    response = dict()
    for obj in await nepseAsync.getNepseIndex():
        response[obj["index"]] = obj
    return response

@app.get(routes["LiveMarket"])
async def get_live_market():
    data = await nepseAsync.getLiveMarket()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


#Bugged, hoping for fix from the library
@app.get(routes["MarketDepth"])
async def get_market_depth(symbol: str):
    data = await nepseAsync.getSymbolMarketDepth(symbol)
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["NepseSubIndices"])
async def get_nepse_subindices():
    data = await _get_nepse_subindices()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


async def _get_nepse_subindices():
    response = dict()
    for obj in await nepseAsync.getNepseSubIndices():
        response[obj["index"]] = obj
    return response

@app.get(routes["TopTenTradeScrips"])
async def get_top_ten_trade_scrips():
    data = await nepseAsync.getTopTenTradeScrips()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopTenTransactionScrips"])
async def get_top_ten_transaction_scrips():
    data = await nepseAsync.getTopTenTransactionScrips()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopTenTurnoverScrips"])
async def get_top_ten_turnover_scrips():
    data = await nepseAsync.getTopTenTurnoverScrips()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["SupplyDemand"])
async def get_supply_demand():
    data = await nepseAsync.getSupplyDemand()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopGainers"])
async def get_top_gainers():
    data = await nepseAsync.getTopGainers()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopLosers"])
async def get_top_losers():
    data = await nepseAsync.getTopLosers()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["IsNepseOpen"])
async def is_nepse_open():
    data = await nepseAsync.isNepseOpen()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["DailyNepseIndexGraph"])
async def get_daily_nepse_index_graph():
    data = await nepseAsync.getDailyNepseIndexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailySensitiveIndexGraph"])
async def get_daily_sensitive_index_graph():
    data = await nepseAsync.getDailySensitiveIndexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyFloatIndexGraph"])
async def get_daily_float_index_graph():
    data = await nepseAsync.getDailyFloatIndexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailySensitiveFloatIndexGraph"])
async def get_daily_sensitive_float_index_graph():
    data = await nepseAsync.getDailySensitiveFloatIndexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyBankSubindexGraph"])
async def get_daily_bank_subindex_graph():
    data = await nepseAsync.getDailyBankSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyDevelopmentBankSubindexGraph"])
async def get_daily_development_bank_subindex_graph():
    data = await nepseAsync.getDailyDevelopmentBankSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyFinanceSubindexGraph"])
async def get_daily_finance_subindex_graph():
    data = await nepseAsync.getDailyFinanceSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyHotelTourismSubindexGraph"])
async def get_daily_hotel_tourism_subindex_graph():
    data = await nepseAsync.getDailyHotelTourismSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyHydroPowerSubindexGraph"])
async def get_daily_hydro_power_subindex_graph():
    data = await nepseAsync.getDailyHydroSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["DailyInvestmentSubindexGraph"])
async def get_daily_investment_subindex_graph():
    data = await nepseAsync.getDailyInvestmentSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyLifeInsuranceSubindexGraph"])
async def get_daily_life_insurance_subindex_graph():
    data = await nepseAsync.getDailyLifeInsuranceSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyManufacturingProcessingSubindexGraph"])
async def get_daily_manufacturing_processing_subindex_graph():
    data = await nepseAsync.getDailyManufacturingSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyMicrofinanceSubindexGraph"])
async def get_daily_microfinance_subindex_graph():
    data = await nepseAsync.getDailyMicrofinanceSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyMutualFundSubindexGraph"])
async def get_daily_mutual_fund_subindex_graph():
    data = await nepseAsync.getDailyMutualfundSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyNonLifeInsuranceSubindexGraph"])
async def get_daily_non_life_insurance_subindex_graph():
    data = await nepseAsync.getDailyNonLifeInsuranceSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyOthersSubindexGraph"])
async def get_daily_others_subindex_graph():
    data = await nepseAsync.getDailyOthersSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyTradingSubindexGraph"])
async def get_daily_trading_subindex_graph():
    data = await nepseAsync.getDailyTradingSubindexGraph()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["DailyScripPriceGraph"])
async def get_daily_scrip_price_graph(symbol: str):
    data = await nepseAsync.getDailyScripPriceGraph(symbol)
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["CompanyList"])
async def get_company_list():
    data = await nepseAsync.getCompanyList()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["SectorScrips"])
async def get_sector_scrips():
    data = await nepseAsync.getSectorScrips()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["CompanyDetails"])
async def get_company_details(symbol: str):
    data = await nepseAsync.getCompanyDetails(symbol)
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["PriceVolume"])
async def get_price_volume():
    data = await nepseAsync.getPriceVolume()
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["PriceVolumeHistory"])
async def get_price_volume_history(symbol: str):
    data = await nepseAsync.getCompanyPriceVolumeHistory(symbol)
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["Floorsheet"])
async def get_floorsheet():
    floorsheet_data = await nepseAsync.getFloorSheet()
    return JSONResponse(content=floorsheet_data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["FloorsheetOf"])
async def get_floorsheet_of(symbol: str):
    data = await nepseAsync.getFloorSheetOf(symbol)
    return JSONResponse(content=data, headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["SecurityList"])
async def getSecurityList():
    data = await nepseAsync.getSecurityList()
    return JSONResponse (content=data, headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["TradeTurnoverTransactionSubindices"])
async def getTradeTurnoverTransactionSubindices():
    companies = {company["symbol"]: company for company in await nepseAsync.getCompanyList()}

    turnover = {obj["symbol"]: obj for obj in await nepseAsync.getTopTenTurnoverScrips()}
    transaction = {obj["symbol"]: obj for obj in await nepseAsync.getTopTenTransactionScrips()}
    trade = {obj["symbol"]: obj for obj in await nepseAsync.getTopTenTradeScrips()}

    gainers = {obj["symbol"]: obj for obj in await nepseAsync.getTopGainers()}
    losers = {obj["symbol"]: obj for obj in await nepseAsync.getTopLosers()}

    price_vol_info = {obj["symbol"]: obj for obj in await nepseAsync.getPriceVolume()}

    sector_sub_indices = await _getNepseSubIndices()
    # this is done since nepse sub indices and sector name are different
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
            "lastUpdatedDateTime": price_vol_info.get(symbol, {}).get("lastUpdatedDateTime", 0),
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

        #let's filter here based on ltp and previos close, if ltp = 0 or previous close = 0, then the company is not trading
        if company_details["ltp"] == 0 or company_details["previousClose"] == 0:
            continue
        scrips_details[symbol] = company_details

    sector_details = dict()
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
            "turnover": sector_sub_indices[sector_mapper[sector]],
            "sectorName": sector,
        }

    return JSONResponse({"scripsDetails": scrips_details, "sectorsDetails": sector_details}, headers={"Access-Control-Allow-Origin": "*"})

async def _getNepseSubIndices():
    return {obj["index"]: obj for obj in await nepseAsync.getNepseSubIndices()}

if __name__ == "__main__":
    import uvicorn
    import platform
    import os

    base_config = {
        "app": "server:app",
        "host": "0.0.0.0",
        "port": 8000,
        "timeout_keep_alive": 60,
        "limit_concurrency": 1000,
        "backlog": 2048,
        "http": "h11",
    }
    if platform.system() == "Windows":
        base_config["reload"] = True
    else:
        if os.getenv("RENDER"):
            base_config.update({
                "http": "httptools"
            })
        else:
            base_config.update({
                "workers": 4,
                "http": "httptools",
                "loop": "uvloop"
            })

    uvicorn.run(**base_config)