#!/usr/bin/env python3
"""
frvi_module_with_api.py

計算永續合約資金費用波動性指數（Funding Rate Volatility Index, FRVI）。

公式：
    FRVI_t = sqrt( (ΔS_t)^2 + (Spread_t / Depth_t)^2 )

參數定義：
  S_t       = (多單未平倉量 - 空單未平倉量) / (多單未平倉量 + 空單未平倉量)
  ΔS_t      = S_t - S_{t-1}
  Spread_t  = 最優賣價 - 最優買價
  Depth_t   = 頂部 N 個委託量（買+賣）的平均值

使用說明：
  1. 在程式頂端自行設定 symbol、levels_n、poll_interval 等參數。
  2. 實作 fetch_market_data() 函式，從多個交易所拉取並合併 open interest 及 order book 資料。
  3. 以 while 迴圈定時呼叫，取得 FRVI 分數後可記錄、觸發警示或串入儀表板。
"""

from typing import List, Tuple, Optional


class FRVICalculator:
    """
    FRVI 計算器：計算資金費用波動性指數
    """

    def __init__(self, levels_n: int = 5):
        """
        初始化 FRVICalculator

        Args:
            levels_n: 用於計算深度的委託檔層數（買 + 賣 各 N 層）
        """
        self.levels_n: int = levels_n
        self.last_imbalance: Optional[float] = None  # 儲存前一次的不平衡值 S_{t-1}

    def reset(self) -> None:
        """
        重設內部狀態，把 last_imbalance 清空
        """
        self.last_imbalance = None

    def _compute_imbalance(self, oi_long: float, oi_short: float) -> float:
        """
        計算未平倉量不平衡 S_t

        S_t = (oi_long - oi_short) / (oi_long + oi_short)

        Returns:
            S_t，範圍限制在 [-1.0, +1.0]
        """
        total = oi_long + oi_short
        if total <= 0:
            return 0.0
        raw = (oi_long - oi_short) / total
        # 防止數值超出範圍
        return max(min(raw, 1.0), -1.0)

    def _compute_spread_and_depth(
        self,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """
        計算最優價差與平均深度

        Spread = ask[0].price - bid[0].price
        Depth  = (sum(top N bids volume) + sum(top N asks volume)) / (2 * N)

        Args:
            bids: list of (price, volume)，由高到低排序
            asks: list of (price, volume)，由低到高排序

        Returns:
            spread, depth
        """
        if not bids or not asks:
            raise ValueError("bids 與 asks 不可為空列表")

        # 取最優買、最優賣價格
        best_bid, _ = bids[0]
        best_ask, _ = asks[0]
        spread = best_ask - best_bid

        # 計算前 N 層累計委託量
        top_bids = bids[: self.levels_n]
        top_asks = asks[: self.levels_n]
        total_vol = sum(vol for _, vol in top_bids) + sum(vol for _, vol in top_asks)
        depth = total_vol / (2 * self.levels_n)
        return spread, depth

    def update(
        self,
        oi_long: float,
        oi_short: float,
        bids: List[Tuple[float, float]],
        asks: List[Tuple[float, float]]
    ) -> float:
        """
        根據一次快照計算 FRVI 分數

        Args:
          oi_long:  多單未平倉量
          oi_short: 空單未平倉量
          bids:     list of (price, volume)，最高買價在前
          asks:     list of (price, volume)，最低賣價在前

        Returns:
          FRVI_t: 無單位的波動性分數
        """
        # 1. 計算當前不平衡 S_t
        current_imbalance = self._compute_imbalance(oi_long, oi_short)

        # 2. 計算 ΔS_t（若為第一筆則設 0）
        if self.last_imbalance is None:
            delta_s = 0.0
        else:
            delta_s = current_imbalance - self.last_imbalance

        # 3. 計算價差與深度
        spread, depth = self._compute_spread_and_depth(bids, asks)

        # 4. 計算流動性脆弱度指標
        liquidity_ratio = float("inf") if depth <= 0 else spread / depth

        # 5. 最終 FRVI 指數（歐氏範數）
        frvi = (delta_s**2 + liquidity_ratio**2) ** 0.5

        # 6. 更新狀態，為下一次計算做準備
        self.last_imbalance = current_imbalance

        return frvi


# -----------------------------------------------------------------------------
# TODO: 實作跨交易所 API 整合邏輯
#
# 在此函式中，您需要：
# 1. 從永續合約交易所拉取多單與空單未平倉量（open interest）
# 2. 從現貨或永續合約委託簿取得前 N 層 bids/asks
# 3. 處理不同來源的資料格式與單位差異，並加以合併或驗證
# 4. 處理 API Rate Limit、Timeout、重試與錯誤回補
# -----------------------------------------------------------------------------
def fetch_market_data(symbol: str, levels_n: int) -> Tuple[
    float, float, List[Tuple[float, float]], List[Tuple[float, float]]
]:
    """
    TODO: 請實作此函式以取得並彙整市場資料

    Args:
        symbol:    永續合約代號（如 "BTCUSDT"）
        levels_n:  取前 N 層委託簿

    Returns:
        oi_long:  多單未平倉量（彙整後）
        oi_short: 空單未平倉量（彙整後）
        bids:     list of (price, volume)，最高買價在前
        asks:     list of (price, volume)，最低賣價在前
    """
    raise NotImplementedError("TODO: 在此實作 fetch_market_data 函式")


# -----------------------------------------------------------------------------
# 主程式範例
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import time
    import datetime

    symbol = "BTCUSDT"        # 永續合約代號
    levels_n = 5              # 前 N 層委託簿
    poll_interval = 60        # 取樣間隔（秒）

    calculator = FRVICalculator(levels_n=levels_n)
    print(f"開始監控 {symbol} 的 FRVI 指數...")

    while True:
        try:
            # 從 API 取得市場資料
            oi_long, oi_short, bids, asks = fetch_market_data(symbol, levels_n)

            # 計算 FRVI
            frvi_value = calculator.update(oi_long, oi_short, bids, asks)

            # 輸出時間戳與 FRVI 分數
            ts = datetime.datetime.utcnow().isoformat()
            print(f"[{ts} UTC] FRVI = {frvi_value:.4f}")

        except NotImplementedError as nie:
            # 提醒開發者實作資料擷取邏輯
            print(f"待實作：{nie}")

        except Exception as e:
            # 處理執行期間發生的錯誤
            print(f"執行錯誤：{e}")  

        time.sleep(poll_interval)
