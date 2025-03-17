import pandas as pd
import matplotlib
# 設置 matplotlib 使用非交互式後端，避免在非主線程創建窗口
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import mplfinance as mpf
import yfinance as yf
import io
import base64
import numpy as np

def get_stock_data(ticker, start_date, end_date):
    """獲取股票數據並計算技術指標"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date, auto_adjust=True)
        
        if data.empty:
            return None, "沒有找到股票數據，請檢查股票代號和日期範圍。"
        
        # 計算 KD 指標
        high_9 = data['High'].rolling(9).max()
        low_9 = data['Low'].rolling(9).min()
        data['%K'] = 100 * ((data['Close'] - low_9) / (high_9 - low_9))
        data['%D'] = data['%K'].rolling(3).mean()
        
        # 計算 MACD
        ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
        data['DIF'] = ema_12 - ema_26
        data['DEA'] = data['DIF'].ewm(span=9, adjust=False).mean()
        data['MACD'] = (data['DIF'] - data['DEA']) * 2
        
        # 計算買賣信號
        # 買入信號: 當 DIF 線從下方穿越 DEA 線時 (MACD 由負轉正)
        data["Buy_Signal"] = data.Close.where((data['DIF'] > data['DEA']) & 
                                             (data['DIF'].shift(1) <= data['DEA'].shift(1)), np.nan)
        # 賣出信號: 當 DIF 線從上方穿越 DEA 線時 (MACD 由正轉負)
        data["Sell_Signal"] = data.Close.where((data['DIF'] < data['DEA']) & 
                                              (data['DIF'].shift(1) >= data['DEA'].shift(1)), np.nan)
        
        return data, None
    except Exception as e:
        return None, f"獲取股票數據時出錯: {str(e)}"

def generate_stock_chart(data, ticker):
    """生成完整的技術分析圖表"""
    try:
        # 創建子圖
        fig, ax = plt.subplots(4, 1, figsize=(12, 12), gridspec_kw={"height_ratios": [3, 1, 1, 1]})
        
        # 設置 K 線圖樣式
        custom_style = mpf.make_mpf_style(
            base_mpf_style="tradingview",
            marketcolors=mpf.make_marketcolors(
                up="red",
                down="green",
                edge={'up': 'red', 'down': 'green'},
                wick={'up': 'red', 'down': 'green'},
                volume={'up': 'red', 'down': 'green'}
            )
        )
        
        # 創建買賣信號圖
        buy_signal = mpf.make_addplot(data.Buy_Signal, type="scatter", markersize=100, marker="^", 
                         color="blue", ax=ax[0])
        sell_signal = mpf.make_addplot(data.Sell_Signal, type="scatter", markersize=100, marker="v", 
                         color="black", ax=ax[0])
        
        apds = [buy_signal, sell_signal]
        
        # 繪製 K 線圖和移動平均線
        mpf_plot = mpf.plot(data=data, type='candle', mav=(5, 10, 20),
                 style=custom_style, ax=ax[0], volume=ax[3], addplot=apds,
                 mavcolors=('blue', 'orange', 'green'), returnfig=True)  # 添加 returnfig=True 以獲取圖形對象
        
        # 獲取移動平均線的圖例
        # 在 mplfinance 中，移動平均線的圖例需要手動添加
        ax[0].set_title(f"{ticker} Stock Price and Moving Averages")
        
        # 創建自定義圖例
        custom_lines = [
            Line2D([0], [0], color='blue', lw=2),
            Line2D([0], [0], color='orange', lw=2),
            Line2D([0], [0], color='green', lw=2)
        ]
        ax[0].legend(custom_lines, ['MA5', 'MA10', 'MA20'], loc='upper left')
        
        # 繪製 KD 指標
        ax[1].plot(data.index, data["%K"], color="blue", label="%K")
        ax[1].plot(data.index, data["%D"], color="orange", label="%D")
        ax[1].set_title("KD Indicator")
        ax[1].legend()
        
        # 繪製 MACD 指標
        bar_colors = ["r" if v >= 0 else "g" for v in data["MACD"]]
        ax[2].plot(data.index, data["DIF"], color="blue", label="DIF")
        ax[2].plot(data.index, data["DEA"], color="orange", label="DEA")
        ax[2].bar(data.index, data["MACD"], color=bar_colors)
        ax[2].set_title("MACD Indicator")
        ax[2].legend()
        
        plt.tight_layout()
        
        # 將圖表轉換為 base64 編碼
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close(fig)
        
        graphic = base64.b64encode(image_png).decode('utf-8')
        return graphic, None
    except Exception as e:
        return None, f"生成圖表時出錯: {str(e)}" 