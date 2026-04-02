# フロントエンドドキュメント

このドキュメントは、Pomodoro タイマーアプリケーションのフロントエンド実装を説明します。

---

## 概要

フロントエンドは vanilla JavaScript（ES Modules 形式）で実装されています。フレームワークは使用せず、3 つのモジュールに分割されています。

```
static/js/
├── app.js          # エントリーポイント・オーケストレーター
├── timer-core.js   # タイマー状態管理（純粋関数）
└── ui.js           # DOM レンダリング
```

---

## `timer-core.js`

タイマーの状態管理ロジックを純粋関数として実装したモジュールです。副作用を持たず、すべての関数は入力から出力を計算して返します。

### エクスポートされる関数

#### `createInitialState(config)`

タイマーの初期状態を生成します。

```javascript
createInitialState(config)
// => { mode, remainingSeconds, totalSeconds, isRunning, completedFocusSessions, startedAt }
```

**引数**: `config` — `/api/config` から取得したタイマー設定オブジェクト

**戻り値**: 初期状態オブジェクト

| フィールド | 説明 |
|----------|------|
| `mode` | 現在のセッション種別 (`"focus"` で初期化) |
| `remainingSeconds` | 残り秒数 |
| `totalSeconds` | 現在モードの合計秒数 |
| `isRunning` | タイマー実行中かどうか (`false` で初期化) |
| `completedFocusSessions` | 完了した集中セッション数 (`0` で初期化) |
| `startedAt` | セッション開始時刻 (`null` で初期化) |

---

#### `getSessionLabel(mode)`

セッション種別の表示ラベルを返します。

```javascript
getSessionLabel("focus")       // => "Focus session"
getSessionLabel("short_break") // => "Short break"
getSessionLabel("long_break")  // => "Long break"
getSessionLabel("unknown")     // => "Focus session" (フォールバック)
```

---

#### `formatTime(totalSeconds)`

秒数を `MM:SS` 形式の文字列に変換します。

```javascript
formatTime(1500) // => "25:00"
formatTime(65)   // => "01:05"
```

---

#### `getProgress(state)`

タイマーの進捗率（0〜1）を返します。

```javascript
getProgress({ totalSeconds: 1500, remainingSeconds: 750 }) // => 0.5
getProgress({ totalSeconds: 0, remainingSeconds: 0 })      // => 0
```

---

#### `startTimer(state)`

タイマーを開始した新しい状態を返します。すでに実行中の場合は状態を変更しません。

```javascript
startTimer(state)
// => { ...state, isRunning: true, startedAt: Date }
```

`startedAt` が `null` の場合は現在時刻が設定されます。既に設定済みの場合はそのまま保持されます。

---

#### `pauseTimer(state)`

タイマーを一時停止した新しい状態を返します。

```javascript
pauseTimer(state)
// => { ...state, isRunning: false }
```

---

#### `resetTimer(state, config)`

タイマーを現在のモードの初期秒数にリセットした新しい状態を返します。

```javascript
resetTimer(state, config)
// => { ...state, isRunning: false, remainingSeconds: <mode duration>, totalSeconds: <mode duration>, startedAt: null }
```

---

#### `tick(state)`

タイマーを1秒進めた新しい状態を返します。タイマーが実行中でない場合、または残り時間が0の場合は状態を変更しません。

```javascript
tick(state)
// => { ...state, remainingSeconds: state.remainingSeconds - 1 }
```

---

#### `advanceSession(state, config)`

現在のセッションを完了して次のセッションへ移行した新しい状態を返します。

セッション遷移ルール:
- `focus` → `completedFocusSessions` が `sessions_before_long_break` の倍数なら `long_break`、それ以外は `short_break`
- `short_break` または `long_break` → `focus`

```javascript
advanceSession(state, config)
// => { mode, remainingSeconds, totalSeconds, isRunning: false, completedFocusSessions, startedAt: null }
```

---

## `ui.js`

DOM 更新ロジックを担当するモジュールです。`timer-core.js` の関数を使用して UI をレンダリングします。

### エクスポートされる関数

#### `renderApp(state, stats)`

アプリケーション全体の UI を現在の状態と統計情報に基づいて更新します。

```javascript
renderApp(state, stats)
```

**更新される DOM 要素**:

| セレクター | 内容 |
|----------|------|
| `#session-label` | セッション種別ラベル (`getSessionLabel(state.mode)`) |
| `#timer-display` | タイマー表示 (`formatTime(state.remainingSeconds)`) |
| `#progress-ring` | CSS カスタムプロパティ `--progress` (`getProgress(state)`) |
| `#start-pause-button` | ボタンテキスト（実行中: `"Pause"`, 停止中: `"Start"`） |
| `#sessions-completed` | 当日完了セッション数（`stats` が存在する場合のみ） |
| `#focus-minutes` | 当日集中時間（`stats` が存在する場合のみ、例: `"75 min"`） |

---

## `app.js`

アプリケーションのエントリーポイントです。`timer-core.js` と `ui.js` を組み合わせてアプリケーション全体を制御します。

### 動作フロー

1. **初期化** (`bootstrap()`): `/api/config` と `/api/stats/today` を並列で取得し、初期状態を生成して UI をレンダリングします
2. **イベントバインド** (`bindEvents()`): ボタンのクリックイベントを設定します
3. **タイマー制御**: `setInterval` (1000ms) で `tick()` を呼び出してカウントダウンします
4. **セッション完了**: 残り時間が0になった時点でインターバルを停止し、集中セッションの場合は `/api/sessions` に保存後、次のセッションへ移行します

### グローバル変数

| 変数 | 説明 |
|-----|------|
| `timerId` | `setInterval` のタイマーID |
| `config` | `/api/config` から取得した設定 |
| `state` | 現在のタイマー状態 |
| `stats` | 当日の統計情報 |

### API 通信

| 関数 | メソッド | エンドポイント | 説明 |
|-----|--------|------------|------|
| `fetchConfig()` | `GET` | `/api/config` | タイマー設定を取得 |
| `fetchStats()` | `GET` | `/api/stats/today` | 当日の統計を取得 |
| `saveCompletedSession(finishedState)` | `POST` | `/api/sessions` | 完了した集中セッションを保存 |

`saveCompletedSession()` は、`finishedState.startedAt` が `null` の場合、`completedAt - totalSeconds` から開始時刻を算出します。

---

## HTML テンプレート (`index.html`)

アプリケーションのメイン HTML ページです。

### 主要 DOM 要素

| ID | 要素 | 説明 |
|----|------|------|
| `#session-label` | `<p>` | 現在のセッション種別ラベル |
| `#timer-display` | `<strong>` | タイマー表示（`MM:SS` 形式） |
| `#progress-ring` | `<div>` | 進捗リング（CSS カスタムプロパティ `--progress` で制御） |
| `#start-pause-button` | `<button>` | スタート/一時停止ボタン |
| `#reset-button` | `<button>` | リセットボタン |
| `#sessions-completed` | `<strong>` | 当日完了セッション数 |
| `#focus-minutes` | `<strong>` | 当日集中時間 |

JavaScript は `<script type="module">` タグで `app.js` を読み込みます。
