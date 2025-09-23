# ShogiProject

将棋の棋譜管理システム - 棋譜の登録・編集・共有・AI解析を行うWebアプリケーション

## 🎯 概要

ShogiProjectは、将棋の棋譜を効率的に管理し、AIによる局面解析機能を提供するWebアプリケーションです。個人の棋譜管理から共有・分析まで、将棋愛好家のニーズに応える包括的なシステムです。

### アーキテクチャ

本システムは2つのマイクロサービスで構成されています：

- **ShogiProject** (本リポジトリ): メインのWebアプリケーション
- **[ShogiProject_Analysis](https://github.com/h-akira/ShogiProject_Analysis)**: AI解析サービス

### 技術スタック

- **フレームワーク**: [WAMBDA](https://github.com/h-akira/wambda) (AWS Lambda用Webフレームワーク)
- **インフラ**: AWS Serverless (Lambda, DynamoDB, S3, CloudFront)
- **デプロイ**: AWS SAM (Serverless Application Model)
- **認証**: AWS Cognito
- **データベース**: DynamoDB (Single Table Design)

## 🏗️ システム構成

![システム構成図](images/structure.png)

- **赤枠**: ShogiProject (本リポジトリ) - メインアプリケーション
- **青枠**: ShogiProject_Analysis - AI解析サービス
- **その他**: 共通インフラ (Cognito, CloudFront等)

各マイクロサービスはSAMで個別にデプロイされ、疎結合なアーキテクチャを実現しています。

## 📊 データ設計

本システムはDynamoDBのSingle Table Designを採用しています。

- **詳細**: [テーブル設計書](doc/table.md)
- **設計方針**: 1つのテーブルで全データを管理し、プレフィックスでデータ種別を識別

## ✨ 機能一覧

### 📝 棋譜管理
- **棋譜登録**: KIF/KI2形式での棋譜取り込み
- **棋譜閲覧**: 盤面表示・手順再生
- **棋譜編集**: 変化手順・コメント追加
- **棋譜削除**: 不要な棋譜の削除

### 🔗 共有機能
- **URL共有**: 一意のURLで棋譜を共有
- **公開設定**: プライベート/パブリック設定
- **アクセス権限**: 特定ユーザーへの閲覧許可

### 🏷️ 整理機能
- **タグ管理**: 棋譜の分類・検索
- **エクスプローラー**: 階層的な棋譜管理
- **検索**: タグ・日付・対局者での絞り込み

### 🤖 AI解析
- **局面解析**: 将棋エンジンによる局面評価
- **最善手表示**: AI推奨手の確認
- **形勢グラフ**: 対局全体の形勢変化

### 🚧 開発予定
- **盤面入力**: マウス操作での棋譜作成
- **将棋ウォーズ連携**: 自動棋譜収集
- **局面検索**: 特定局面での検索

## 🚀 開発環境セットアップ

### 前提条件

- Python 3.9以上
- AWS CLI (設定済み)
- AWS SAM CLI

### ローカル開発

```bash
# リポジトリのクローン
git clone https://github.com/h-akira/ShogiProject.git
cd ShogiProject

# 依存関係のインストール
cd Lambda
pip install -r requirements.txt

# ローカルサーバー起動（3つのターミナルが必要）

# ターミナル1: SAM Local APIサーバー起動
sam local start-api --port 3000

# ターミナル2: 静的ファイルサーバー起動
wambda-admin.py static --port 8080

# ターミナル3: プロキシサーバー起動（統合エンドポイント）
wambda-admin.py proxy --proxy-port 8000

# ブラウザで http://localhost:8000 にアクセス

# テスト実行
cd Lambda
python lambda_function.py
```

### デプロイ

```bash
# SAMビルド
sam build

# デプロイ
sam deploy --guided

# 静的ファイルをS3に同期
aws s3 sync static/ s3://your-bucket/static/
```

## 📁 プロジェクト構造

```
ShogiProject/
├── Lambda/                     # メインアプリケーション
│   ├── lambda_function.py      # エントリーポイント
│   ├── project/               # 設定・ルーティング
│   ├── shogi/                 # 将棋ロジック
│   ├── accounts/              # 認証機能
│   ├── templates/             # HTMLテンプレート
│   └── requirements.txt       # Python依存関係
├── static/                    # 静的ファイル
│   ├── css/                  # スタイルシート
│   ├── js/                   # JavaScript
│   └── images/               # 画像ファイル
├── doc/                      # ドキュメント
│   └── table.md             # テーブル設計書
├── template.yaml             # SAM設定
└── samconfig.toml           # デプロイ設定
```

## 🤝 コントリビューション

1. Issueで機能要望・バグ報告
2. フォークしてフィーチャーブランチ作成
3. プルリクエスト送信

## 📄 ライセンス

MIT License

## 📞 サポート

- **Issues**: [GitHub Issues](https://github.com/h-akira/ShogiProject/issues)
- **作者**: h-akira
