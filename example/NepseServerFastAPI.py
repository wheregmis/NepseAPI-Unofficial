from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from nepse import Nepse #, AsyncNepse
import json

app = FastAPI()

#pip install --upgrade git+https://github.com/basic-bgnr/NepseUnofficialApi.git@dev

nepse = Nepse()
#asyncnepse = AsyncNepse() #will swich later, currently not all methods are async and has ssl errors
nepse.setTLSVerification(False)

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
    "DailyNepseIndexGraph": "/DailyNepseIndexGraph",
    "DailyScripPriceGraph": "/DailyScripPriceGraph",
    "CompanyList": "/CompanyList",
    "SectorScrips": "/SectorScrips",
    "CompanyDetails": "/CompanyDetails",
    "Floorsheet": "/Floorsheet",
    "FloorsheetOf": "/FloorsheetOf",
    "PriceVolumeHistory": "/PriceVolumeHistory",
    "SecurityList": "/SecurityList",
    "TradeTurnoverTransactionSubindices": "/TradeTurnoverTransactionSubindices",
}

@app.get("/")
async def get_index():
    content = "<ul>" + "".join([f"<li><a href={value}>{key}</a></li>" for key, value in routes.items()]) + "</ul>"
    html_content = f"<h1>Serving hot stock data using FastAPI</h1>{content}"
    return Response(content=html_content, media_type="text/html")

@app.get(routes["Summary"])
async def get_summary():
    return JSONResponse(content= await _get_summary(), headers={"Access-Control-Allow-Origin": "*"})


async def _get_summary():
    response = dict()
    for obj in nepse.getSummary():
        response[obj["detail"]] = obj["value"]
    return response

@app.get(routes["NepseIndex"])
async def get_nepse_index():
    return JSONResponse(content= await _get_nepse_index(), headers={"Access-Control-Allow-Origin": "*"})


async def _get_nepse_index():
    response = dict()
    for obj in nepse.getNepseIndex():
        response[obj["index"]] = obj
    return response

@app.get(routes["NepseSubIndices"])
async def get_nepse_subindices():
    return JSONResponse(content=await _get_nepse_subindices(), headers={"Access-Control-Allow-Origin": "*"})


async def _get_nepse_subindices():
    response = dict()
    for obj in nepse.getNepseSubIndices():
        response[obj["index"]] = obj
    return response

