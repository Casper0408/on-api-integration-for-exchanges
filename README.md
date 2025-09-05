# on-api-integration-for-exchanges
# FRVI 資金費用波動性指數計算器

## 專案說明

本專案提供一個可重複使用的模組，用於計算永續合約資金費用的波動性指數（Funding Rate Volatility Index, FRVI）。  

透過衡量未平倉量不平衡與委託簿流動性脆弱度兩大維度，實現即時無參數擬合的波動性監控。

## 功能特色

- 即時計算 FRVI 指數，無需回歸或參數擬合  
- 結合持倉不平衡與委託簿深度／價差  
- 支援自訂前 N 層委託簿深度  
- 模組化設計，僅須提供快照資料即能運作  
- 內建錯誤處理與初始化機制，穩定可靠  

## 使用方式

1. 下載或克隆本專案。  
2. 在 `frvi_module_with_api.py` 中實作 `fetch_market_data` 函式，完成跨交易所資料擷取邏輯。  
3. 執行主程式：  
   ```bash
   python3 frvi_module_with_api.py
   ```  
4. 查看終端機輸出或自訂警示機制。

## TODO：實作 `fetch_market_data`

請於 `frvi_module_with_api.py` 中完成以下步驟，確保資料來源正確且穩定：  

- 定義資料來源  
  - 永續合約交易所 open interest API（如 Binance、OKEx）  
  - 現貨或永續合約委託簿 API  

- 擷取並處理未平倉量  
  1. 向各交易所發送 open interest 請求  
  2. 解析回傳 JSON，取出 `oi_long`（多單）與 `oi_short`（空單）  
  3. 彙整多源數據（加總或平均），保持一致性  

- 擷取並處理委託簿深度  
  1. 向各交易所發送 order book 請求  
  2. 解析 `bids` 和 `asks`，取前 N 層價格與數量  
  3. `bids` 由高到低排序，`asks` 由低到高排序  
  4. 多源合併可依流動性指標或預設優先順序選取最終快照  

- 錯誤處理與穩定性  
  - 設定 API 請求超時、重試機制  
  - 處理 HTTP 錯誤和異常回傳格式  
  - 紀錄日誌，並在失敗時拋出 `NotImplementedError` 或自訂例外  

- 範例程式碼片段  
  ```python
  def fetch_market_data(symbol: str, levels_n: int):
      # TODO: 從 Binance API 擷取 open interest
      # TODO: 從 OKEx API 擷取 open interest
      # TODO: 加總或平均多源 oi_long、oi_short
      # TODO: 從 Binance API 擷取 order book
      # TODO: 從 OKEx API 擷取 order book
      # TODO: 合併或選擇 bids、asks 最終快照
      # return oi_long, oi_short, bids, asks
      raise NotImplementedError("TODO: 實作 fetch_market_data")
  ```

## 參數說明

- `symbol`：永續合約標的（例如 `"BTCUSDT"`）  
- `levels_n`：計算委託簿深度時需取前 N 層  
- `poll_interval`：主程式中設定的取樣間隔（秒）  
