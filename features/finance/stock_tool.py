import yfinance as yf

class StockTool:
    def __init__(self):
        # 設定你關注的股票代碼 (可以隨時擴充)
        self.watchlist = {
            "MU": "美光 (Micron)",
            "GOOG": "Google",
            "GLDM": "黃金 ETF",
            "NVDA": "輝達",
            "TSM": "台積電 ADR"
        }

    def check_market(self, user_text):
        """
        掃描使用者說的話，如果有股票關鍵字，就去抓數據。
        回傳：一段包含股價資訊的字串 (如果沒提到股票就回傳 None)
        """
        user_text = user_text.upper() # 轉大寫方便比對
        found_stocks = []
        
        # 1. 關鍵字觸發：如果使用者直接問特定股票
        for symbol, name in self.watchlist.items():
            if symbol in user_text or name in user_text:
                found_stocks.append(symbol)
        
        # 2. 廣泛觸發：如果使用者問「股市」、「持股」、「賺錢沒」
        if not found_stocks and any(k in user_text for k in ["股市", "股票", "股價", "大盤", "持股"]):
             # 如果沒指定哪支，就預設全抓你的持股
             found_stocks = ["MU", "GOOG", "GLDM"]

        if not found_stocks:
            return None

        # 3. 抓取數據
        print(f"Doro 正在查詢股市數據: {found_stocks} ...")
        report = "【系統提供之即時股市數據】\n"
        
        try:
            for symbol in found_stocks:
                ticker = yf.Ticker(symbol)
                # 取得今日即時數據 (若休市則是收盤價)
                data = ticker.history(period="1d")
                
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    # 簡單計算漲跌 (Open vs Close)
                    open_price = data['Open'].iloc[-1]
                    change = ((price - open_price) / open_price) * 100
                    
                    sign = "+" if change >= 0 else ""
                    report += f"- {symbol}: {price:.2f} USD ({sign}{change:.2f}%)\n"
                else:
                    report += f"- {symbol}: 查無數據 (可能休市中)\n"
            
            return report
        except Exception as e:
            print(f"抓股票失敗: {e}")
            return None