# フロントエンドドキュメント

## 概要

バニラJavaScript（ES Modules）で実装されたSPAライクなPomodoro タイマーUIです。フレームワークを使用せず、状態管理は純粋関数、DOM操作は専用モジュールに分離しています。

---

## ファイル構成

```
pomodoro_app/static/
├── css/
│   └── styles.css       ← スタイルシート
├── img/
│   └── pomodoro.png     ← アイコン画像
└── js/
    ├── app.js           ← エントリーポイント（ブートストラップ・イベント処理）
    ├── timer-core.js    ← タイマー状態管理（純粋関数）
    └── ui.js            ← DOM更新
```

---

## `app.js` — エントリーポイント

`<script type="module">` で読み込まれるエントリーポイントです。アプリの起動、イベントバインド、タイマーインターバルの管理を担います。

### 起動フロー

1. `bootstrap()` を呼び出し
2. `/api/config` と `/api/stats/today` を並行取得
3. `createInitialState(config)` で初期状態を生成
4. `#start-pause-button` と `#reset-button` にイベントリスナーを登録
5. `renderApp(state, stats)` で初期画面を描画

### 主要な関数

| 関数 | 説明 |
|---|---|
| `bootstrap()` | アプリ起動処理（設定・統計取得、状態初期化、イベントバインド）|
| `toggleStartPause()` | 開始/一時停止ボタンのハンドラ |
| `handleReset()` | リセットボタンのハンドラ |
| `startInterval()` | 1秒間隔のタイマーを開始。`tick()` を呼び出し、残り0秒でセッション完了処理を行う |
| `stopInterval()` | タイマーインターバルを停止 |
| `fetchConfig()` | `GET /api/config` を呼び出す |
| `fetchStats()` | `GET /api/stats/today` を呼び出す |
| `saveCompletedSession(finishedState)` | `POST /api/sessions` で集中セッションを保存（集中セッション完了時のみ呼び出される）|

### セッション完了時の動作

`remainingSeconds === 0` になると:
1. インターバルを停止
2. セッション種別が `"focus"` の場合のみ `saveCompletedSession()` と `fetchStats()` を呼び出す
3. `advanceSession()` で次のセッションに自動遷移

---

## `timer-core.js` — タイマー状態管理

副作用を持たない純粋関数のみで構成されます。状態オブジェクトは不変（イミュータブル）で扱い、変更時は新しいオブジェクトを返します。

### 状態オブジェクト (`state`)

```javascript
{
    mode: "focus",               // "focus" | "short_break" | "long_break"
    remainingSeconds: 1500,      // 残り秒数
    totalSeconds: 1500,          // セッション全体の秒数
    isRunning: false,            // タイマー動作中フラグ
    completedFocusSessions: 0,   // 完了した集中セッション数（セッション遷移に使用）
    startedAt: null,             // Date | null（開始日時）
}
```

### エクスポートされる関数

| 関数 | シグネチャ | 説明 |
|---|---|---|
| `createInitialState` | `(config) → state` | 初期状態を生成。`mode` は `"focus"` |
| `startTimer` | `(state) → state` | タイマーを開始。`isRunning` を `true` にし、`startedAt` を現在時刻でセット |
| `pauseTimer` | `(state) → state` | タイマーを一時停止。`isRunning` を `false` に |
| `resetTimer` | `(state, config) → state` | 現在のモードのまま残り時間をリセット |
| `tick` | `(state) → state` | `remainingSeconds` を1減らす。停止中または0秒の場合はそのまま返す |
| `advanceSession` | `(state, config) → state` | 次のセッションに遷移。集中→短い休憩/長い休憩、休憩→集中 |
| `formatTime` | `(totalSeconds) → string` | 秒数を `"MM:SS"` 形式に変換（例: `"25:00"`）|
| `getProgress` | `(state) → number` | 進捗率を `0.0`〜`1.0` で返す（`remainingSeconds / totalSeconds`）|
| `getSessionLabel` | `(mode) → string` | モードを表示用テキストに変換（例: `"Focus session"`, `"Short break"`, `"Long break"`）|

### セッション遷移ロジック

```
集中セッション完了
  → completedFocusSessions % sessions_before_long_break === 0 の場合: long_break
  → それ以外: short_break

休憩セッション完了
  → focus
```

---

## `ui.js` — DOM更新

`renderApp(state, stats)` の1関数のみをエクスポートします。アプリの状態を受け取り、DOMを更新します。

### `renderApp(state, stats)`

| 更新対象 | セレクタ | 内容 |
|---|---|---|
| セッションラベル | `#session-label` | `getSessionLabel(state.mode)` の結果 |
| タイマー表示 | `#timer-display` | `formatTime(state.remainingSeconds)` の結果 |
| 進捗リング | `#progress-ring` | CSSカスタムプロパティ `--progress` を `getProgress(state)` で更新 |
| 開始/一時停止ボタン | `#start-pause-button` | `state.isRunning` が `true` の場合 `"Pause"`、`false` の場合 `"Start"` |
| 完了セッション数 | `#sessions-completed` | `stats.sessions_completed` |
| 集中時間 | `#focus-minutes` | `${stats.focus_minutes} min` |

`stats` が `null` または `undefined` の場合、統計表示は更新されません。

---

## `styles.css` — スタイルシート

CSSカスタムプロパティを使用したデザインシステムです。

### カラートークン

| 変数名 | 用途 |
|---|---|
| `--background-start` / `--background-end` | グラデーション背景 |
| `--card-background` | タイマーカードの背景 |
| `--panel-background` | 進捗パネルの背景 |
| `--text-strong` | メインテキスト |
| `--text-muted` | サブテキスト |
| `--accent` | アクセントカラー |
| `--accent-deep` | 深めのアクセントカラー |
| `--ring-track` | 進捗リングのトラック色 |

### 進捗リング

`#progress-ring` 要素の `--progress` CSSカスタムプロパティ（`0.0`〜`1.0`）を `ui.js` から動的に更新することで、残り時間に応じた円形プログレスバーを表現します。

---

## HTMLテンプレート (`index.html`)

| 要素ID | 説明 |
|---|---|
| `#session-label` | 現在のセッション種別ラベル |
| `#progress-ring` | 円形プログレスバー（`--progress` カスタムプロパティを持つ）|
| `#timer-display` | 残り時間表示（`MM:SS` 形式）|
| `#start-pause-button` | 開始/一時停止ボタン |
| `#reset-button` | リセットボタン |
| `#sessions-completed` | 本日の完了セッション数 |
| `#focus-minutes` | 本日の集中時間（分）|
