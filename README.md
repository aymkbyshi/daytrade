# Alpaca自動売買システム

このプロジェクトは、Alpaca APIを使用した米国株式の自動売買システムです。移動平均クロス戦略を実装し、自動的に売買を行います。

## 機能

- 米国株式市場（NYSE/NASDAQ）での自動売買
- 移動平均クロス戦略（MA5/MA20）の実装
- リアルタイムの市場データ取得
- 自動注文実行
- 詳細なログ記録

## 必要条件

- Python 3.8以上
- Alpaca APIアカウント（Paper Trading）
- 必要なPythonパッケージ（requirements.txtに記載）

## セットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/alpaca-auto-trading.git
cd alpaca-auto-trading
```

2. 仮想環境の作成と有効化
```bash
python3 -m venv venv
source venv/bin/activate  # Linuxの場合
# または
.\venv\Scripts\activate  # Windowsの場合
```

3. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
`.env`ファイルを作成し、以下の内容を設定：
```
APCA_API_KEY_ID=あなたのAPIキー
APCA_API_SECRET_KEY=あなたのシークレットキー
APCA_API_BASE_URL=https://paper-api.alpaca.markets
```

## 使用方法

1. プログラムの実行
```bash
python auto_trader_ma.py
```

2. ログの確認
- ログファイルは`log`ディレクトリに保存されます
- 日付ごとに新しいログファイルが作成されます

## 取引戦略

- 移動平均クロス戦略を使用
- MA5（5期間移動平均）とMA20（20期間移動平均）のクロスで売買判断
- ゴールデンクロス（MA5 > MA20）で買い
- デッドクロス（MA5 < MA20）で売り

## 注意事項

- このプログラムはPaper Trading環境で動作します
- 実際の取引を行う前に、十分なテストを実施してください
- 投資は自己責任で行ってください

## ライセンス

MIT License

## 作者

あなたの名前 