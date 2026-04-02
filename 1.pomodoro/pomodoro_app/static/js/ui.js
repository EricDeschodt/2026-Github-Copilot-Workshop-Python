import { formatTime, getProgress, getSessionLabel } from "./timer-core.js";

export function renderApp(state, stats, gamification) {
    document.querySelector("#session-label").textContent = getSessionLabel(state.mode);
    document.querySelector("#timer-display").textContent = formatTime(state.remainingSeconds);
    document.querySelector("#progress-ring").style.setProperty("--progress", getProgress(state));
    document.querySelector("#start-pause-button").textContent = state.isRunning ? "Pause" : "Start";

    if (stats) {
        document.querySelector("#sessions-completed").textContent = String(stats.sessions_completed);
        document.querySelector("#focus-minutes").textContent = `${stats.focus_minutes} min`;
    }

    if (gamification) {
        renderGamification(gamification);
    }
}

function renderGamification(gamification) {
    const { xp, level, xp_for_next_level, streak, achievements } = gamification;
    const xpProgressInCurrentLevel = 100 - xp_for_next_level;
    const xpProgress = `${xpProgressInCurrentLevel}%`;

    document.querySelector("#level-badge").textContent = `Lv ${level}`;
    document.querySelector("#xp-label").textContent = `${xp} XP`;
    document.querySelector("#streak-badge").textContent = `🔥 ${streak}`;
    document.querySelector("#xp-bar-fill").style.setProperty("--xp-progress", xpProgress);
    document.querySelector("#xp-next").textContent =
        xp_for_next_level === 100
            ? `Level ${level} — complete Pomodoros to earn XP`
            : `${xp_for_next_level} XP to level ${level + 1}`;

    renderAchievements(achievements);
}

function renderAchievements(achievements) {
    const grid = document.querySelector("#achievements-grid");
    if (!grid) return;

    grid.innerHTML = "";
    for (const achievement of achievements) {
        const badge = document.createElement("div");
        badge.className = `achievement-badge${achievement.unlocked ? " achievement-badge--unlocked" : ""}`;
        badge.title = achievement.description;
        badge.setAttribute("aria-label", `${achievement.name}: ${achievement.description}${achievement.unlocked ? " (unlocked)" : " (locked)"}`);
        badge.innerHTML = `
            <span class="achievement-icon">${achievement.unlocked ? "🏆" : "🔒"}</span>
            <span class="achievement-name">${achievement.name}</span>
        `;
        grid.appendChild(badge);
    }
}

export async function renderWeeklyChart() {
    const chartEl = document.querySelector("#weekly-chart");
    if (!chartEl) return;

    const response = await fetch("/api/stats/weekly");
    const { days } = await response.json();

    const maxSessions = Math.max(...days.map((d) => d.sessions_completed), 1);
    const chartHeight = 64;
    const dayLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

    chartEl.innerHTML = "";
    days.forEach((day, index) => {
        const barHeightPx = Math.max(4, (day.sessions_completed / maxSessions) * chartHeight);
        const dayDate = new Date(day.date + "T00:00:00Z");
        const dayName = dayLabels[dayDate.getUTCDay() === 0 ? 6 : dayDate.getUTCDay() - 1];
        const isToday = day.date === new Date().toISOString().slice(0, 10);

        const wrapper = document.createElement("div");
        wrapper.className = "bar-chart__bar-wrapper";

        const bar = document.createElement("div");
        bar.className = `bar-chart__bar${isToday ? " bar-chart__bar--active" : ""}`;
        bar.style.height = `${barHeightPx}px`;
        bar.title = `${day.date}: ${day.sessions_completed} session${day.sessions_completed !== 1 ? "s" : ""}`;

        const label = document.createElement("span");
        label.className = "bar-chart__label";
        label.textContent = dayName;

        wrapper.appendChild(bar);
        wrapper.appendChild(label);
        chartEl.appendChild(wrapper);
    });
}