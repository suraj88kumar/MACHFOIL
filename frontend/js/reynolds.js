// frontend/js/reynolds.js
const API = window.API_BASE || "http://127.0.0.1:8000";

// Mode toggle: ν vs ρ/μ
const modeRadios = document.querySelectorAll('input[name="mode"]');
const nuBlock = document.getElementById('nu_block');
const rhomuBlock = document.getElementById('rhomu_block');

modeRadios.forEach(r => {
  r.addEventListener('change', () => {
    const useNu = r.value === 'nu' && r.checked;
    nuBlock.style.display = useNu ? '' : 'none';
    rhomuBlock.style.display = useNu ? 'none' : '';
  });
});

// Temperature presets for kinematic viscosity
document.querySelectorAll('.preset').forEach(el => {
  el.addEventListener('click', () => {
    document.getElementById('re_nu').value = el.dataset.nu;
    window.setStatus(`✓ Preset: ν = ${el.dataset.nu} m²/s`, 'info');
  });
});

// Main Reynolds calculation
document.getElementById('btn_re')?.addEventListener('click', async () => {
  const V = parseFloat(document.getElementById('re_V').value);
  const c = parseFloat(document.getElementById('re_c').value);
  
  // Validate inputs
  if (!V || V <= 0 || V > 500) {
    window.setStatus('✗ Velocity must be 0 < V ≤ 500 m/s', 'error');
    return;
  }
  if (!c || c <= 0 || c > 100) {
    window.setStatus('✗ Chord must be 0 < c ≤ 100 m', 'error');
    return;
  }

  try {
    window.setStatus('Computing Reynolds number…', 'info');
    
    const mode = document.querySelector('input[name="mode"]:checked').value;
    let payload = { V, c };
    
    if (mode === 'nu') {
      const nu = parseFloat(document.getElementById('re_nu').value);
      if (!nu || nu <= 0) {
        window.setStatus('✗ Kinematic viscosity must be positive', 'error');
        return;
      }
      payload.nu = nu;
    } else {
      const rho = parseFloat(document.getElementById('re_rho').value);
      const mu = parseFloat(document.getElementById('re_mu').value);
      if (!rho || rho <= 0 || !mu || mu <= 0) {
        window.setStatus('✗ Density and viscosity must be positive', 'error');
        return;
      }
      payload.rho = rho;
      payload.mu = mu;
    }

    const { data } = await axios.post(`${API}/api/re/`, payload);
    
    // Display result
    const reOut = document.getElementById('re_out');
    const reRegime = document.getElementById('re_regime');
    
    reOut.textContent = `Re = ${data.Re.toLocaleString()}`;
    
    const regimeClass = `regime-${data.regime}`;
    reRegime.innerHTML = `<div class="regime-badge ${regimeClass}">${data.regime.toUpperCase()}</div>`;
    
    window.setStatus(`✓ Re = ${data.Re_scientific} (${data.regime})`, 'success');
  } catch (err) {
    console.error('Reynolds API error:', err);
    const errMsg = err?.response?.data?.detail || err?.message || 'Request failed';
    window.setStatus(`✗ ${errMsg}`, 'error');
  }
});

// Enter key to compute
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
    e.preventDefault();
    document.getElementById('btn_re')?.click();
  }
});

// Clear results
document.getElementById('btn_clear_re')?.addEventListener('click', () => {
  document.getElementById('re_out').textContent = 'Re = —';
  document.getElementById('re_regime').innerHTML = '';
  window.setStatus('', ''); // Hide status
});
