import requests
from strands import tool
import csv
from io import StringIO



@tool
def get_daily_historical_stock_data(symbol: str, outputsize: str = "compact") -> dict:
    """Get daily stock data (OHLCV) for any global stock symbol historically for the last 100 days.
    
    Args:
        symbol: Stock symbol (e.g., 'IBM', 'AAPL', 'TSCO.LON', 'SHOP.TRT')
        outputsize: 'compact' for latest 100 days or 'full' for 20+ years of data
    """
    # You'll need to set your API key here
    API_KEY = "Dom will provide in email"
    
    # Build the API request
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if "Error Message" in data:
            return {
                "status": "error",
                "content": [{"text": f"Invalid symbol or API error: {data['Error Message']}"}]
            }
        
        if "Note" in data:
            return {
                "status": "error", 
                "content": [{"text": "API rate limit reached. Please wait before making another request."}]
            }
        
        # Extract the time series data
        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            return {
                "status": "error",
                "content": [{"text": "Unexpected API response format"}]
            }
        
        # Get metadata and time series
        meta_data = data.get("Meta Data", {})
        time_series = data[time_series_key]
        
        # Return in Strands ToolResult format
        result_data = {
            "symbol": symbol,
            "last_refreshed": meta_data.get("3. Last Refreshed"),
            "timezone": meta_data.get("5. Time Zone"),
            "data_points": len(time_series),
            "outputsize": outputsize,
            "daily_data": time_series
        }
        
        return {
            "status": "success",
            "content": [
                {"text": f"Retrieved {len(time_series)} days of data for {symbol}"},
                {"json": result_data}
            ]
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "content": [{"text": f"Network error: {str(e)}"}]
        }
    except Exception as e:
        return {
            "status": "error", 
            "content": [{"text": f"Unexpected error: {str(e)}"}]
        }