import yfinance as yf

# Define the stock ticker and the time range
ticker = "CB"  # Chubb Limited
start_date = "2024-07-07"
end_date = "2024-8-10"

# Download hourly data using yfinance
data = yf.download(ticker, start=start_date, end=end_date, interval="1h")
data.to_csv('Chubb_Limited_Hourly_Kline_1.csv')