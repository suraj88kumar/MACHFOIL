// frontend/js/reynolds.js
(function () {
  const API = window.API_BASE || "http://127.0.0.1:8000";

  const modeRadios = document.querySelectorAll('input[name="mode"]');
  const nuBlock = document.getElementById("nu_block");
  const rhomuBlock = document.getElementById("rhomu_block");
  const out = document.getElementById("re_out");

  function getNumber(id) {
    const v = document.getElementById(id).value;
    return Number(v);
  }

  // Toggle input blocks based on radio selection
  modeRadios.forEach((r) => {
    r.addEventListener("change", () => {
      const useNu = r.value === "nu" && r.checked;
      nuBlock.style.display = useNu ? "" : "none";
      rhomuBlock.style.display = useNu ? "none" : "";
    });
  });

  // Initial toggle (ensure correct visibility on load)
  (function initToggle() {
    const checked = [...modeRadios].find((x) => x.checked)?.value || "nu";
    nuBlock.style.display = checked === "nu" ? "" : "none";
    rhomuBlock.style.display = checked === "nu" ? "none" : "";
  })();

  async function computeRe() {
    const V = getNumber("re_V");
    const c = getNumber("re_c");
    const mode = [...modeRadios].find((x) => x.checked)?.value || "nu";

    if (!(V > 0) || !(c > 0)) {
      out.textContent = "Please enter positive values for V and c.";
      return;
    }

    let payload = { V, c };

    if (mode === "nu") {
      const nu = getNumber("re_nu");
      if (!(nu > 0)) {
        out.textContent = "Please enter a positive kinematic viscosity ν.";
        return;
      }
      payload.nu = nu;
    } else {
      const rho = getNumber("re_rho");
      const mu = getNumber("re_mu");
      if (!(rho > 0) || !(mu > 0)) {
        out.textContent = "Please enter positive values for ρ and μ.";
        return;
      }
      payload.rho = rho;
      payload.mu = mu;
    }

    try {
      const resp = await axios.post(`${API}/api/re/`, payload);
      if (resp.data && typeof resp.data.Re === "number") {
        out.textContent = `Re = ${resp.data.Re.toLocaleString()}`;
      } else if (resp.data?.error) {
        out.textContent = resp.data.error;
      } else {
        out.textContent = "Unexpected response from server.";
      }
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || "Request failed.";
      out.textContent = msg;
    }
  }

  document.getElementById("btn_re").addEventListener("click", computeRe);
})();