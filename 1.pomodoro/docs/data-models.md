# データモデル仕様

このドキュメントは、Pomodoro タイマーアプリケーションで使用されるデータモデルを説明します。

---

## Python データモデル

### `SessionRecord`

**ファイル**: `pomodoro_app/models.py`

完了または進行中のポモドーロセッションを表すデータクラスです。

```python
@dataclass(slots=True)
class SessionRecord:
    session_type: str
    duration_seconds: int
    started_at: datetime
    completed_at: datetime | None = None
```

| フィールド | 型 | 説明 |
|----------|-----|------|
| `session_type` | `str` | セッション種別。`"focus"`, `"short_break"`, `"long_break"` のいずれか |
| `duration_seconds` | `int` | セッションの長さ（秒） |
| `started_at` | `datetime` | セッション開始日時 |
| `completed_at` | `datetime \| None` | セッション完了日時。`None` の場合はセッション未完了 |

#### プロパティ

| プロパティ | 型 | 説明 |
|----------|-----|------|
| `is_completed` | `bool` | `completed_at` が `None` でない場合に `True` を返す |

---

### `TimerConfig`

**ファイル**: `pomodoro_app/services/timer_service.py`

タイマーの各フェーズの時間設定を保持するイミュータブルなデータクラスです。

```python
@dataclass(frozen=True, slots=True)
class TimerConfig:
    focus_seconds: int = 25 * 60        # 1500
    short_break_seconds: int = 5 * 60   # 300
    long_break_seconds: int = 15 * 60   # 900
    sessions_before_long_break: int = 4
```

| フィールド | 型 | デフォルト値 | 説明 |
|----------|-----|------------|------|
| `focus_seconds` | `int` | `1500` (25分) | 集中セッションの長さ（秒） |
| `short_break_seconds` | `int` | `300` (5分) | 短い休憩の長さ（秒） |
| `long_break_seconds` | `int` | `900` (15分) | 長い休憩の長さ（秒） |
| `sessions_before_long_break` | `int` | `4` | 長い休憩が入るまでの集中セッション数 |

このクラスは `frozen=True` のため、インスタンス生成後に変更できません。

---

## データベーススキーマ

**データベース**: SQLite  
**ファイルパス**: `instance/pomodoro.sqlite3`

### `sessions` テーブル

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_type TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT
)
```

| カラム | 型 | 制約 | 説明 |
|------|-----|------|------|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | 自動採番の主キー |
| `session_type` | `TEXT` | `NOT NULL` | セッション種別 (`"focus"`, `"short_break"`, `"long_break"`) |
| `duration_seconds` | `INTEGER` | `NOT NULL` | セッションの長さ（秒） |
| `started_at` | `TEXT` | `NOT NULL` | 開始日時（ISO 8601 形式、UTC） |
| `completed_at` | `TEXT` | nullable | 完了日時（ISO 8601 形式、UTC）。`NULL` の場合は未完了 |

#### 注意事項

- 日時は UTC タイムゾーンの ISO 8601 形式文字列として保存されます
- `list_today()` では `completed_at` が `NULL` でないレコードのみ取得します
- 当日の範囲は UTC 基準の00:00:00〜翌00:00:00です

---

## セッション種別

| 値 | 説明 |
|----|------|
| `"focus"` | 集中セッション（デフォルト: 25分） |
| `"short_break"` | 短い休憩（デフォルト: 5分） |
| `"long_break"` | 長い休憩（デフォルト: 15分） |
