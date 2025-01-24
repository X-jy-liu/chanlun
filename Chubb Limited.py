import yfinance as yf
import pandas as pd
import numpy as np
import mplfinance as mpf

# Define the stock ticker and the time range
ticker = "CB"  # Chubb Limited
# start_date = "2024-07-09"
# end_date = "2024-8-10"

# # Download hourly data using yfinance
# data = yf.download(ticker, start=start_date, end=end_date, interval="1h")
# data.to_csv('Chubb_Limited_Hourly_Kline.csv')

file_path = 'Chubb_Limited_Hourly_Kline.csv'
data = pd.read_csv(file_path)
# Convert the 'Datetime' column to datetime
data['Datetime'] = pd.to_datetime(data['Datetime'])

# Set the 'Datetime' column as the index
data.set_index('Datetime', inplace=True)
# print(data.head(3))
# print(f'1st Close Price',data.iloc[0,0])
# print(f'1st High Price',data.iloc[0,1])
# print(f'1st Low Price',data.iloc[0,2])
# print(f'1st Open Price',data.iloc[0,3])
# print(f'1st Volume',data.iloc[0,4])
patterns = []
closest_pattern = 'none'
idx_to_drop = []
# The columns of the data are in order: close, high, low, open, volume
# 先判断顶底分型，然后导出处理了包含关系后的数据
for i in range(1, len(data) - 1):
    prev, curr, next_ = data.iloc[i - 1], data.iloc[i], data.iloc[i + 1]
    # 判断顶分型
    if curr[1] > prev[1] and curr[1] > next_[1] and \
        curr[2] > prev[2] and curr[2] > next_[2]:
        # patterns.append(('top', i))
        closest_pattern = 'top'

    # 判断底分型
    if curr[1] < prev[1] and curr[1] < next_[1] and \
        curr[2] < prev[2] and curr[2] < next_[2]:
        # patterns.append(('bottom', i))
        closest_pattern = 'bottom'

    # 右包含检测，只考虑两个K线之间的包含关系
    if prev[1] > curr[1] and prev[2] < curr[2]:
        # 当右包含出现时，上一个分型为顶分型
        if closest_pattern == 'top':
            data.iloc[i]['low'] = prev[2]
        # 当右包含出现时，上一个分型为底分型
        if closest_pattern == 'bottom':
            data.iloc[i]['high'] = prev[1]
        # 把i-1行的数据删除
        idx_to_drop.append(i-1)

data = data.drop(data.index[idx_to_drop])


# 将已经处理过包含关系的数据重新判断顶分底分型
for i in range(1, len(data) - 1):
    prev, curr, next_ = data.iloc[i - 1], data.iloc[i], data.iloc[i + 1]
    # 判断顶分型
    if curr[1] > prev[1] and curr[1] > next_[1] and \
        curr[2] > prev[2] and curr[2] > next_[2]:
        patterns.append(('top', i))

    # 判断底分型
    if curr[1] < prev[1] and curr[1] < next_[1] and \
        curr[2] < prev[2] and curr[2] < next_[2]:
        patterns.append(('bottom', i))


# -------------------------------
# 1) 构造“拐点连接线”所需的 Series
# -------------------------------
turning_points = pd.Series(data=np.nan, index=data.index)

for pattern, i in patterns:
    if pattern == 'top':
        # 顶分型在 High 标注
        turning_points.iloc[i] = data.iloc[i]['High']
    else:
        # 底分型在 Low 标注
        turning_points.iloc[i] = data.iloc[i]['Low']

# 用于连线的 addplot
apd_line = mpf.make_addplot(
    turning_points,
    type='line',       # 连线
    color='blue',
    linestyle='-',     
    width=1.0,
    secondary_y=False  # 在主图中叠加
)

# -------------------------------
# 2) 分别构造“顶分型点”和“底分型点”的 Series，用来散点标记
# -------------------------------
top_points = pd.Series(data=np.nan, index=data.index)
bottom_points = pd.Series(data=np.nan, index=data.index)

for pattern, i in patterns:
    if pattern == 'top':
        top_points.iloc[i] = data.iloc[i]['High']
    else:
        bottom_points.iloc[i] = data.iloc[i]['Low']

# 顶点散点标记
apd_top = mpf.make_addplot(
    top_points,
    type='scatter',
    marker='^',        # 上三角
    color='red',
    markersize=100     # 可以调节大小
)


# 底点散点标记
apd_bottom = mpf.make_addplot(
    bottom_points,
    type='scatter',
    marker='v',        # 下三角
    color='green',
    markersize=100
)

# -------------------------------
# 3) 整合并画图
# -------------------------------
plots = [apd_line, apd_top, apd_bottom]

mpf.plot(
    data,
    type='candle',      # K线
    addplot=plots,
    title=f"{ticker} Hourly Candlestick with Patterns - remove i-1 if i-1's extreme values including i's",
    figsize=(12, 8)
)

# print(data.columns)

# # Ensure the data has the correct format for mplfinance
# data.index.name = 'Date'
# data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# # Plot the data as K-lines (candlestick chart)
# mpf.plot(data, type='candle', style = 'charles', title='Chubb Limited K-line', ylabel='Price')