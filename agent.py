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
    last_5_days = df.tail(5)
    
    print("\n=======================================")
    print("📅 過去 5 日數據追蹤 (0050 元大台灣50)")
    print("=======================================")
    
    for index, row in last_5_days.iterrows():
        date_str = index.strftime("%Y-%m-%d")
        close_price = float(row['Close'])
        ma5 = float(row['5MA'])
        k_val = float(row['K'])
        d_val = float(row['D'])
        
        print(f"[{date_str}] 收盤: {close_price:.2f} | 5MA: {ma5:.2f} | K: {k_val:.2f} | D: {d_val:.2f}")

    # ==========================================
    # 4. 判斷區：最新一日多重策略判定
    # ==========================================
    latest_k = float(df['K'].iloc[-1])
    latest_d = float(df['D'].iloc[-1])
    yest_k = float(df['K'].iloc[-2])
    yest_d = float(df['D'].iloc[-2])

    print("\n=======================================")
    print("🎯 今日狀態判定")
    print("=======================================")
    
    # 基本面：確認今天是否發生黃金交叉（快線由下往上穿過慢線）
    is_golden_cross = (latest_k > latest_d) and (yest_k <= yest_d)

    # 策略 A：原有的 K < 35 寬鬆型黃金交叉
    if latest_k < 35 and is_golden_cross:
        print("🔥【訊號觸發】符合 K < 35 且 K 值由下往上穿過 D 值！")
    else:
        print("💡【常規策略】今日未符合 K < 35 交叉條件。")
        
    # 策略 B：精選【黃金勾勾】策略（超跌區確認轉強出手）
    # 邏輯：昨日 K 值在 20 以下（便宜貨出現），且今天確認形成黃金交叉轉強
    # 或者交叉發生在極度低檔的防守區（K < 25）
    if is_golden_cross and (yest_k < 20 or latest_k < 25):
        print("🪝【特選訊號：黃金勾勾】🎯 成功在便宜區（K<20）完成深蹲，且今日快線如勾子般強勢勾起、穿過慢線！買點出現！")
    else:
        print("💡【黃金勾勾策略】今日未出現低檔落底勾起的黃金轉折點。")
        
    print("=======================================\n")
