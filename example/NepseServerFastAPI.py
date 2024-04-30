from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from nepse import Nepse
import json

app = FastAPI()

nepse = Nepse()
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
    "TradeTurnoverTransactionSubindices": "/TradeTurnoverTransactionSubindices",
}

@app.get("/")
def get_index():
    content = "<ul>" + "".join([f"<li><a href={value}>{key}</a></li>" for key, value in routes.items()]) + "</ul>"
    html_content = f"<h1>Serving hot stock data</h1>{content}"
    return Response(content=html_content, media_type="text/html")

@app.get(routes["Summary"])
def get_summary():
    return JSONResponse(content=_get_summary(), headers={"Access-Control-Allow-Origin": "*"})


def _get_summary():
    response = dict()
    for obj in nepse.getSummary():
        response[obj["detail"]] = obj["value"]
    return response

@app.get(routes["NepseIndex"])
def get_nepse_index():
    return JSONResponse(content=_get_nepse_index(), headers={"Access-Control-Allow-Origin": "*"})


def _get_nepse_index():
    response = dict()
    for obj in nepse.getNepseIndex():
        response[obj["index"]] = obj
    return response

@app.get(routes["NepseSubIndices"])
def get_nepse_subindices():
    return JSONResponse(content=_get_nepse_subindices(), headers={"Access-Control-Allow-Origin": "*"})


def _get_nepse_subindices():
    response = dict()
    for obj in nepse.getNepseSubIndices():
        response[obj["index"]] = obj
    return response

@app.get(routes["TopTenTradeScrips"])
def get_top_ten_trade_scrips():
    return JSONResponse(content=nepse.getTopTenTradeScrips(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopTenTransactionScrips"])
def get_top_ten_transaction_scrips():
    return JSONResponse(content=nepse.getTopTenTransactionScrips(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopTenTurnoverScrips"])
def get_top_ten_turnover_scrips():
    return JSONResponse(content=nepse.getTopTenTurnoverScrips(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["SupplyDemand"])
def get_supply_demand():
    return JSONResponse(content=nepse.getSupplyDemand(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopGainers"])
def get_top_gainers():
    return JSONResponse(content=nepse.getTopGainers(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TopLosers"])
def get_top_losers():
    return JSONResponse(content=nepse.getTopLosers(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["IsNepseOpen"])
def is_nepse_open():
    return JSONResponse(content=nepse.isNepseOpen(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["DailyNepseIndexGraph"])
def get_daily_nepse_index_graph():
    return JSONResponse(content=nepse.getDailyNepseIndexGraph(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["DailyScripPriceGraph"])
def get_daily_scrip_price_graph(symbol: str):
    return JSONResponse(content=nepse.getDailyScripPriceGraph(symbol), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["CompanyList"])
def get_company_list():
    company_list = nepse.getCompanyList()
    return JSONResponse(content=nepse.getCompanyList(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["SectorScrips"])
def get_sector_scrips():
    return JSONResponse(content=nepse.getSectorScrips(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["CompanyDetails"])
def get_company_details(symbol: str):
    return JSONResponse(content=nepse.getCompanyDetails(symbol), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["PriceVolume"])
def get_price_volume():
    return JSONResponse(content=nepse.getPriceVolume(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["PriceVolumeHistory"])
def get_price_volume_history(symbol: str):
    return JSONResponse(content=nepse.getCompanyPriceVolumeHistory(symbol), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["Floorsheet"])
def get_floorsheet():
    return JSONResponse(content=nepse.getFloorSheet(), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["FloorsheetOf"])
def get_floorsheet_of(symbol: str):
    return JSONResponse(content=nepse.getFloorSheetOf(symbol), headers={"Access-Control-Allow-Origin": "*"})


@app.get(routes["TradeTurnoverTransactionSubindices"])
def get_trade_turnover_transaction_subindices():
    return JSONResponse(content=nepse.getTradeTurnoverTransactionSubindices(), headers={"Access-Control-Allow-Origin": "*"})


if __name__ == "__main__":
    import uvicorn
    #uvicorn.run(app, host="localhost", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
