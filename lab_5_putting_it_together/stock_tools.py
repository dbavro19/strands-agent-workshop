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
    API_KEY = "1L4X6JEQZSBX0V1F"
    
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
    

@tool
def get_stock_quote(symbol: str) -> dict:
    """Get the latest price and volume information for a stock ticker.
    
    Args:
        symbol: Stock symbol (e.g., 'IBM', 'AAPL', '300135.SHZ')
    """
    # You'll need to set your API key here
    API_KEY = "1L4X6JEQZSBX0V1F"
    
    # Build the API request
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
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
        
        # Extract the quote data
        quote_key = "Global Quote"
        if quote_key not in data:
            return {
                "status": "error",
                "content": [{"text": "Unexpected API response format"}]
            }
        
        quote_data = data[quote_key]
        
        # Extract key quote information
        quote_info = {
            "symbol": quote_data.get("01. symbol"),
            "open": quote_data.get("02. open"),
            "high": quote_data.get("03. high"),
            "low": quote_data.get("04. low"),
            "price": quote_data.get("05. price"),
            "volume": quote_data.get("06. volume"),
            "latest_trading_day": quote_data.get("07. latest trading day"),
            "previous_close": quote_data.get("08. previous close"),
            "change": quote_data.get("09. change"),
            "change_percent": quote_data.get("10. change percent")
        }
        
        # Create readable summary
        price = quote_info.get("price", "N/A")
        change = quote_info.get("change", "N/A")
        change_percent = quote_info.get("change_percent", "N/A")
        
        summary = f"{symbol}: ${price} ({change}, {change_percent})"
        
        return {
            "status": "success",
            "content": [
                {"text": summary},
                {"json": quote_info}
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
    

@tool
def get_company_overview(symbol: str) -> dict:
    """Get comprehensive company overview including financial ratios and key metrics.
    
    Args:
        symbol: Stock symbol (e.g., 'IBM', 'AAPL', 'TSCO.LON')
    """
    # You'll need to set your API key here
    API_KEY = "1L4X6JEQZSBX0V1F"
    
    # Build the API request
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
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
        
        # Check if we got valid company data
        if "Symbol" not in data:
            return {
                "status": "error",
                "content": [{"text": "No company overview data available for this symbol"}]
            }
        
        # Extract key metrics for summary
        company_name = data.get("Name", symbol)
        sector = data.get("Sector", "N/A")
        market_cap = data.get("MarketCapitalization", "N/A")
        pe_ratio = data.get("PERatio", "N/A")
        dividend_yield = data.get("DividendYield", "N/A")
        profit_margin = data.get("ProfitMargin", "N/A")
        
        # Create readable summary
        summary = f"{company_name} ({symbol}): {sector} sector, Market Cap: ${market_cap}, P/E: {pe_ratio}, Dividend Yield: {dividend_yield}, Profit Margin: {profit_margin}"
        
        return {
            "status": "success",
            "content": [
                {"text": summary},
                {"json": data}
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
    


@tool
def get_earnings_calendar(symbol: str = None, horizon: str = "3month") -> dict:
    """Get upcoming earnings calendar for all companies or a specific symbol.
    
    Args:
        symbol: Optional stock symbol (e.g., 'IBM', 'AAPL'). If not provided, returns all companies
        horizon: Time horizon - '3month', '6month', or '12month' (default: '3month')
    """
    # You'll need to set your API key here
    API_KEY = "1L4X6JEQZSBX0V1F"
    
    # Validate horizon parameter
    valid_horizons = ["3month", "6month", "12month"]
    if horizon not in valid_horizons:
        return {
            "status": "error",
            "content": [{"text": f"Invalid horizon. Must be one of: {', '.join(valid_horizons)}"}]
        }
    
    # Build the API request
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "EARNINGS_CALENDAR",
        "horizon": horizon,
        "apikey": API_KEY
    }
    
    # Add symbol if provided
    if symbol:
        params["symbol"] = symbol
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # Check if response contains error message
        content = response.text
        if "Error Message" in content:
            return {
                "status": "error",
                "content": [{"text": "Invalid symbol or API error"}]
            }
        
        if "API call frequency" in content or "rate limit" in content.lower():
            return {
                "status": "error",
                "content": [{"text": "API rate limit reached. Please wait before making another request."}]
            }
        
        # Parse CSV content
        csv_reader = csv.DictReader(StringIO(content))
        earnings_data = []
        
        for row in csv_reader:
            earnings_data.append(row)
        
        if not earnings_data:
            return {
                "status": "error",
                "content": [{"text": "No earnings data found for the specified parameters"}]
            }
        
        # Create summary
        total_earnings = len(earnings_data)
        if symbol:
            summary = f"Found {total_earnings} upcoming earnings events for {symbol} in the next {horizon}"
        else:
            summary = f"Found {total_earnings} upcoming earnings events across all companies in the next {horizon}"
        
        # Add sample of upcoming earnings to summary
        if earnings_data:
            next_few = earnings_data[:3]  # Show first 3 upcoming
            summary += "\n\nNext upcoming earnings:"
            for earning in next_few:
                date = earning.get('reportDate', 'N/A')
                sym = earning.get('symbol', 'N/A')
                name = earning.get('name', 'N/A')
                summary += f"\n• {sym} ({name}): {date}"
        
        return {
            "status": "success",
            "content": [
                {"text": summary},
                {"json": {
                    "horizon": horizon,
                    "symbol": symbol,
                    "total_earnings": total_earnings,
                    "earnings_calendar": earnings_data
                }}
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


import requests
from strands import tool

@tool
def get_earnings_transcript(symbol: str, quarter: str) -> dict:
    """Get earnings call transcript with LLM-based sentiment analysis for a specific quarter.
    
    Args:
        symbol: Stock symbol (e.g., 'IBM', 'AAPL')
        quarter: Fiscal quarter in YYYYQM format (e.g., '2024Q1', '2023Q4')
    """
    # You'll need to set your API key here
    API_KEY = "1L4X6JEQZSBX0V1F"
    
    # Validate quarter format
    if not quarter or len(quarter) != 6 or not quarter[:4].isdigit() or quarter[4] != 'Q' or quarter[5] not in '1234':
        return {
            "status": "error",
            "content": [{"text": "Invalid quarter format. Use YYYYQM format (e.g., '2024Q1', '2023Q4')"}]
        }
    
    # Build the API request
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "EARNINGS_CALL_TRANSCRIPT",
        "symbol": symbol,
        "quarter": quarter,
        "apikey": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=60)  # Longer timeout for transcript data
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if "Error Message" in data:
            return {
                "status": "error",
                "content": [{"text": f"Invalid symbol, quarter, or API error: {data['Error Message']}"}]
            }
        
        if "Note" in data:
            return {
                "status": "error",
                "content": [{"text": "API rate limit reached. Please wait before making another request."}]
            }
        
        # Check if we got valid transcript data
        if "transcript" not in data and "content" not in data:
            return {
                "status": "error",
                "content": [{"text": f"No earnings call transcript available for {symbol} in {quarter}"}]
            }
        
        # Extract key information for summary
        company_name = data.get("symbol", symbol)
        quarter_info = data.get("quarter", quarter)
        fiscal_date = data.get("fiscal_date_ending", "N/A")
        
        # Try to get sentiment or key metrics if available
        sentiment_summary = ""
        if "sentiment" in data:
            sentiment_summary = f", Sentiment: {data.get('sentiment', 'N/A')}"
        
        # Get transcript length for summary
        transcript_text = data.get("transcript", data.get("content", ""))
        word_count = len(transcript_text.split()) if transcript_text else 0
        
        # Create readable summary
        summary = f"Earnings call transcript for {company_name} {quarter_info}"
        if fiscal_date != "N/A":
            summary += f" (Fiscal period ending: {fiscal_date})"
        summary += f"{sentiment_summary}. Transcript contains approximately {word_count:,} words."
        
        return {
            "status": "success",
            "content": [
                {"text": summary},
                {"json": data}
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