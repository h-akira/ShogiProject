# テーブル定義書

ShogiProjectではDynamoDBのSingle Table Designを採用し、1つのテーブルで全てのデータを管理しています。

## 🏗️ 設計方針

### Single Table Designの採用理由

- **パフォーマンス**: 複雑なJOINクエリを避けてレスポンス時間を最適化
- **コスト効率**: テーブル数を削減してDynamoDB課金を最小化
- **スケーラビリティ**: アクセスパターンに最適化されたデータ配置

### キー設計戦略

データ種別をプレフィックスで識別し、効率的なクエリパターンを実現：

- `kifu#uname#<username>` - ユーザー別棋譜管理
- `tag#uname#<username>` - ユーザー別タグ管理
- `analysis#<id>` - AI解析結果
- `users#<username>` - ユーザー設定

## 🔍 インデックス設計

**共通キー（プライマリキー）**: 全アイテムが必須で持つ属性
- `pk` (String): Partition Key - データ種別とオーナーを識別
- `sk` (String): Sort Key - 個別アイテムIDや補助情報を格納

### SwapIndex (GSI)
- **Partition Key**: `sk`, **Sort Key**: `pk`
- **Projection**: ALL
- **目的**: ID逆引き検索・一意性制約
- **用途**:
  - シェアコードから棋譜取得
  - タグが付いた棋譜一覧
  - ユーザーのアクセス権限確認

### CommonGSI (GSI)
- **Partition Key**: `cgsi_pk`, **Sort Key**: `sk`
- **Projection**: ALL
- **目的**: 共有・グループ化データアクセス
- **用途**:
  - 共有棋譜アクセス
  - ユーザーの解析一覧

### CommonLSI (LSI)
- **Partition Key**: `pk`, **Sort Key**: `clsi_sk`
- **Projection**: INCLUDE (`cgsi_pk`, `clsi_sk`)
- **目的**: 名前・スラグ検索
- **用途**:
  - カスタムURL検索
  - タグ名検索・重複チェック

### CreatedIndex (LSI)
- **Partition Key**: `pk`, **Sort Key**: `created`
- **Projection**: INCLUDE (`cgsi_pk`, `clsi_sk`, `share`)
- **目的**: 作成日時順ソート
- **用途**: 棋譜・タグの作成日時順リスト表示

### LatestAccessIndex (LSI)
- **Partition Key**: `pk`, **Sort Key**: `latest_access`
- **Projection**: INCLUDE (`cgsi_pk`, `clsi_sk`, `share`)
- **目的**: アクセス日時順ソート
- **用途**: よくアクセスされる棋譜の表示

### LatestUpdateIndex (LSI)
- **Partition Key**: `pk`, **Sort Key**: `latest_update`
- **Projection**: INCLUDE (`cgsi_pk`, `clsi_sk`, `share`)
- **目的**: 更新日時順ソート
- **用途**: 最近更新された棋譜の表示

## 📋 エンティティ一覧

DynamoDBの特性上、各エンティティ（アイテム）は異なる属性セットを持ちます。以下は主要なエンティティタイプとその属性構成です。

### 1. 棋譜エンティティ
**キーパターン**: `pk=kifu#uname#<username>`, `sk=kid#<kifu_id>`

| 属性名 | データ型 | 説明 |
|-------|---------|------|
| `cgsi_pk` | String | `kifu#scode#<share_code>` |
| `clsi_sk` | String | `slug#<custom_slug>` |
| `kifu` | String | 棋譜データ (KIF/KI2形式) |
| `first_or_second` | String | 先手/後手 (`first`/`second`) |
| `result` | String | 対局結果 (`win`/`lose`/`draw`/`sennichite`) |
| `memo` | String | 棋譜メモ・コメント |
| `public` | Boolean | 公開設定 |
| `share` | Boolean | 共有可能設定 |
| `created` | String | 作成日時 (ISO 8601) |
| `latest_access` | String | 最終アクセス日時 |
| `latest_update` | String | 最終更新日時 |

### 2. ユーザー設定エンティティ
**キーパターン**: `pk=users`, `sk=uname#<username>`

| 属性名 | データ型 | 説明 |
|-------|---------|------|
| `kifu_max` | Number | ユーザーの棋譜最大ID |
| `tag_max` | Number | ユーザーのタグ最大ID |

### 3. システム設定エンティティ
**キーパターン**: `pk=system`, `sk=none`

| 属性名 | データ型 | 説明 |
|-------|---------|------|
| `kifu_max` | Number | システム全体の棋譜最大ID |
| `tag_max` | Number | システム全体のタグ最大ID |

### 4. タグ定義エンティティ
**キーパターン**: `pk=tag#uname#<username>`, `sk=tid#<tag_id>`

| 属性名 | データ型 | 説明 |
|-------|---------|------|
| `clsi_sk` | String | `tname#<tag_name>` |
| `created` | String | 作成日時 (ISO 8601) |
| `latest_access` | String | 最終アクセス日時 |
| `latest_update` | String | 最終更新日時 |

### 5. 棋譜-タグ関連付けエンティティ
**キーパターン**: `pk=tag#kid#<kifu_id>`, `sk=tid#<tag_id>`

