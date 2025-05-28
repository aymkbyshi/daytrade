import os
import time
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# ロギングの設定
def setup_logging():
    log_dir = 'log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

# Alpaca APIの設定
def setup_alpaca():
    load_dotenv()
    api = tradeapi.REST(
        key_id=os.getenv('APCA_API_KEY_ID'),
        secret_key=os.getenv('APCA_API_SECRET_KEY'),
        base_url=os.getenv('APCA_API_BASE_URL')
    )
    return api

# 口座情報の表示
def show_account_info(api):
    try:
        account = api.get_account()
        logging.info(f"=== 口座情報 ===")
        logging.info(f"口座番号: {account.account_number}")
        logging.info(f"口座残高: ${float(account.cash):.2f}")
        logging.info(f"証拠金残高: ${float(account.equity):.2f}")
        logging.info(f"証拠金維持率: {float(account.maintenance_margin_ratio)*100:.2f}%")
        logging.info(f"取引可能額: ${float(account.buying_power):.2f}")
        logging.info(f"=================")
    except Exception as e:
        logging.error(f"口座情報の取得に失敗: {str(e)}")

# 移動平均の計算
def calculate_ma(data, short_window=5, long_window=20):
    data['MA5'] = data['close'].rolling(window=short_window).mean()
    data['MA20'] = data['close'].rolling(window=long_window).mean()
    return data

# トレードシグナルの生成
def generate_signal(data):
    if len(data) < 2:
        return None
    
    current = data.iloc[-1]
    previous = data.iloc[-2]
    
    # ゴールデンクロス
    if current['MA5'] > current['MA20'] and previous['MA5'] <= previous['MA20']:
        return 'BUY'
    # デッドクロス
    elif current['MA5'] < current['MA20'] and previous['MA5'] >= previous['MA20']:
        return 'SELL'
    
    return None

# メインのトレーディングロジック
def main():
    setup_logging()
    api = setup_alpaca()
    symbol = 'AAPL'  # 取引対象の銘柄
    
    # 口座情報の表示
    show_account_info(api)
    
    while True:
        try:
            # 現在時刻の取得（UTC）
            now = datetime.utcnow()
            
            # 取引時間のチェック（米国東部時間 9:30-16:00）
            et_hour = (now.hour - 4) % 24  # UTCからETへの変換
            if not (9 <= et_hour <= 16):
                logging.info(f"Market is closed (ET: {et_hour}:00). Waiting...")
                time.sleep(300)  # 5分待機
                continue
            
            # 1分足データの取得
            end = now
            start = end - timedelta(minutes=30)
            
            # 日付をISO形式の文字列に変換
            start_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            logging.info(f"Fetching data from {start_str} to {end_str}")
            
            try:
                bars = api.get_bars(
                    symbol,
                    '1Min',
                    start=start_str,
                    end=end_str,
                    adjustment='raw'
                ).df
            except Exception as e:
                logging.error(f"API Error: {str(e)}")
                time.sleep(60)
                continue
            
            # データの確認
            if bars.empty:
                logging.info("No data received from API")
                time.sleep(60)
                continue
                
            logging.info(f"Received data: {len(bars)} bars")
            logging.info(f"Columns: {bars.columns.tolist()}")
            
            # データの前処理
            if 'close' not in bars.columns:
                logging.error("'close' column not found in data")
                time.sleep(60)
                continue
            
            data = calculate_ma(bars)
            
            # 現在のポジション確認
            position = None
            try:
                position = api.get_position(symbol)
                logging.info(f"Current position: {position.qty} shares")
            except:
                logging.info("No current position")
            
            # シグナル生成
            signal = generate_signal(data)
            
            if signal == 'BUY' and position is None:
                # 買い注文
                api.submit_order(
                    symbol=symbol,
                    qty=1,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                logging.info(f"BUY executed for {symbol}")
            
            elif signal == 'SELL' and position is not None:
                # 売り注文
                api.submit_order(
                    symbol=symbol,
                    qty=1,
                    side='sell',
                    type='market',
                    time_in_force='gtc'
                )
                logging.info(f"SELL executed for {symbol}")
            
            else:
                logging.info("No action - signal or condition not met")
            
            # 1分待機
            time.sleep(60)
            
        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main() 