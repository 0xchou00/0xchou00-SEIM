const state = {
  apiKey: localStorage.getItem("0xchou00_api_key") || "",
  refreshTimer: null,
};

const elements = {
  apiKeyInput: document.getElementById("api-key-input"),
  saveKeyButton: document.getElementById("save-key-button"),
  severityFilter: document.getElementById("severity-filter"),
  sourceFilter: document.getElementById("source-filter"),
  timeFilter: document.getElementById("time-filter"),
  refreshFilter: document.getElementById("refresh-filter"),
  connectionBadge: document.getElementById("connection-badge"),
  lastUpdated: document.getElementById("last-updated"),
  alertsCount: document.getElementById("alerts-count"),
  logsCount: document.getElementById("logs-count"),
  urgentCount: document.getElementById("urgent-count"),
  topSource: document.getElementById("top-source"),
  alertsList: document.getElementById("alerts-list"),
  logsList: document.getElementById("logs-list"),
  alertsEmpty: document.getElementById("alerts-empty"),
  logsEmpty: document.getElementById("logs-empty"),
  alertsMeta: document.getElementById("alerts-meta"),
  logsMeta: document.getElementById("logs-meta"),
};

function bootDashboard() {
  elements.apiKeyInput.value = state.apiKey;
  elements.saveKeyButton.addEventListener("click", handleConnect);
  elements.severityFilter.addEventListener("change", restartPolling);
  elements.sourceFilter.addEventListener("change", restartPolling);
  elements.timeFilter.addEventListener("change", restartPolling);
  elements.refreshFilter.addEventListener("change", restartPolling);

  if (state.apiKey) {
    restartPolling();
  }
}

function handleConnect() {
  const apiKey = elements.apiKeyInput.value.trim();
  if (!apiKey) {
    setConnectionState("error", "MISSING KEY");
    elements.lastUpdated.textContent = "enter a valid X-API-Key";
    return;
  }

  state.apiKey = apiKey;
  localStorage.setItem("0xchou00_api_key", apiKey);
  restartPolling();
}

function restartPolling() {
  clearRefreshTimer();
  refreshDashboard();
  state.refreshTimer = window.setInterval(refreshDashboard, Number(elements.refreshFilter.value));
}

function clearRefreshTimer() {
  if (state.refreshTimer) {
    window.clearInterval(state.refreshTimer);
    state.refreshTimer = null;
  }
}

async function refreshDashboard() {
  if (!state.apiKey) {
    return;
  }

  setConnectionState("warn", "POLLING");

  const alertsParams = new URLSearchParams({
    limit: "100",
    since_minutes: elements.timeFilter.value,
  });

  if (elements.severityFilter.value) {
    alertsParams.set("severity", elements.severityFilter.value);
  }

  if (elements.sourceFilter.value) {
    alertsParams.set("source_type", elements.sourceFilter.value);
  }

  const logsParams = new URLSearchParams({
    limit: "100",
    since_minutes: elements.timeFilter.value,
  });

  if (elements.sourceFilter.value) {
    logsParams.set("source_type", elements.sourceFilter.value);
  }

  try {
    const [alertsResponse, logsResponse] = await Promise.all([
      apiGet(`/alerts?${alertsParams.toString()}`),
      apiGet(`/logs?${logsParams.toString()}`),
    ]);

    renderAlerts(alertsResponse.items || []);
    renderLogs(logsResponse.items || []);
    updateSummary(alertsResponse.items || [], logsResponse.items || []);
    setConnectionState("ok", "LIVE");
    elements.lastUpdated.textContent = `last poll ${new Date().toLocaleTimeString()}`;
  } catch (error) {
    setConnectionState("error", "ERROR");
    elements.lastUpdated.textContent = error.message;
  }
}

async function apiGet(path) {
  const response = await fetch(path, {
    headers: {
      "X-API-Key": state.apiKey,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `request failed with status ${response.status}`);
  }

  return response.json();
}

function updateSummary(alerts, logs) {
  elements.alertsCount.textContent = String(alerts.length);
  elements.logsCount.textContent = String(logs.length);
  elements.urgentCount.textContent = String(
    alerts.filter((item) => ["critical", "high"].includes((item.severity || "").toLowerCase())).length
  );

  const counts = [...alerts, ...logs].reduce((accumulator, item) => {
    const source = item.source_type || "unknown";
    accumulator[source] = (accumulator[source] || 0) + 1;
    return accumulator;
  }, {});

  const topSource = Object.entries(counts).sort((left, right) => right[1] - left[1])[0];
  elements.topSource.textContent = topSource ? `${topSource[0]}:${topSource[1]}` : "n/a";
}

function renderAlerts(alerts) {
  elements.alertsMeta.textContent = `${alerts.length} visible`;
  elements.alertsEmpty.classList.toggle("hidden", alerts.length > 0);
  elements.alertsList.innerHTML = alerts.map((alert) => {
    const severity = normalizeSeverity(alert.severity);
    return `
      <article class="list-item">
        <div class="list-item-header">
          <div class="item-tags">
            <span class="severity-pill severity-${severity}">${severity}</span>
            <span class="source-pill">${escapeHtml(alert.source_type || "unknown")}</span>
          </div>
          <span class="muted">${formatTimestamp(alert.created_at)}</span>
        </div>
        <h3 class="item-title">${escapeHtml(alert.title || "alert")}</h3>
        <p class="item-description">${escapeHtml(alert.description || "no description")}</p>
        <div class="item-meta">
          <span>detector:${escapeHtml(alert.detector || "n/a")}</span>
          <span>src:${escapeHtml(alert.source_ip || "n/a")}</span>
          <span>count:${escapeHtml(String(alert.event_count || 0))}</span>
        </div>
      </article>
    `;
  }).join("");
}

function renderLogs(logs) {
  elements.logsMeta.textContent = `${logs.length} visible`;
  elements.logsEmpty.classList.toggle("hidden", logs.length > 0);
  elements.logsList.innerHTML = logs.map((log) => {
    const severity = normalizeSeverity(log.severity);
    const normalized = log.normalized || {};
    return `
      <article class="list-item">
        <div class="list-item-header">
          <div class="item-tags">
            <span class="severity-pill severity-${severity}">${severity}</span>
            <span class="source-pill">${escapeHtml(log.source_type || "unknown")}</span>
          </div>
          <span class="muted">${formatTimestamp(log.created_at)}</span>
        </div>
        <h3 class="item-title">${escapeHtml(log.event_type || "event")}</h3>
        <p class="item-description">${escapeHtml(log.raw_message || "")}</p>
        <div class="item-meta">
          <span>ip:${escapeHtml(log.source_ip || "n/a")}</span>
          <span>user:${escapeHtml(log.username || normalized.username || "n/a")}</span>
            <span>status:${escapeHtml(String(normalized.status || normalized.http_status || "n/a"))}</span>
            <span>country:${escapeHtml(log.country || normalized.country || "n/a")}</span>
            <span>mal:${escapeHtml(String(log.is_malicious ?? normalized.is_malicious ?? false))}</span>
          </div>
        </article>
      `;
  }).join("");
}

function setConnectionState(kind, label) {
  elements.connectionBadge.textContent = label;
  elements.connectionBadge.className = `badge badge-${kind}`;
}

function normalizeSeverity(severity) {
  const normalized = (severity || "info").toLowerCase();
  return ["critical", "high", "medium", "low", "info"].includes(normalized) ? normalized : "info";
}

function formatTimestamp(value) {
  if (!value) {
    return "unknown";
  }

  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

bootDashboard();