*共通属性のみ*

### 6. 棋譜アクセス権限エンティティ
**キーパターン**: `pk=kallowed#kid#<kifu_id>`, `sk=uname#<username>`

*共通属性のみ*

### 7. ユーザー全体アクセス権限エンティティ
**キーパターン**: `pk=uallowed#uname#<username>`, `sk=uname#<allowed_username>`

*共通属性のみ*

### 8. AI解析結果エンティティ
**キーパターン**: `pk=analysis`, `sk=aid#<analysis_id>`

| 属性名 | データ型 | 説明 |
|-------|---------|------|
| `cgsi_pk` | String | `analysis#uname#<username>` |
| `created` | String | 作成日時 (ISO 8601) |
| `status` | String | 解析ステータス (`waiting`/`succeeded`/`error`) |
| `response` | String | 解析結果・エラー詳細 |
| `expired` | Number | TTL (Unix timestamp) |

## 📊 データパターン例

### 1. 棋譜データ
```json
{
  "pk": "kifu#uname#h-akira",
  "sk": "kid#fdsaj9d9s0",
  "cgsi_pk": "kifu#scode#lkihofkwif4tF",
  "clsi_sk": "slug#社団戦/2025/鈴木",
  "kifu": "手合割：平手\n先手：...",
  "first_or_second": "first",
  "result": "sennichite",
  "memo": "序盤研究用の棋譜",
  "public": true,
  "share": true,
  "created": "2025-12-31T11:11:31Z",
  "latest_access": "2025-12-31T11:11:31Z",
  "latest_update": "2025-12-31T11:11:31Z"
}
```

### 2. ユーザー設定
```json
{
  "pk": "users",
  "sk": "uname#h-akira",
  "kifu_max": 3000,
  "tag_max": 50
}
```

### 3. システム設定
```json
{
  "pk": "system",
  "sk": "none",
  "kifu_max": 3000,
  "tag_max": 50
}
```

### 4. タグ定義
```json
{
  "pk": "tag#uname#h-akira",
  "sk": "tid#jko2kdl",
  "clsi_sk": "tname#四間飛車",
  "created": "2025-12-31T11:11:31Z",
  "latest_access": "2025-12-31T11:11:31Z",
  "latest_update": "2025-12-31T11:11:31Z"
}
```

### 5. 棋譜-タグ関連付け
```json
{
  "pk": "tag#kid#fdsaj9d9s1",
  "sk": "tid#jko2kdl"
}
```

### 6. 棋譜アクセス権限
```json
{
  "pk": "kallowed#kid#fdsaj9d9s1",
  "sk": "uname#h-akira2"
}
```

### 7. ユーザー全体アクセス権限
```json
{
  "pk": "uallowed#uname#h-akira",
  "sk": "uname#h-akira2"
}
```

### 8. AI解析結果
```json
{
  "pk": "analysis",
  "sk": "aid#fdjsklfadf",
  "cgsi_pk": "analysis#uname#h-akira",
  "created": "2025-12-31T11:11:31Z",
  "status": "succeeded",
  "response": "{\"moves\": [...], \"evaluation\": [...]}",
  "expired": 1234567890
}
```

## 🔧 主なクエリパターン

### 1. ユーザーの棋譜一覧取得
```python
# 作成日時順
response = table.query(
    IndexName='CreatedIndex',
    KeyConditionExpression=Key('pk').eq('kifu#uname#h-akira')
)
```

### 2. 共有棋譜の取得
```python
# シェアコードから取得
response = table.query(
    IndexName='SwapIndex',
    KeyConditionExpression=Key('sk').eq('kifu#scode#ABC123')
)
```

### 3. タグ検索
```python
# タグ名での検索
response = table.query(
    IndexName='CommonLSI',
    KeyConditionExpression=Key('pk').eq('tag#uname#h-akira') &
                          Key('clsi_sk').begins_with('tname#四間飛車')
)
```

### 4. 解析状況確認
```python
# ユーザーの解析リスト
response = table.query(
    IndexName='CommonGSI',
    KeyConditionExpression=Key('cgsi_pk').eq('analysis#uname#h-akira')
)
```

## ⚡ パフォーマンス考慮事項

### スケーラビリティ対策

1. **Partition分散**: 将来的にユーザー数増加時は、ユーザー名のハッシュ値でPartitionを分散
2. **Hot Partition回避**: アクセス頻度の高いデータは適切に分散配置
3. **バッチ処理**: 大量データ処理時はDynamoDB StreamsやETLパイプライン活用

### 最適化ポイント

- **Project Type**: 必要な属性のみをインデックスに含めてコスト削減
- **TTL活用**: 解析結果などの一時データは自動削除
- **Consistent Read**: 強整合性が必要なケースでのみ使用

## 🔄 データマイグレーション

新機能追加時のテーブル拡張戦略：

1. **後方互換性**: 既存データ構造を維持
2. **段階的移行**: 新旧データ形式の並行運用
3. **バージョニング**: データスキーマのバージョン管理

---

**注意**: 本設計は現在のアクセスパターンに最適化されており、要件変更時は適宜見直しが必要です。