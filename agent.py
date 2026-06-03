import yfinance as yf
import pandas_ta as ta
import pandas as pd

print("啟動 Agent：開始抓取 0050.TW 歷史資料...")

# 1. 抓取過去 3 個月的資料，確保有足夠天數計算 KD
df = yf.download("0050.TW", period="3mo")

if df.empty:
    print("無法抓取資料，請檢查網路或股票代號。")
else:
    # 2. 計算 5日 KD 值
    # k=5 代表 5日 RSV, d=3 代表 K值平滑, smooth_k=3 代表 D值平滑
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=5, d=3, smooth_k=3)
    
    # 3. 將計算結果合併回原資料表
    df = pd.concat([df, stoch], axis=1)
    
    # pandas_ta 產生的欄位名稱通常為 STOCHk_5_3_3, STOCHd_5_3_3
    # 我們用程式自動尋找包含 'STOCHk' 的欄位，避免版本差異導致名稱不同
    k_col = [col for col in df.columns if 'STOCHk' in col][0]
    d_col = [col for col in df.columns if 'STOCHd' in col][0]
    
    # 4. 取得最新一天的資料 (iloc[-1] 代表最後一列)
    # 取出數值，使用 .item() 確保提取出純數字 (避免 yfinance 新版格式問題)
    latest_date = df.index[-1].strftime("%Y-%m-%d")
    latest_close = float(df['Close'].iloc[-1].iloc[0]) if isinstance(df['Close'], pd.DataFrame) else float(df['Close'].iloc[-1])
    latest_k = float(df[k_col].iloc[-1])
    latest_d = float(df[d_col].iloc[-1])
    
    # 5. 印出報表
    print("\n=======================================")
    print(f"📈 觀察日期: {latest_date}")
    print(f"🎯 觀察標的: 0050 (元大台灣50)")
    print(f"💰 最新收盤價: {latest_close:.2f} 元")
    print(f"📊 5日 K 值: {latest_k:.2f}")
    print(f"📊 5日 D 值: {latest_d:.2f}")
    print("=======================================\n")
    
    # 6. 條件判斷：K < 35 且 黃金交叉
    yest_k = float(df[k_col].iloc[-2])
    yest_d = float(df[d_col].iloc[-2])
    
    if latest_k < 35 and (latest_k > latest_d) and (yest_k <= yest_d):
        print("🔥【訊號觸發】符合 K < 35 且 K 值由下往上穿過 D 值！")
    else:
        print("💡【狀態】今日未符合設定之進場條件。")
