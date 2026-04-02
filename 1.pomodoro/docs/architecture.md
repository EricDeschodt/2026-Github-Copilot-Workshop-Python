# アーキテクチャ概要

## 技術スタック

| 区分 | 技術 |
|---|---|
| バックエンド | Python / Flask 3.x |
| データベース | SQLite（`instance/pomodoro.sqlite3`） |
| フロントエンド | バニラ JavaScript（ES Modules）|
| テンプレート | Jinja2 |
| テスト | pytest |

---

## レイヤー構成

```
app.py                          ← エントリーポイント
pomodoro_app/
├── __init__.py                 ← アプリケーションファクトリ (create_app)
├── routes.py                   ← Blueprint / HTTPルーティング
├── models.py                   ← データモデル (SessionRecord)
├── time_provider.py            ← 時刻取得の抽象化 (TimeProvider)
├── repositories/
│   └── session_repository.py  ← データアクセス層 (SQLite)
├── services/
│   ├── timer_service.py        ← TimerConfig（タイマー設定値）
│   └── stats_service.py       ← 統計計算ロジック
├── templates/
│   └── index.html              ← メインHTMLテンプレート
└── static/
    ├── css/styles.css          ← スタイルシート
    └── js/
        ├── app.js              ← エントリーポイント（ブートストラップ）
        ├── timer-core.js       ← タイマー状態管理（純粋関数）
        └── ui.js               ← DOM更新
```

---

## バックエンドの構成

### アプリケーションファクトリ (`create_app`)

`pomodoro_app/__init__.py` の `create_app()` 関数がアプリケーションを構築します。

- `instance/pomodoro.sqlite3` を自動作成
- `TimerConfig` をデフォルト設定で `app.config["TIMER_CONFIG"]` に登録
- `SessionRepository` と `TimeProvider` を `app.extensions` に登録
- `main_blueprint` を登録

### ルーティング層 (`routes.py`)

`Blueprint("main")` に3つのAPIエンドポイントと1つのHTMLエンドポイントを定義しています。リクエストのバリデーションはルート関数内で行います。

### リポジトリ層 (`repositories/session_repository.py`)

SQLiteを直接操作し、セッションの保存と本日のセッション一覧取得を担います。`TimeProvider` を依存注入し、テスト時に時刻を差し替え可能にしています。

### サービス層 (`services/`)

- `TimerConfig`: タイマー設定値を保持するイミュータブルなデータクラス
- `summarize_today()`: セッション一覧から統計情報（完了数・集中時間・ストリーク）を算出

---

## フロントエンドの構成

ES Modules を使用したバニラ JavaScript です。状態管理は純粋関数ベースで、DOMへの副作用は `ui.js` に集約しています。

```
app.js (エントリーポイント)
├── timer-core.js (状態管理・純粋関数)
└── ui.js (DOM更新)
```

起動時に `/api/config` と `/api/stats/today` を並行取得し、初期状態を構築します。集中セッション完了時のみ `/api/sessions` にPOSTして統計を更新します。

---

## データフロー

```
ブラウザ
  │  GET /api/config → タイマー設定を取得
  │  GET /api/stats/today → 本日の統計を取得
  │  [タイマー動作中] 1秒ごとに tick() で状態更新
  │  [集中セッション完了] POST /api/sessions → セッション保存
  │  GET /api/stats/today → 統計を再取得・画面更新
  │
Flask routes.py
  │  → SessionRepository.save() / list_today()
  │
SQLite (instance/pomodoro.sqlite3)
```
