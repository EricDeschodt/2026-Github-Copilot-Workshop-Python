# API リファレンス

## 概要

PomodoroタイマーアプリのREST API仕様です。すべてのAPIエンドポイントは `/` 配下に提供されます。

---

## エンドポイント一覧

### `GET /`

**説明:** メインHTMLページを返します。

**レスポンス:** `text/html`（`index.html` テンプレート）

---

### `GET /api/config`

**説明:** タイマーの設定値（各セッションの秒数など）を返します。

**レスポンス:** `200 OK`

```json
{
  "focus_seconds": 1500,
  "short_break_seconds": 300,
  "long_break_seconds": 900,
  "sessions_before_long_break": 4
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| `focus_seconds` | `integer` | 集中セッションの秒数（デフォルト: 1500 = 25分）|
| `short_break_seconds` | `integer` | 短い休憩の秒数（デフォルト: 300 = 5分）|
| `long_break_seconds` | `integer` | 長い休憩の秒数（デフォルト: 900 = 15分）|
| `sessions_before_long_break` | `integer` | 長い休憩に入るまでの集中セッション数（デフォルト: 4）|

---

### `GET /api/stats/today`

**説明:** 本日（UTC）に完了した集中セッションの統計情報を返します。

**レスポンス:** `200 OK`

```json
{
  "sessions_completed": 3,
  "focus_minutes": 75,
  "current_streak": 3
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| `sessions_completed` | `integer` | 本日完了した集中セッション数 |
| `focus_minutes` | `integer` | 本日の集中時間の合計（分） |
| `current_streak` | `integer` | 連続完了セッション数（`sessions_completed` と同値）|

---

### `POST /api/sessions`

**説明:** 完了したセッションを記録します。フロントエンドは集中セッション完了時にこのAPIを呼び出します。

**リクエストヘッダー:**

```
Content-Type: application/json
```

**リクエストボディ:**

```json
{
  "session_type": "focus",
  "duration_seconds": 1500,
  "started_at": "2025-01-01T09:00:00+00:00",
  "completed_at": "2025-01-01T09:25:00+00:00"
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `session_type` | `string` | ✅ | セッション種別。`"focus"`, `"short_break"`, `"long_break"` のいずれか |
| `duration_seconds` | `integer` | ✅ | セッションの秒数 |
| `started_at` | `string` (ISO 8601) | ✅ | セッション開始日時 |
| `completed_at` | `string` (ISO 8601) | ✅ | セッション完了日時 |

**レスポンス:**

- `201 Created` — 保存成功

```json
{ "status": "created" }
```

- `400 Bad Request` — 必須フィールドが欠けている場合

```json
{ "error": "Missing required fields", "fields": ["completed_at", "started_at"] }
```

- `400 Bad Request` — `session_type` が無効な値の場合

```json
{ "error": "Invalid session_type" }
```

- `400 Bad Request` — 日時や数値のパースに失敗した場合

```json
{ "error": "Invalid session payload" }
```
