from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from alpaca_trade_api.rest import REST
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Trading Platform")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Alpaca client
alpaca = REST(
    key_id=os.getenv('ALPACA_KEY'),
    secret_key=os.getenv('ALPACA_SECRET'),
    base_url='https://paper-api.alpaca.markets'  # Paper trading URL
)

@app.get("/api/stock/{symbol}")
async def get_stock_price(symbol: str):
    """Get the current price of a stock"""
    try:
        # Get the latest trade
        trade = alpaca.get_latest_trade(symbol)
        
        return {
            "symbol": symbol,
            "price": float(trade.price),
            "timestamp": str(trade.timestamp)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{symbol}/history")
async def get_stock_history(symbol: str):
    """Get historical data for a stock"""
    try:
        # Get bar data for the last 30 days
        bars = alpaca.get_bars(symbol, '1Day').df
        
        # Convert the data to a format suitable for frontend charts
        history = []
        for date, row in bars.iterrows():
            history.append({
                "date": str(date),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": int(row['volume'])
            })
        
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))