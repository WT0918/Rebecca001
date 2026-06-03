import yfinance as yf
import pandas as pd

print("啟動 Agent：開始抓取 0050.TW 歷史資料...")

# 1. 抓取半年資料，確保有足夠天數計算 5MA 與 KD
df = yf.download("0050.TW", period="6mo")

if df.empty:
    print("無法抓取資料，請檢查網路或股票代號。")
else:
    # 處理 yfinance 新版可能產生的雙層欄位問題
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # ==========================================
    # 2. 運算區：計算 5MA 與 KD 值
    # ==========================================
    # 計算 5日均線 (5MA)
    df['5MA'] = df['Close'].rolling(window=5).mean()

    # 計算 KD 值
    rsv_period = 5 # 5日 RSV
    roll_low = df['Low'].rolling(window=rsv_period).min()
    roll_high = df['High'].rolling(window=rsv_period).max()
    df['RSV'] = 100 * (df['Close'] - roll_low) / (roll_high - roll_low)
    df['RSV'] = df['RSV'].fillna(50)

    k_list = [50]
    d_list = [50]
    
    for rsv in df['RSV'].iloc[1:]:
        k = (k_list[-1] * (2/3)) + (rsv * (1/3))
        d = (d_list[-1] * (2/3)) + (k * (1/3))
        k_list.append(k)
        d_list.append(d)
        
    df['K'] = k_list
    df['D'] = d_list

    # ==========================================
    # 3. 報表區：印出過去 5 日的詳細數據
    # ==========================================
    # 使用 .tail(5) 取得資料表的最後 5 筆資料
    last_5_days = df.tail(5)
    
    print("\n=======================================")
    print("📅 過去 5 日數據追蹤 (0050 元大台灣50)")
    print("=======================================")
    
    # 透過迴圈將這 5 天的資料逐行印出
    for index, row in last_5_days.iterrows():
        date_str = index.strftime("%Y-%m-%d")
        close_price = float(row['Close'])
        ma5 = float(row['5MA'])
        k_val = float(row['K'])
        d_val = float(row['D'])
        
        print(f"[{date_str}] 收盤: {close_price:.2f} | 5MA: {ma5:.2f} | K: {k_val:.2f} | D: {d_val:.2f}")

    # ==========================================
    # 4. 判斷區：最新一日條件判斷
    # ==========================================
    latest_k = float(df['K'].iloc[-1])
    latest_d = float(df['D'].iloc[-1])
    yest_k = float(df['K'].iloc[-2])
    yest_d = float(df['D'].iloc[-2])

    print("\n=======================================")
    print("🎯 今日狀態判定")
    print("=======================================")
    # 條件判斷：K < 35 且 黃金交叉 (K由下往上穿過D)
    if latest_k < 35 and (latest_k > latest_d) and (yest_k <= yest_d):
        print("🔥【訊號觸發】符合 K < 35 且 K 值由下往上穿過 D 值！")
    else:
        print("💡【狀態】今日未符合設定之進場條件。")
    print("=======================================\n")
