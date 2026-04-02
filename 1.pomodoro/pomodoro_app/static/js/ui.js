import { formatTime, getProgress, getSessionLabel } from "./timer-core.js";

const COLOR_BLUE = [109, 121, 242];
const COLOR_YELLOW = [245, 196, 0];
const COLOR_RED = [239, 68, 68];

function lerpChannel(a, b, t) {
    return Math.round(a + (b - a) * t);
}

function getTimerColor(progress) {
    let r, g, b;
    if (progress > 0.5) {
        const t = (1.0 - progress) * 2;
        r = lerpChannel(COLOR_BLUE[0], COLOR_YELLOW[0], t);
        g = lerpChannel(COLOR_BLUE[1], COLOR_YELLOW[1], t);
        b = lerpChannel(COLOR_BLUE[2], COLOR_YELLOW[2], t);
    } else {
        const t = (0.5 - progress) * 2;
        r = lerpChannel(COLOR_YELLOW[0], COLOR_RED[0], t);
        g = lerpChannel(COLOR_YELLOW[1], COLOR_RED[1], t);
        b = lerpChannel(COLOR_YELLOW[2], COLOR_RED[2], t);
    }
    return `rgb(${r},${g},${b})`;
}

export function renderApp(state, stats) {
    document.querySelector("#session-label").textContent = getSessionLabel(state.mode);
    document.querySelector("#timer-display").textContent = formatTime(state.remainingSeconds);

    const progress = getProgress(state);
    const ring = document.querySelector("#progress-ring");
    ring.style.setProperty("--progress", progress);
    ring.style.setProperty("--ring-active-color", getTimerColor(progress));

    document.querySelector("#start-pause-button").textContent = state.isRunning ? "Pause" : "Start";

    if (stats) {
        document.querySelector("#sessions-completed").textContent = String(stats.sessions_completed);
        document.querySelector("#focus-minutes").textContent = `${stats.focus_minutes} min`;
    }
}