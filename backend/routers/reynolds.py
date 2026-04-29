from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional

router = APIRouter()

class ReReq(BaseModel):
    V: float          # velocity [m/s]
    c: float          # chord [m]
    rho: Optional[float] = None  # density [kg/m^3]
    mu: Optional[float] = None   # dynamic viscosity [Pa·s]
    nu: Optional[float] = None   # kinematic viscosity [m^2/s]

    @field_validator('V')
    @classmethod
    def validate_velocity(cls, v):
        """Velocity must be positive and within reasonable range."""
        if v <= 0:
            raise ValueError("Velocity must be positive (> 0 m/s)")
        if v > 500:  # Mach limits for subsonic/transonic regimes
            raise ValueError("Velocity is unreasonably high (> 500 m/s). Check your input.")
        return v

    @field_validator('c')
    @classmethod
    def validate_chord(cls, v):
        """Chord length must be positive and within reasonable range."""
        if v <= 0:
            raise ValueError("Chord must be positive (> 0 m)")
        if v > 100:
            raise ValueError("Chord is unreasonably large (> 100 m). Check your input.")
        return v

    @field_validator('rho')
    @classmethod
    def validate_rho(cls, v):
        """Density must be positive and within reasonable range."""
        if v is not None:
            if v <= 0:
                raise ValueError("Density must be positive (> 0 kg/m³)")
            if v > 1500:  # Beyond liquid water density
                raise ValueError("Density is unreasonably high (> 1500 kg/m³). Check your input.")
        return v

    @field_validator('mu')
    @classmethod
    def validate_mu(cls, v):
        """Dynamic viscosity must be positive and within reasonable range."""
        if v is not None:
            if v <= 0:
                raise ValueError("Dynamic viscosity must be positive (> 0 Pa·s)")
            if v > 1:
                raise ValueError("Dynamic viscosity is unreasonably high (> 1 Pa·s). Check your input.")
        return v

    @field_validator('nu')
    @classmethod
    def validate_nu(cls, v):
        """Kinematic viscosity must be positive and within reasonable range."""
        if v is not None:
            if v <= 0:
                raise ValueError("Kinematic viscosity must be positive (> 0 m²/s)")
            if v > 0.01:  # Beyond typical liquids
                raise ValueError("Kinematic viscosity is unreasonably high (> 0.01 m²/s). Check your input.")
        return v

@router.post("/")
def reynolds(req: ReReq):
    """
    Calculate Reynolds number (Re = ρVc/μ = Vc/ν).
    
    Accepts either:
    - nu (kinematic viscosity) [m²/s]
    - OR rho + mu (density + dynamic viscosity)
    
    Returns:
    - Re: Dimensionless Reynolds number
    - regime: Flow regime classification (laminar/transitional/turbulent)
    """
    try:
        # Calculate Reynolds number
        if req.nu is not None:
            Re = (req.V * req.c) / req.nu
        elif (req.rho is not None) and (req.mu is not None):
            Re = (req.rho * req.V * req.c) / req.mu
        else:
            raise HTTPException(
                status_code=400,
                detail="Provide either 'nu' (kinematic viscosity), or both 'rho' (density) and 'mu' (dynamic viscosity)"
            )
        
        # Classify flow regime
        if Re < 500_000:
            regime = "laminar"
        elif Re < 1_000_000:
            regime = "transitional"
        else:
            regime = "turbulent"
        
        return {
            "Re": round(Re, 2),
            "Re_scientific": f"{Re:.3e}",
            "regime": regime,
            "V": req.V,
            "c": req.c,
            "note": "High Re → inertial forces dominate; Low Re → viscous forces dominate"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
