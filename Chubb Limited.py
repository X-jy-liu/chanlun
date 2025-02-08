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

closest_pattern = 'none'
idx_to_drop = []

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

# ------------------------------第一二步结束------------------------------

# ------------------------------第三步开始：标准序列化------------------------------
# 1. 先计算初步的 patterns
patterns = []
for i in range(1, len(data) - 1):
    prev, curr, next_ = data.iloc[i - 1], data.iloc[i], data.iloc[i + 1]
    
    # 判断顶分型
    is_top = curr['High'] > prev['High'] and curr['High'] > next_['High'] and \
             curr['Low'] > prev['Low'] and curr['Low'] > next_['Low']

    # 判断底分型
    is_bottom = curr['High'] < prev['High'] and curr['High'] < next_['High'] and \
                curr['Low'] < prev['Low'] and curr['Low'] < next_['Low']

    if is_top and is_bottom:
        continue  # 排除不合理情况

    if is_top:
        patterns.append(('top', i))
    elif is_bottom:
        patterns.append(('bottom', i))

# 2. 处理 “最近标准分型” 规则
filtered_patterns = []
last_top_idx = -1
last_bottom_idx = -1

for idx, (pattern, i) in enumerate(sorted(patterns, key=lambda x: x[1])):  # 按 K 线索引排序
    if pattern == 'top':
        # 如果最近的底分型比当前的顶分型更近，则去掉这个顶分型
        if last_bottom_idx != -1 and abs(i - last_bottom_idx) < abs(i - last_top_idx):
            continue  # 不标记当前顶分型
        last_top_idx = i  # 更新最近的顶分型
    else:  # pattern == 'bottom'
        # 如果最近的顶分型比当前的底分型更近，则去掉这个底分型
        if last_top_idx != -1 and abs(i - last_top_idx) < abs(i - last_bottom_idx):
            continue  # 不标记当前底分型
        last_bottom_idx = i  # 更新最近的底分型

    # 保留符合规则的分型
    filtered_patterns.append((pattern, i))

# 3. 重新赋值 patterns（后续的绘图代码仍然适用）
patterns = filtered_patterns


# ------------------------------第三步结束------------------------------

# ------------------------------以下为画图内容------------------------------

# 将已经处理过包含关系的数据重新判断顶分底分型 (需要放到最后)
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