@app.get(routes["TopTenTradeScrips"])
async def get_top_ten_trade_scrips():
    return JSONResponse(content=nepse.getTopTenTradeScrips(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopTenTransactionScrips"])
async def get_top_ten_transaction_scrips():
    return JSONResponse(content=nepse.getTopTenTransactionScrips(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopTenTurnoverScrips"])
async def get_top_ten_turnover_scrips():
    return JSONResponse(content=nepse.getTopTenTurnoverScrips(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["SupplyDemand"])
async def get_supply_demand():
    return JSONResponse(content=nepse.getSupplyDemand(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopGainers"])
async def get_top_gainers():
    return JSONResponse(content=nepse.getTopGainers(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopLosers"])
async def get_top_losers():
    return JSONResponse(content=nepse.getTopLosers(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["IsNepseOpen"])
async def is_nepse_open():
    return JSONResponse(content=nepse.isNepseOpen(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["DailyNepseIndexGraph"])
async def get_daily_nepse_index_graph():
    return JSONResponse(content=nepse.getDailyNepseIndexGraph(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["DailyScripPriceGraph"])
async def get_daily_scrip_price_graph(symbol: str):
    return JSONResponse(content=nepse.getDailyScripPriceGraph(symbol), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["CompanyList"])
async def get_company_list():
    return JSONResponse(content=nepse.getCompanyList(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["SectorScrips"])
async def get_sector_scrips():
    return JSONResponse(content=nepse.getSectorScrips(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["CompanyDetails"])
async def get_company_details(symbol: str):
    return JSONResponse(content=nepse.getCompanyDetails(symbol), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["PriceVolume"])
async def get_price_volume():
    return JSONResponse(content=nepse.getPriceVolume(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["PriceVolumeHistory"])
async def get_price_volume_history(symbol: str):
    return JSONResponse(content=nepse.getCompanyPriceVolumeHistory(symbol), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["Floorsheet"])
async def get_floorsheet():
    return JSONResponse(content=nepse.getFloorSheet(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["FloorsheetOf"])
async def get_floorsheet_of(symbol: str):
    return JSONResponse(content=nepse.getFloorSheetOf(symbol), headers={"Access-Control-Allow-Origin": "*"})


@app.route(routes["CompanyList"])
async def getSecurityList():
    return JSONResponse (content=nepse.getSecurityList(), headers={"Access-Control-Allow-Origin": "*"})

@app.get(routes["TradeTurnoverTransactionSubindices"])
async def getTradeTurnoverTransactionSubindices():
    companies = {company["symbol"]: company for company in nepse.getCompanyList()}
    turnover = {obj["symbol"]: obj for obj in nepse.getTopTenTurnoverScrips()}
    transaction = {obj["symbol"]: obj for obj in nepse.getTopTenTransactionScrips()}
    trade = {obj["symbol"]: obj for obj in nepse.getTopTenTradeScrips()}

    gainers = {obj["symbol"]: obj for obj in nepse.getTopGainers()}
    losers = {obj["symbol"]: obj for obj in nepse.getTopLosers()}

    price_vol_info = {obj["symbol"]: obj for obj in nepse.getPriceVolume()}

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

    scrips_details = dict()
    for symbol, company in companies.items():
        company_details = {}

        company_details["symbol"] = symbol
        company_details["sectorName"] = company["sectorName"]
        company_details["totalTurnover"] = (
            turnover[symbol]["turnover"] if symbol in turnover.keys() else 0
        )
        company_details["totalTrades"] = (
            transaction[symbol]["totalTrades"] if symbol in transaction.keys() else 0
        )
        company_details["totalTradeQuantity"] = (
            trade[symbol]["shareTraded"] if symbol in transaction.keys() else 0
        )

        if symbol in gainers.keys():
            (
                company_details["pointChange"],
                company_details["percentageChange"],
                company_details["ltp"],
            ) = (
                gainers[symbol]["pointChange"],
                gainers[symbol]["percentageChange"],
                gainers[symbol]["ltp"],
            )
        elif symbol in losers.keys():
            (
                company_details["pointChange"],
                company_details["percentageChange"],
                company_details["ltp"],
            ) = (
                losers[symbol]["pointChange"],
                losers[symbol]["percentageChange"],
                losers[symbol]["ltp"],
            )
        else:
            (
                company_details["pointChange"],
                company_details["percentageChange"],
                company_details["ltp"],
            ) = (0, 0, 0)

        scrips_details[symbol] = company_details

    sector_details = dict()
    sectors = {company["sectorName"] for company in companies.values()}
    for sector in sectors:
        total_trades, total_trade_quantity, total_turnover = 0, 0, 0
        for scrip_details in scrips_details.values():
            if scrip_details["sectorName"] == sector:
                total_trades += scrip_details["totalTrades"]
                total_trade_quantity += scrip_details["totalTradeQuantity"]
                total_turnover += scrip_details["totalTurnover"]

        sector_details[sector] = {
            "totalTrades": total_trades,
            "totalTradeQuantity": total_trade_quantity,
            "totalTurnover": total_turnover,
            "index": sector_sub_indices[sector_mapper[sector]],
            "sectorName": sector,
        }

    return JSONResponse({"scripsDetails": scrips_details, "sectorsDetails": sector_details}, headers={"Access-Control-Allow-Origin": "*"})

async def _getNepseSubIndices():
    response = dict()
    for obj in nepse.getNepseSubIndices():
        response[obj["index"]] = obj
    return response

if __name__ == "__main__":
    import uvicorn
    #uvicorn.run(app, host="localhost", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
