# NEPSE API

![Build and Push Docker Image](https://github.com/surajrimal07/NepseAPI/actions/workflows/docker-build.yml/badge.svg)

An unofficial API service for Nepal Stock Exchange (NEPSE) that provides real-time market data through both REST and WebSocket endpoints.

## Features

- Real-time market data access
- Multiple data endpoints including:
  - Price and Volume information
  - Market Summary
  - Live Market Data
  - Top Gainers/Losers
  - Company Details
  - Sector-wise Information
  - Index and Sub-indices
  - Floorsheet Data

## Architecture

The project consists of two main servers:

1. **REST API Server** (`server.py`)
   - Built with FastAPI
   - Provides HTTP endpoints for market data
   - Runs on port 8000
   - Supports CORS
   - Uses uvicorn as the ASGI server

2. **WebSocket Server** (`socketServer.py`)
   - Provides real-time data streaming
   - Runs on port 5555
   - Supports bidirectional communication

## Installation

```sh
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Starting the Servers

```sh
# Start REST API server
python server.py

# Start WebSocket server
python socketServer.py
```

### Docker Support

```sh
docker build -t nepseapi .
docker run -p 8000:8000 -p 5555:5555 nepseapi
```

You can directly use the Docker image from Docker Hub:

```sh
docker run -p 8000:8000 -p 5555:5555 surajrimal/nepseapi:latest
```

Alternatively, you can use the provided Docker Compose file. Clone the project or copy the `docker-compose.yml` file and run:

```sh
docker-compose up -d
```

## API Endpoints

Base URL: `http://localhost:8000`

| Endpoint       | Description                |
|----------------|----------------------------|
| `/Summary`     | Get market summary         |
| `/PriceVolume` | Get price and volume data  |
| `/LiveMarket`  | Get live market data       |
| `/TopGainers`  | Get top gaining stocks     |
| `/TopLosers`   | Get top losing stocks      |
| `/CompanyList` | Get list of all companies  |
| `/NepseIndex`  | Get NEPSE index data       |
| `/Floorsheet`  | Get floorsheet data        |
| `/SupplyDemand`| Get market supply/demand data |

And many more endpoints available at the root URL (`/`).

## Environment Requirements

- Python 3.11+
- Dependencies:
  - FastAPI
  - uvicorn
  - websockets
  - httpx

## License

This project uses an unofficial API client for NEPSE and must be used in accordance with NEPSE's terms and conditions.

## Deployment Options

The project supports multiple deployment configurations:

### PM2 Process Management

- Configuration available in `ecosystem.config.js`
- Manages both REST and WebSocket servers

### CI/CD

- Automated builds via GitHub Actions
- Multi-platform Docker image support
- Automated testing and deployment pipeline

## Disclaimer

This project is not affiliated with the official Nepal Stock Exchange (NEPSE). The author is not liable for any legal issues or damages resulting from the use of this API.

## Acknowledgements

This project depends upon and is heavily inspired by [NepseUnofficialApi](https://github.com/basic-bgnr/NepseUnofficialApi). Thanks to the author [basic-bgnr](https://github.com/basic-bgnr) for open sourcing the project.
