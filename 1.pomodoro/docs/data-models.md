# データモデル仕様

## `SessionRecord`

**ファイル:** `pomodoro_app/models.py`

セッション（集中・休憩）の記録を表すデータクラスです。

```python
@dataclass(slots=True)
class SessionRecord:
    session_type: str
    duration_seconds: int
    started_at: datetime
    completed_at: datetime | None = None
```

### フィールド

| フィールド | 型 | 説明 |
|---|---|---|
| `session_type` | `str` | セッション種別。`"focus"`, `"short_break"`, `"long_break"` のいずれか |
| `duration_seconds` | `int` | セッションの長さ（秒） |
| `started_at` | `datetime` | セッション開始日時 |
| `completed_at` | `datetime \| None` | セッション完了日時。`None` の場合は未完了 |

### プロパティ

| プロパティ | 型 | 説明 |
|---|---|---|
| `is_completed` | `bool` | `completed_at is not None` の場合 `True` |

---

## `TimerConfig`

**ファイル:** `pomodoro_app/services/timer_service.py`

タイマー設定値を保持するイミュータブルなデータクラスです。アプリ起動時に `app.config["TIMER_CONFIG"]` に登録されます。

```python
@dataclass(frozen=True, slots=True)
class TimerConfig:
    focus_seconds: int = 25 * 60        # 1500
    short_break_seconds: int = 5 * 60   # 300
    long_break_seconds: int = 15 * 60   # 900
    sessions_before_long_break: int = 4
```

### フィールド

| フィールド | 型 | デフォルト値 | 説明 |
|---|---|---|---|
| `focus_seconds` | `int` | `1500` | 集中セッションの秒数（25分）|
| `short_break_seconds` | `int` | `300` | 短い休憩の秒数（5分）|
| `long_break_seconds` | `int` | `900` | 長い休憩の秒数（15分）|
| `sessions_before_long_break` | `int` | `4` | 長い休憩に入るまでの集中セッション数 |

---

## SQLite スキーマ

**データベース:** `instance/pomodoro.sqlite3`（アプリ起動時に自動作成）

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_type TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT
);
```

### カラム

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | 自動採番ID |
| `session_type` | `TEXT` | NOT NULL | セッション種別 |
| `duration_seconds` | `INTEGER` | NOT NULL | セッションの秒数 |
| `started_at` | `TEXT` | NOT NULL | 開始日時（ISO 8601 UTC形式）|
| `completed_at` | `TEXT` | — | 完了日時（ISO 8601 UTC形式）。`NULL` の場合は未完了 |

日時はUTCのISO 8601形式（例: `2025-01-01T09:00:00+00:00`）で保存されます。

---

## 統計サマリ

**ファイル:** `pomodoro_app/services/stats_service.py`

`summarize_today()` 関数が返すdict形式のデータです。

| フィールド | 型 | 説明 |
|---|---|---|
| `sessions_completed` | `int` | 当日に完了した集中セッション数 |
| `focus_minutes` | `int` | 当日の集中時間合計（分、端数切り捨て）|
| `current_streak` | `int` | 連続完了セッション数（`sessions_completed` と同値）|
