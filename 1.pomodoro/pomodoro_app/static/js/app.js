import {
	advanceSession,
	createInitialState,
	pauseTimer,
	resetTimer,
	startTimer,
	tick,
} from "./timer-core.js";
import { renderApp } from "./ui.js";

let timerId = null;
let config = null;
let state = null;
let stats = null;

async function bootstrap() {
	[config, stats] = await Promise.all([fetchConfig(), fetchStats()]);
	state = createInitialState(config);
	bindEvents();
	renderApp(state, stats);
}

function bindEvents() {
	document.querySelector("#start-pause-button").addEventListener("click", toggleStartPause);
	document.querySelector("#reset-button").addEventListener("click", handleReset);
}

function toggleStartPause() {
	state = state.isRunning ? pauseTimer(state) : startTimer(state);

	if (state.isRunning) {
		startInterval();
	} else {
		stopInterval();
	}

	renderApp(state, stats);
}

function handleReset() {
	stopInterval();
	state = resetTimer(state, config);
	renderApp(state, stats);
}

function startInterval() {
	stopInterval();
	timerId = window.setInterval(async () => {
		state = tick(state);

		if (state.remainingSeconds === 0) {
			stopInterval();
			const finishedState = state;

			if (finishedState.mode === "focus") {
				await saveCompletedSession(finishedState);
				stats = await fetchStats();
			}

			state = advanceSession(finishedState, config);
		}

		renderApp(state, stats);
	}, 1000);
}

function stopInterval() {
	if (timerId !== null) {
		window.clearInterval(timerId);
		timerId = null;
	}
}

async function fetchConfig() {
	const response = await fetch("/api/config");
	return response.json();
}

async function fetchStats() {
	const response = await fetch("/api/stats/today");
	return response.json();
}

async function saveCompletedSession(finishedState) {
	const completedAt = new Date();
	const startedAt =
		finishedState.startedAt ?? new Date(completedAt.getTime() - finishedState.totalSeconds * 1000);

	await fetch("/api/sessions", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			session_type: finishedState.mode,
			duration_seconds: finishedState.totalSeconds,
			started_at: startedAt.toISOString(),
			completed_at: completedAt.toISOString(),
		}),
	});
}

bootstrap();