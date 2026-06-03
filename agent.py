import yfinance as yf
import pandas as pd

print("啟動 Agent：開始抓取 0050.TW 歷史資料...")

# 1. 抓取半年資料，讓 KD 值的運算有足夠的歷史資料進行平滑
df = yf.download("0050.TW", period="6mo")

if df.empty:
    print("無法抓取資料，請檢查網路或股票代號。")
else:
    # 處理 yfinance 新版可能產生的雙層欄位問題
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # ==========================================
    # 2. 自行計算 KD 值 (完全不需要依賴 pandas-ta)
    # ==========================================
    rsv_period = 5 # 5日 RSV
    
    # 計算 RSV = (收盤價 - N日最低價) / (N日最高價 - N日最低價) * 100
    roll_low = df['Low'].rolling(window=rsv_period).min()
    roll_high = df['High'].rolling(window=rsv_period).max()
    df['RSV'] = 100 * (df['Close'] - roll_low) / (roll_high - roll_low)
    
    # 將前幾天無法計算 RSV 的空值填入 50
    df['RSV'] = df['RSV'].fillna(50)

    # 計算 K 與 D (台灣市場標準平滑權重為 1/3 與 2/3)
    k_list = [50] # 初始 K 值設定為 50
    d_list = [50] # 初始 D 值設定為 50
    
    for rsv in df['RSV'].iloc[1:]:
        k = (k_list[-1] * (2/3)) + (rsv * (1/3))
        d = (d_list[-1] * (2/3)) + (k * (1/3))
        k_list.append(k)
        d_list.append(d)
        
    df['K'] = k_list
    df['D'] = d_list

    # ==========================================
    # 3. 取得最新結果並進行條件判斷
    # ==========================================
    latest_date = df.index[-1].strftime("%Y-%m-%d")
    
    latest_close = float(df['Close'].iloc[-1])
    latest_k = float(df['K'].iloc[-1])
    latest_d = float(df['D'].iloc[-1])
    
    yest_k = float(df['K'].iloc[-2])
    yest_d = float(df['D'].iloc[-2])

    # 印出報表
    print("\n=======================================")
    print(f"📈 觀察日期: {latest_date}")
    print(f"🎯 觀察標的: 0050 (元大台灣50)")
    print(f"💰 最新收盤價: {latest_close:.2f} 元")
    print(f"📊 5日 K 值: {latest_k:.2f}")
    print(f"📊 5日 D 值: {latest_d:.2f}")
    print("=======================================\n")
    
    # 條件判斷：K < 35 且 黃金交叉 (K由下往上穿過D)
    if latest_k < 35 and (latest_k > latest_d) and (yest_k <= yest_d):
        print("🔥【訊號觸發】符合 K < 35 且 K 值由下往上穿過 D 值！")
    else:
        print("💡【狀態】今日未符合設定之進場條件。")
