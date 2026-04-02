const SESSION_LABELS = {
    focus: "Focus session",
    short_break: "Short break",
    long_break: "Long break",
};

export function createInitialState(config) {
    return {
        mode: "focus",
        remainingSeconds: config.focus_seconds,
        totalSeconds: config.focus_seconds,
        isRunning: false,
        completedFocusSessions: 0,
        startedAt: null,
    };
}

export function getSessionLabel(mode) {
    return SESSION_LABELS[mode] ?? "Focus session";
}

export function formatTime(totalSeconds) {
    const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
    const seconds = String(totalSeconds % 60).padStart(2, "0");
    return `${minutes}:${seconds}`;
}

export function getProgress(state) {
    if (state.totalSeconds === 0) {
        return 0;
    }

    return state.remainingSeconds / state.totalSeconds;
}

export function startTimer(state) {
    if (state.isRunning) {
        return state;
    }

    return {
        ...state,
        isRunning: true,
        startedAt: state.startedAt ?? new Date(),
    };
}

export function pauseTimer(state) {
    return {
        ...state,
        isRunning: false,
    };
}

export function resetTimer(state, config) {
    return {
        ...state,
        isRunning: false,
        remainingSeconds: getDurationForMode(state.mode, config),
        totalSeconds: getDurationForMode(state.mode, config),
        startedAt: null,
    };
}

export function tick(state) {
    if (!state.isRunning || state.remainingSeconds <= 0) {
        return state;
    }

    return {
        ...state,
        remainingSeconds: state.remainingSeconds - 1,
    };
}

export function advanceSession(state, config) {
    const nextCompletedFocusSessions =
        state.mode === "focus"
            ? state.completedFocusSessions + 1
            : state.completedFocusSessions;

    let nextMode = "focus";
    if (state.mode === "focus") {
        nextMode =
            nextCompletedFocusSessions % config.sessions_before_long_break === 0
                ? "long_break"
                : "short_break";
    }

    const nextDuration = getDurationForMode(nextMode, config);

    return {
        mode: nextMode,
        remainingSeconds: nextDuration,
        totalSeconds: nextDuration,
        isRunning: false,
        completedFocusSessions: nextCompletedFocusSessions,
        startedAt: null,
    };
}

function getDurationForMode(mode, config) {
    if (mode === "short_break") {
        return config.short_break_seconds;
    }
    if (mode === "long_break") {
        return config.long_break_seconds;
    }
    return config.focus_seconds;
}