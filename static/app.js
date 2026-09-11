"use strict";

const uiToken = document.querySelector('meta[name="ui-token"]').content;
const uiHeaders = { "X-UI-Token": uiToken };

function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.style.display = "block";
  window.setTimeout(() => { toast.style.display = "none"; }, 2600);
}

function setBadge(status) {
  const badge = document.getElementById("badge");
  badge.textContent = status;
  const kind = status === "ONLINE" ? "online" : status === "STOPPED" ? "stopped" : status === "ERROR" ? "error" : "working";
  badge.className = `badge ${kind}`;
}

function render(state) {
  setBadge(state.status);
  document.getElementById("detail").textContent = state.detail;
  document.getElementById("url").textContent = state.url || "Waiting for Pinggy URL…";
  document.getElementById("curl").textContent = state.curl_command || "Start the tunnel to generate the command.";
  document.getElementById("permission-status").textContent = state.sms_permission ? "Granted" : "Not granted";
  document.getElementById("start").disabled = state.service_running;
  document.getElementById("stop").disabled = !state.service_running;
  document.getElementById("copy").disabled = !state.curl_command;
  document.getElementById("share").disabled = !state.curl_command;

  const logs = document.getElementById("logs");
  logs.innerHTML = "";
  (state.logs.length ? state.logs : ["No activity yet."]).forEach((entry) => {
    const item = document.createElement("li");
    item.textContent = entry;
    logs.appendChild(item);
  });
}

async function refreshState() {
  try {
    const response = await fetch(`/ui/state?t=${Date.now()}`, { headers: uiHeaders, cache: "no-store" });
    if (!response.ok) throw new Error("Dashboard refresh failed");
    render(await response.json());
  } catch (error) {
    showToast(error.message);
  }
}

async function post(path) {
  const response = await fetch(path, { method: "POST", headers: uiHeaders });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || "Action failed");
  showToast(data.message || "Done");
  await refreshState();
}

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", async () => {
    try { await post(`/ui/service/${button.dataset.action}`); }
    catch (error) { showToast(error.message); }
  });
});

document.getElementById("permission").addEventListener("click", async () => {
  try { await post("/ui/permission/request"); }
  catch (error) { showToast(error.message); }
});

document.getElementById("copy").addEventListener("click", async () => {
  try { await post("/ui/curl/copy"); }
  catch (error) { showToast(error.message); }
});

document.getElementById("share").addEventListener("click", async () => {
  try { await post("/ui/curl/share"); }
  catch (error) { showToast(error.message); }
});

refreshState();
window.setInterval(refreshState, 4000);
