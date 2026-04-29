// frontend/js/airfoil.js
const API = window.API_BASE || "http://127.0.0.1:8000";
const svg = document.getElementById("foil_svg");
let lastPoints = [];

async function callAPI(url, payload) {
  try {
    window.setStatus("Generating airfoil…", "info");
    const { data } = await axios.post(url, payload);
    if (!data?.points?.length) throw new Error("API returned no points.");
    lastPoints = data.points;
    window.drawAirfoil(lastPoints, svg);
    window.setStatus(`✓ Generated ${lastPoints.length} points`, "success");
  } catch (err) {
    console.error("Airfoil API error:", err);
    const errMsg = err?.response?.data?.detail || err?.message || "Request failed";
    window.setStatus(`✗ ${errMsg}`, "error");
  }
}

// 4-digit
document.getElementById("btn_naca4")?.addEventListener("click", async () => {
  const m = parseFloat(document.getElementById("n4_m").value);
  const p = parseFloat(document.getElementById("n4_p").value);
  const t = parseFloat(document.getElementById("n4_t").value);
  const n = parseInt(document.getElementById("n4_n").value, 10);
  const closed_te = document.getElementById("n4_te").checked;

  if (!(n > 10) || !(t > 0) || !(p >= 0) || !(m >= 0)) {
    return window.setStatus("✗ Please enter valid numeric inputs.", "error");
  }
  await callAPI(`${API}/api/airfoil/naca4`, { m, p, t, n, closed_te });
});

// 5-digit
document.getElementById("btn_naca5")?.addEventListener("click", async () => {
  const p_pos = parseFloat(document.getElementById("n5_p").value);
  const t = parseFloat(document.getElementById("n5_t").value);
  const n = parseInt(document.getElementById("n5_n").value, 10);
  const closed_te = document.getElementById("n5_te").checked;
  await callAPI(`${API}/api/airfoil/naca5`, { p_pos, t, n, closed_te });
});

// 6-series
document.getElementById("btn_naca6")?.addEventListener("click", async () => {
  const family = document.getElementById("n6_family").value;
  const t = parseFloat(document.getElementById("n6_t").value);
  await callAPI(`${API}/api/airfoil/naca6`, { family, t, n: 200 });
});

// Download
document.getElementById("btn_download")?.addEventListener("click", () => {
  if (!lastPoints.length) {
    window.setStatus("✗ Generate an airfoil first.", "error");
    return;
  }
  const text = lastPoints.map(([x, y]) => `${x.toFixed(6)} ${y.toFixed(6)}`).join("\n");
  const blob = new Blob([text], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "airfoil.dat";
  a.click();
  URL.revokeObjectURL(a.href);
  window.setStatus("✓ Downloaded airfoil.dat", "success");
});
