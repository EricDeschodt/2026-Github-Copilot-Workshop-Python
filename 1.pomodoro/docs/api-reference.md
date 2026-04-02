# API リファレンス

このドキュメントは、Pomodoro タイマーアプリケーションの REST API エンドポイントを説明します。

---

## エンドポイント一覧

| メソッド | パス | 説明 |
|--------|------|------|
| `GET` | `/` | メインページ（HTML）を返す |
| `GET` | `/api/config` | タイマー設定を返す |
| `GET` | `/api/stats/today` | 当日のセッション統計を返す |
| `POST` | `/api/sessions` | 完了セッションを保存する |

---

## `GET /`

HTMLテンプレート `index.html` をレンダリングして返します。

### レスポンス

- **ステータスコード**: `200 OK`
- **Content-Type**: `text/html`

---

## `GET /api/config`

タイマーの各フェーズの時間設定を返します。

### レスポンス

- **ステータスコード**: `200 OK`
- **Content-Type**: `application/json`

```json
{
  "focus_seconds": 1500,
  "short_break_seconds": 300,
  "long_break_seconds": 900,
  "sessions_before_long_break": 4
}
```

| フィールド | 型 | 説明 |
|----------|-----|------|
| `focus_seconds` | `integer` | 集中セッションの長さ（秒）。デフォルト: 1500 (25分) |
| `short_break_seconds` | `integer` | 短い休憩の長さ（秒）。デフォルト: 300 (5分) |
| `long_break_seconds` | `integer` | 長い休憩の長さ（秒）。デフォルト: 900 (15分) |
| `sessions_before_long_break` | `integer` | 長い休憩が入るまでの集中セッション数。デフォルト: 4 |

---

## `GET /api/stats/today`

当日（UTC）に完了した集中セッションの統計を返します。

### レスポンス

- **ステータスコード**: `200 OK`
- **Content-Type**: `application/json`

```json
{
  "sessions_completed": 3,
  "focus_minutes": 75,
  "current_streak": 3
}
```

| フィールド | 型 | 説明 |
|----------|-----|------|
| `sessions_completed` | `integer` | 当日に完了した集中セッション数 |
| `focus_minutes` | `integer` | 当日の合計集中時間（分） |
| `current_streak` | `integer` | 連続完了セッション数（現在は `sessions_completed` と同値） |

---

## `POST /api/sessions`

完了したセッションをデータベースに保存します。

### リクエスト

- **Content-Type**: `application/json`

```json
{
  "session_type": "focus",
  "duration_seconds": 1500,
  "started_at": "2026-04-02T09:00:00Z",
  "completed_at": "2026-04-02T09:25:00Z"
}
```

| フィールド | 型 | 必須 | 説明 |
|----------|-----|------|------|
| `session_type` | `string` | ✅ | セッション種別。`"focus"`, `"short_break"`, `"long_break"` のいずれか |
| `duration_seconds` | `integer` | ✅ | セッションの長さ（秒） |
| `started_at` | `string` (ISO 8601) | ✅ | セッション開始日時 |
| `completed_at` | `string` (ISO 8601) | ✅ | セッション完了日時 |

### レスポンス

#### 成功時

- **ステータスコード**: `201 Created`
- **Content-Type**: `application/json`

```json
{
  "status": "created"
}
```

#### エラー時

**必須フィールド欠落 (400)**

```json
{
  "error": "Missing required fields",
  "fields": ["completed_at", "started_at"]
}
```

**無効な `session_type` (400)**

```json
{
  "error": "Invalid session_type"
}
```

**無効なペイロード (400)**

```json
{
  "error": "Invalid session payload"
}
```
