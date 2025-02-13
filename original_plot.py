import pandas as pd
import numpy as np
import mplfinance as mpf

def plot_candlestick_with_patterns(data, patterns, ticker="CB"):
    """
    绘制 K 线图，并标注顶分型和底分型的点，同时连接这些拐点。
    
    :param data: Pandas DataFrame，包含股票数据，索引为时间戳，列包括 'Open', 'High', 'Low', 'Close', 'Volume'
    :param patterns: List of tuples，形如 [('top', index), ('bottom', index)]
    :param ticker: 股票代码（默认 "CB"）
    """
    # -------------------------------
    # 1) 构造“拐点连接线”所需的 Series
    # -------------------------------
    turning_points = pd.Series(data=np.nan, index=data.index)
    
    for pattern, i in patterns:
        if pattern == 'top':
            turning_points.iloc[i] = data.iloc[i]['High']
        else:
            turning_points.iloc[i] = data.iloc[i]['Low']
    
    # 用于连线的 addplot
    turning_points = turning_points.interpolate()
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
    plots = [apd_top, apd_bottom]
    
    mpf.plot(
        data,
        type='candle',      # K线
        addplot=plots,
        title=f"{ticker} Hourly Candlestick with Patterns",
        figsize=(12, 8)
    )

def plot_candlestick_chart(data, ticker="CB"):
    """
    绘制 K 线图。
    
    :param data: Pandas DataFrame，包含股票数据，索引为时间戳，列包括 'Open', 'High', 'Low', 'Close', 'Volume'
    :param ticker: 股票代码（默认 "CB"）
    """
    mpf.plot(
        data,
        type='candle',      # K线
        title=f"{ticker} Hourly Candlestick Chart",
        volume=True,
        style='charles',
        figsize=(12, 8)
    )


# Define the stock ticker and the time range
ticker = "CB"  # Chubb Limited
file_path = 'Chubb_Limited_Hourly_Kline.csv'
data = pd.read_csv(file_path)
# Convert the 'Datetime' column to datetime
data['Datetime'] = pd.to_datetime(data['Datetime'])

# Set the 'Datetime' column as the index
data.set_index('Datetime', inplace=True)

# plot_candlestick_chart(data)
plot_candlestick_chart(data)

closest_pattern = 'none'
idx_to_drop = []
patterns = []

# ------------------------------第一二步开始：初步分型，包含关系处理------------------------------

# 第一步：初步判断顶底分型，只储存最近的分型信息用作包含判断的条件
# 第二步：根据初步顶底分型判断，更改

# The columns of the data are in order: close, high, low, open, volume
# 先判断顶底分型，然后导出处理了包含关系后的数据
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

plot_candlestick_with_patterns(data,patterns)
