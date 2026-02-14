from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ReReq(BaseModel):
    V: float          # velocity [m/s]
    c: float          # chord [m]
    rho: Optional[float] = None  # density [kg/m^3]
    mu: Optional[float] = None   # dynamic viscosity [Pa·s]
    nu: Optional[float] = None   # kinematic viscosity [m^2/s]

@router.post("/")
def reynolds(req: ReReq):
    if req.nu is not None:
        Re = (req.V * req.c) / req.nu
    elif (req.rho is not None) and (req.mu is not None):
        Re = (req.rho * req.V * req.c) / req.mu
    else:
        return {"error": "Provide either nu, or rho and mu"}
    return {"Re": Re}