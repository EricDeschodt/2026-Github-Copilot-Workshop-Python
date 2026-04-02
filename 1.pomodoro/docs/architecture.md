# アーキテクチャ概要

このドキュメントは、Pomodoro タイマーアプリケーションの現在のアーキテクチャを説明します。

---

## 全体構成

アプリケーションは Flask ベースのウェブアプリケーションです。バックエンドは Python、フロントエンドは vanilla JavaScript（ES Modules）で実装されています。

```
1.pomodoro/
├── app.py                    # エントリーポイント（Flask アプリ起動）
├── requirements.txt          # Python 依存関係
├── pomodoro_app/             # アプリケーションパッケージ
│   ├── __init__.py           # アプリケーションファクトリ (create_app)
│   ├── models.py             # データモデル
│   ├── time_provider.py      # 時刻プロバイダー（テスト差し替え用）
│   ├── repositories/         # データアクセス層
│   │   ├── __init__.py
│   │   └── session_repository.py
│   ├── services/             # ビジネスロジック層
│   │   ├── __init__.py
│   │   ├── stats_service.py
│   │   └── timer_service.py
│   ├── routes.py             # REST API エンドポイント
│   ├── static/               # 静的ファイル
│   │   ├── css/styles.css
│   │   ├── img/pomodoro.png
│   │   └── js/
│   │       ├── app.js        # フロントエンドエントリーポイント
│   │       ├── timer-core.js # タイマーロジック（純粋関数）
│   │       └── ui.js         # UI レンダリング
│   └── templates/
│       └── index.html        # メインページテンプレート
└── tests/                    # テストスイート
    ├── conftest.py
    ├── frontend/
    ├── integration/
    └── unit/
```

---

## レイヤー構成

### 1. アプリケーションファクトリ (`pomodoro_app/__init__.py`)

`create_app()` 関数が Flask アプリケーションを生成します。

- SQLite データベースのパスを `instance/pomodoro.sqlite3` に設定します
- `TimerConfig` をアプリ設定 (`TIMER_CONFIG`) に登録します
- `TimeProvider` と `SessionRepository` を `app.extensions` に登録します
- `main_blueprint` を登録します

### 2. データアクセス層（リポジトリパターン）

`SessionRepository` クラスが SQLite を直接操作してセッションデータを永続化します。

- `_initialize()`: `sessions` テーブルを作成（未存在時）
- `list_today()`: 当日完了したセッションを取得
- `save()`: 新しいセッションを保存

`TimeProvider` を依存注入として受け取り、現在時刻の取得をテスト時に差し替え可能にしています。

### 3. サービス層（ビジネスロジック）

- **`TimerConfig`** (`timer_service.py`): タイマー設定値を保持するイミュータブルなデータクラス
- **`summarize_today()`** (`stats_service.py`): セッションリストから当日の統計情報を計算する純粋関数
- **`calculate_focus_minutes()`** (`stats_service.py`): 完了した集中セッションの合計時間（分）を計算する純粋関数

### 4. ルーター層 (`routes.py`)

Flask の `Blueprint` を使用して REST API エンドポイントを定義します。

- `GET /api/config`: `TimerConfig` を JSON で返す
- `GET /api/stats/today`: `SessionRepository` と `summarize_today()` を組み合わせて統計を返す
- `POST /api/sessions`: リクエストを検証して `SessionRecord` を生成し `SessionRepository.save()` で保存する

### 5. フロントエンド層

ES Modules 形式の vanilla JavaScript で実装されています。詳細は [`frontend.md`](./frontend.md) を参照してください。

---

## データフロー

```
ブラウザ
  │
  ├─ GET /               → index.html を返す
  │
  ├─ GET /api/config     → TimerConfig → JSON
  │
  ├─ GET /api/stats/today → SessionRepository.list_today()
  │                          → summarize_today() → JSON
  │
  └─ POST /api/sessions  → バリデーション → SessionRecord
                            → SessionRepository.save() → 201
```

---

## 永続化

SQLite を使用してセッションデータを永続化します。データベースファイルは `instance/pomodoro.sqlite3` に配置されます。

スキーマは [`data-models.md`](./data-models.md) を参照してください。

---

## テスト戦略

```
tests/
├── unit/           # 単体テスト（モデル、サービス、リポジトリ）
├── integration/    # 統合テスト（Flask テストクライアント使用）
└── frontend/       # フロントエンドテスト
```

`conftest.py` でインメモリ SQLite を使用したテスト用アプリを構成しています。
