// ── State ──────────────────────────────────────────────────────────────────
let lights = [];
let selectedMac = null;
let mode = "white"; // 'white' | 'rgb'
let sendTimer = null;

// ── iro.js color wheel ────────────────────────────────────────────────────
const colorPicker = new iro.ColorPicker("#color-wheel", {
  width: 220,
  color: "#ff9900",
  layout: [{ component: iro.ui.Wheel }],
});

colorPicker.on("color:change", () => {
  if (selectedMac && mode === "rgb") scheduleSend();
});

// ── Helpers ───────────────────────────────────────────────────────────────
async function api(method, path, body) {
  const res = await fetch(path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// Debounce BLE sends so dragging sliders doesn't flood the device
function scheduleSend() {
  clearTimeout(sendTimer);
  sendTimer = setTimeout(sendCurrent, 80);
}

async function sendCurrent() {
  if (!selectedMac) return;
  try {
    if (mode === "white") {
      const kelvin = parseInt(document.getElementById("kelvin-slider").value);
      await api("POST", `/lights/${selectedMac}/temperature`, { kelvin });
    } else {
      const { r, g, b } = colorPicker.color.rgb;
      await api("POST", `/lights/${selectedMac}/color`, { r, g, b });
    }
    const intensity =
      parseInt(document.getElementById("intensity-slider").value) / 100;
    await api("POST", `/lights/${selectedMac}/intensity`, { value: intensity });
  } catch (e) {
    console.error("Send error:", e.message);
  }
}

// ── Render light list ─────────────────────────────────────────────────────
function renderLights() {
  const list = document.getElementById("light-list");
  list.innerHTML = "";
  if (lights.length === 0) {
    list.innerHTML =
      '<div style="color:#555;font-size:0.8rem">No lights found.</div>';
    return;
  }
  for (const light of lights) {
    const card = document.createElement("div");
    card.className =
      "light-card" + (light.mac === selectedMac ? " selected" : "");
    card.innerHTML = `
      <div class="light-card-header">
        <span class="light-mac">${light.mac}</span>
        <span class="badge ${light.connected ? "connected" : "disconnected"}">
          ${light.connected ? "on" : "off"}
        </span>
      </div>
      <button class="connect-btn ${
        light.connected ? "do-disconnect" : "do-connect"
      }">
        ${light.connected ? "Disconnect" : "Connect"}
      </button>
    `;
    card.querySelector(".connect-btn").addEventListener("click", async (e) => {
      e.stopPropagation();
      const btn = e.currentTarget;
      btn.disabled = true;
      try {
        if (light.connected) {
          await api("POST", `/lights/${light.mac}/disconnect`);
          if (selectedMac === light.mac) showPlaceholder();
        } else {
          await api("POST", `/lights/${light.mac}/connect`);
          selectLight(light.mac);
        }
        await refreshLights();
      } catch (err) {
        alert(err.message);
        btn.disabled = false;
      }
    });
    card.addEventListener("click", () => {
      if (light.connected) selectLight(light.mac);
    });
    list.appendChild(card);
  }
}

// ── Light selection ───────────────────────────────────────────────────────
function selectLight(mac) {
  selectedMac = mac;
  document.getElementById("placeholder").style.display = "none";
  document.getElementById("controls").style.display = "flex";
  document.getElementById("selected-mac").textContent = mac;
  renderLights();
}

function showPlaceholder() {
  selectedMac = null;
  document.getElementById("placeholder").style.display = "";
  document.getElementById("controls").style.display = "none";
  renderLights();
}

// ── Refresh lights from server ────────────────────────────────────────────
async function refreshLights() {
  const data = await api("GET", "/lights");
  lights = data.lights;
  // If selected light disconnected externally, go back to placeholder
  if (selectedMac && !lights.find((l) => l.mac === selectedMac)?.connected) {
    showPlaceholder();
  } else {
    renderLights();
  }
}

// ── Discover ──────────────────────────────────────────────────────────────
document.getElementById("discover-btn").addEventListener("click", async () => {
  const btn = document.getElementById("discover-btn");
  const spinner = document.getElementById("spinner");
  btn.disabled = true;
  spinner.style.display = "block";
  try {
    const data = await api("POST", "/lights/discover");
    lights = data.lights;
    renderLights();
  } catch (e) {
    alert("Discovery failed: " + e.message);
  } finally {
    btn.disabled = false;
    spinner.style.display = "none";
  }
});

// ── Mode toggle ───────────────────────────────────────────────────────────
document.querySelectorAll(".mode-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    mode = btn.dataset.mode;
    document
      .querySelectorAll(".mode-btn")
      .forEach((b) => b.classList.toggle("active", b === btn));
    document
      .getElementById("white-panel")
      .classList.toggle("visible", mode === "white");
    document
      .getElementById("rgb-panel")
      .classList.toggle("visible", mode === "rgb");
    if (selectedMac) scheduleSend();
  });
});

// ── Sliders ───────────────────────────────────────────────────────────────
document.getElementById("kelvin-slider").addEventListener("input", (e) => {
  document.getElementById("kelvin-val").textContent = e.target.value + " K";
  if (selectedMac) scheduleSend();
});

document.getElementById("intensity-slider").addEventListener("input", (e) => {
  document.getElementById("intensity-val").textContent = e.target.value + "%";
  if (selectedMac) scheduleSend();
});

// ── Power off ─────────────────────────────────────────────────────────────
document.getElementById("power-off-btn").addEventListener("click", async () => {
  if (!selectedMac) return;
  await api("POST", `/lights/${selectedMac}/power_off`);
});

// ── Init ──────────────────────────────────────────────────────────────────
refreshLights();
setInterval(refreshLights, 3000);
