import numpy as np
from hashlib import sha256
from typing import Dict, List, Tuple
from .naca6_data import NACA6_LIBRARY

# ---------- helpers ----------
def cosine_spacing(n: int) -> np.ndarray:
    beta = np.linspace(0.0, np.pi, n)
    return (1 - np.cos(beta)) / 2.0  # [0..1]

def thickness_4digit(x: np.ndarray, t: float, closed_te: bool = True) -> np.ndarray:
    # Classic 4-digit thickness formula
    # yt = 5 t [0.2969 sqrt(x) - 0.1260 x - 0.3516 x^2 + 0.2843 x^3 - k x^4]
    # k=0.1015 (open TE) or 0.1036 (closed TE)
    k = 0.1015 if closed_te else 0.1036
    yt = 5 * t * (0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - k*x**4)
    return yt

# ---------- NACA 4-digit ----------
def naca4_points(m: float, p: float, t: float, n: int = 200, closed_te: bool = True) -> Tuple[str, np.ndarray]:
    x = cosine_spacing(n)
    yt = thickness_4digit(x, t, closed_te=closed_te)

    if m == 0 and p == 0:
        yc = np.zeros_like(x)
        dyc_dx = np.zeros_like(x)
    else:
        yc = np.where(
            x < p,
            m/p**2 * (2*p*x - x**2),
            m/(1-p)**2 * ((1 - 2*p) + 2*p*x - x**2),
        )
        dyc_dx = np.where(
            x < p,
            2*m/p**2 * (p - x),
            2*m/(1-p)**2 * (p - x),
        )
    theta = np.arctan(dyc_dx)

    xu = x - yt*np.sin(theta)
    yu = yc + yt*np.cos(theta)
    xl = x + yt*np.sin(theta)
    yl = yc - yt*np.cos(theta)

    X = np.concatenate([xu[::-1], xl[1:]])
    Y = np.concatenate([yu[::-1], yl[1:]])
    pts = np.column_stack([X, Y])
    key = sha256(pts.tobytes()).hexdigest()
    return key, pts

# ---------- NACA 5-digit (standard mean line, design Cl_i=0.3) ----------
# Table from University of Cambridge "Aerodynamics for Students" (mean line 210..250)
# mean-line designation -> (p, m, k1)
FIVE_DIGIT_TABLE: Dict[float, Tuple[float, float]] = {
    # p : (m, k1)
    0.05: (0.0580, 361.4),
    0.10: (0.1260, 51.64),
    0.15: (0.2025, 15.957),
    0.20: (0.2900, 6.643),
    0.25: (0.3910, 3.230),
}
# Thickness uses the same 4-digit distribution
def naca5_standard_points(p_pos: float, t: float, n: int = 200, closed_te: bool = True) -> Tuple[str, np.ndarray]:
    if p_pos not in FIVE_DIGIT_TABLE:
        raise ValueError(f"Unsupported p (max camber position). Choose one of {list(FIVE_DIGIT_TABLE.keys())}")
    m, k1 = FIVE_DIGIT_TABLE[p_pos]
    x = cosine_spacing(n)
    yt = thickness_4digit(x, t, closed_te=closed_te)

    # piecewise mean line
    yc = np.where(
        x < m,
        (k1/6.0)*(x**3 - 3*m*x**2 + m**2*(3 - m)*x),
        (k1/6.0)*(m**3*(1 - x)),
    )
    dyc_dx = np.where(
        x < m,
        (k1/6.0)*(3*x**2 - 6*m*x + m**2*(3 - m)),
        -(k1/6.0)*(m**3),
    )
    theta = np.arctan(dyc_dx)

    xu = x - yt*np.sin(theta)
    yu = yc + yt*np.cos(theta)
    xl = x + yt*np.sin(theta)
    yl = yc - yt*np.cos(theta)

    X = np.concatenate([xu[::-1], xl[1:]])
    Y = np.concatenate([yu[::-1], yl[1:]])
    pts = np.column_stack([X, Y])
    key = sha256(pts.tobytes()).hexdigest()
    return key, pts

# ---------- NACA 6-series (symmetric) ----------
def naca6_symmetric_points(code: str, t: float, n: int = 200) -> Tuple[str, np.ndarray]:
    """
    Returns points for a symmetric NACA 6 or 6A family thickness distribution by
    scaling a stored base distribution to the requested thickness.
    Provide e.g., code="63A" or "63" or "64" and a base airfoil key in NACA6_LIBRARY.

    NOTE: 6-series are defined by mapping & prescribed pressure distribution.
    Standard practice is to use tabulated coords; other thickness values can
    be obtained by scaling/interpolation of the base distribution.  See docs. 
    """
    # pick a stored base (e.g., "63A010")
    # You can map different bases per family; here we try "code+010" first
    preferred = [f"{code}010", f"{code}-010", f"{code}0010"]
    base_key = next((k for k in preferred if k in NACA6_LIBRARY), None)
    if base_key is None:
        raise ValueError(f"No base shape found for {code}. Add coordinates to NACA6_LIBRARY.")
    base = np.asarray(NACA6_LIBRARY[base_key])  # Nx2, chord-normalized
    # base nominal thickness:
    base_t = np.max(base[:,1]) - np.min(base[:,1])
    scale = t / base_t if base_t > 0 else 1.0
    scaled = base.copy()
    scaled[:,1] *= scale

    key = sha256(scaled.tobytes()).hexdigest()
    return key, scaled