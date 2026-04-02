import { formatTime, getProgress, getSessionLabel } from "./timer-core.js";

export function renderApp(state, stats) {
    document.querySelector("#session-label").textContent = getSessionLabel(state.mode);
    document.querySelector("#timer-display").textContent = formatTime(state.remainingSeconds);
    document.querySelector("#progress-ring").style.setProperty("--progress", getProgress(state));
    document.querySelector("#start-pause-button").textContent = state.isRunning ? "Pause" : "Start";

    if (stats) {
        document.querySelector("#sessions-completed").textContent = String(stats.sessions_completed);
        document.querySelector("#focus-minutes").textContent = `${stats.focus_minutes} min`;
    }
}