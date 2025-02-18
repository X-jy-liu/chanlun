import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt

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

def plot_candlestick_with_subplots(original_data, cleaned_data, ticker="CB"):
    """
    绘制两个 K 线子图，分别为原始数据和清理后的数据。

    :param original_data: Pandas DataFrame，原始股票数据
    :param cleaned_data: Pandas DataFrame，清理后的股票数据
    :param ticker: 股票代码（默认 "CB"）
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [1, 1]})

    # Set the main title before plotting to avoid suptitle errors
    fig.suptitle(f"{ticker} Candlestick Chart Comparison", fontsize=14)

    # 绘制原始 K 线图
    mpf.plot(original_data, type='candle', ax=axes[0], style='charles')
    axes[0].set_title(f"{ticker} Original Candlestick Chart")

    # 绘制清理后的 K 线图
    mpf.plot(cleaned_data, type='candle', ax=axes[1], style='charles')
    axes[1].set_title(f"{ticker} Cleaned Candlestick Chart")

    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to fit title
    plt.show()



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

original_data = data.copy()

# plot_candlestick_chart(data)

# The columns of the data are in order: close, high, low, open, volume
# ------------------------------第一二步开始：初步分型，包含关系处理------------------------------

def clean_containing_k_lines(data):
    """
    Recursively cleans the containing K-lines by handling overlapping K-lines 
    based on predefined conditions until no containing relationship exists.
    
    :param data: Pandas DataFrame with columns ['Close', 'High', 'Low', 'Open', 'Volume']
    :return: Cleaned DataFrame with no containing K-lines
    """
    idx_to_drop = []  # Store indices to be removed
    new_data = data.copy()  # Work on a copy to avoid modifying original

    # Iterate through the dataset
    for i in range(2, len(new_data) - 1):  # Ensuring K1, K2, C1, C2 exist
        K1, K2, C1, C2 = new_data.iloc[i - 2], new_data.iloc[i - 1], new_data.iloc[i], new_data.iloc[i + 1]

        # Ensure C1 and C2 have a containing relationship
        if (C1.iloc[1] >= C2.iloc[1] and C1.iloc[2] <= C2.iloc[2]) or (C1.iloc[1] <= C2.iloc[1] and C1.iloc[2] >= C2.iloc[2]):  # 1&2 -> High & Low

            # Case 1: K1 high > K2 high & K1 low > K2 low & C1 low < K2 low
            if K1.iloc[1] > K2.iloc[1] and K1.iloc[2] > K2.iloc[2] and C1.iloc[2] < K2.iloc[2]:  
                new_high = min(C1.iloc[1], C2.iloc[1])  # Take lower high
                new_low = min(C1.iloc[2], C2.iloc[2])  # Take lower low

            # Case 2: K1 high > K2 high & K1 low > K2 low & C1 low > K2 low (Standard Bottom Pattern)
            elif K1.iloc[1] > K2.iloc[1] and K1.iloc[2] > K2.iloc[2] and C1.iloc[2] > K2.iloc[2]:  
                new_high = max(C1.iloc[1], C2.iloc[1])  # Take higher high
                new_low = max(C1.iloc[2], C2.iloc[2])  # Take higher low

            # Case 3: K1 high < K2 high & K1 low < K2 low & C1 high > K2 high
            elif K1.iloc[1] < K2.iloc[1] and K1.iloc[2] < K2.iloc[2] and C1.iloc[1] > K2.iloc[1]:  
                new_high = max(C1.iloc[1], C2.iloc[1])  # Take higher high
                new_low = max(C1.iloc[2], C2.iloc[2])  # Take higher low

            # Case 4: K1 high < K2 high & K1 low < K2 low & C1 high < K2 high (Standard Top Pattern)
            elif K1.iloc[1] < K2.iloc[1] and K1.iloc[2] < K2.iloc[2] and C1.iloc[1] < K2.iloc[1]:  
                new_high = min(C1.iloc[1], C2.iloc[1])  # Take lower high
                new_low = min(C1.iloc[2], C2.iloc[2])  # Take lower low

            else:
                continue  # Skip if none of the cases match

            # Assign new values to C2 (preserving C2's timestamp)
            new_data.iloc[i + 1, 1] = new_high  # Update High
            new_data.iloc[i + 1, 2] = new_low  # Update Low

            # Mark C1 for deletion
            idx_to_drop.append(i)

    # Remove marked rows
    new_data = new_data.drop(new_data.index[idx_to_drop])
    # If containing relationships still exist, recurse
    if len(idx_to_drop) > 0:
        return clean_containing_k_lines(new_data)  # Recursive call until no containing lines exist

    return new_data  # Return cleaned dataset

# --------------------------- clean illegal k-lines where open and close outrange the high and low ---------------------------

def restrict_kline_prices(data):
    """
    Ensures that the Open and Close prices remain within the High and Low boundaries.

    :param data: Pandas DataFrame with columns ['Close', 'High', 'Low', 'Open', 'Volume']
    :return: DataFrame with restricted prices
    """
    # Iterate over each row to check and fix invalid Open/Close prices
    for i in range(len(data)):
        high, low = data.iloc[i, 1], data.iloc[i, 2]  # High, Low
        open_price, close_price = data.iloc[i, 3], data.iloc[i, 0]  # Open, Close

        # Restrict Open price
        if open_price > high:
            data.iloc[i, 3] = high
        elif open_price < low:
            data.iloc[i, 3] = low

        # Restrict Close price
        if close_price > high:
            data.iloc[i, 0] = high
        elif close_price < low:
            data.iloc[i, 0] = low

    return data

# --------------------------- clean illegal k-lines where open and close outrange the high and low ---------------------------

# Call the function on your dataset
tmp = clean_containing_k_lines(data)
data_cleaned = restrict_kline_prices(tmp)

# plot_candlestick_chart(data_cleaned)

# 生成并绘制子图
# print('The data reduction after the containing handling:')
# print(f'Original data length: {len(original_data)}')
# print(f'Cleaned data length: {len(data_cleaned)}')
# print(f'Data shrinkage: {((len(original_data) - len(data_cleaned)) / len(original_data) * 100):.2f}%')




# plot_candlestick_with_subplots(original_data, data_cleaned)

# ------------------------------第一二步结束------------------------------

# ------------------------------第三步开始：标准序列化------------------------------

patterns = []
data = data_cleaned.copy()

# 1. 简单过滤顶分，低分不考虑特殊分型

for i in range(1, len(data) - 1):
    prev, curr, next_ = data.iloc[i - 1], data.iloc[i], data.iloc[i + 1]
    # 判断顶分型
    if curr[1] > prev[1] and curr[1] > next_[1] and \
        curr[2] > prev[2] and curr[2] > next_[2]:
        patterns.append(('top',i))

    # 判断底分型
    if curr[1] < prev[1] and curr[1] < next_[1] and \
        curr[2] < prev[2] and curr[2] < next_[2]:
        patterns.append(('bottom',i))

# 2. 过滤出特殊分型并储存

special_fractals = []

for i in range(len(patterns) - 1):
    f1_type, f1_idx = patterns[i]
    f2_type, f2_idx = patterns[i + 1]
    
    # 1) The difference in their indices is less than 4
    if (f2_idx - f1_idx) < 4:
        special_fractals.append({
            'first fractal': f1_type,
            'first fractal index': f1_idx,
            'second fractal': f2_type,
            'second fractal index': f2_idx
        })



special_patterns = []
for sf in special_fractals:
    special_patterns.append((sf['first fractal'], sf['first fractal index']))
    special_patterns.append((sf['second fractal'], sf['second fractal index']))

special_patterns = list(dict.fromkeys(special_patterns))

Ni = []
print(special_patterns[:5])
i = 0
while i < len(special_patterns) - 1:
    fractal = special_patterns[i]
    next_fractal = special_patterns[i+1]
    if next_fractal[1] - fractal[1] < 4:
        dict = {
                'first fractal': fractal[0],
                'first index': fractal[1],
                'second fractal': next_fractal[0],
                'second index': next_fractal[1]
                # sec idx - first idx < 4
                }
        i += 2
        Ni.append(dict)
    else:
        dict = {
                'first fractal': fractal[0],
                'first index': fractal[1],
                'second fractal': None,
                'second index': None
                # sec idx - first idx < 4
                }
        i += 2
        Ni.append(dict)

for i in Ni:
    print(i)
    print('-'*10)

'''
dictionary
{
    'first fractal':
    'first index'
    'second fractal':
    'second index':
    # sec idx - first idx < 4

}
'''

# plot_candlestick_with_patterns(data,special_patterns)
# last_pattern_idx = -3
# for i in range(1, len(data) - 1):
#     prev, curr, next_ = data.iloc[i - 1], data.iloc[i], data.iloc[i + 1]
    
#     # 判断顶分型
#     is_top = curr['High'] > prev['High'] and curr['High'] > next_['High'] and \
#              curr['Low'] > prev['Low'] and curr['Low'] > next_['Low']

#     # 判断底分型
#     is_bottom = curr['High'] < prev['High'] and curr['High'] < next_['High'] and \
#                 curr['Low'] < prev['Low'] and curr['Low'] < next_['Low']

#     if is_top and is_bottom:
#         continue  # 排除不合理情况

#     if (is_top or is_bottom) and (i - last_pattern_idx > 2):
#         if is_top:
#             patterns.append(('top', i))
#         else:
#             patterns.append(('bottom', i))
#         last_pattern_idx = i  # 更新最近的分型索引

# # plot_candlestick_with_patterns(data,patterns)
# print(type(patterns))
# print('-'*100)
# # 2. 处理 “最近标准分型” 规则
# prev_pattern = None
# indices_to_remove = []
# for idx, (curr_pattern, i) in enumerate(sorted(patterns, key=lambda x: x[1])):  # 按 K 线索引排序
#     if curr_pattern == prev_pattern:
#         indices_to_remove.append(idx)
#     else:
#         prev_pattern = curr_pattern

# for i in sorted(indices_to_remove, reverse=True):
#     del patterns[i]
# # 3. 重新赋值 patterns（后续的绘图代码仍然适用）
# print(patterns)