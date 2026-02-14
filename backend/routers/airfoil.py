from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from services.geom import naca4_points, naca5_standard_points, naca6_symmetric_points

router = APIRouter()

class Naca4Req(BaseModel):
    m: float  # e.g., 0.02 for '2'
    p: float  # e.g., 0.4  for '4'
    t: float  # e.g., 0.12 for '12'
    n: int = 200
    closed_te: bool = True

@router.post("/naca4")
def naca4(req: Naca4Req):
    key, pts = naca4_points(req.m, req.p, req.t, req.n, req.closed_te)
    return {"id": key, "points": pts.tolist()}

class Naca5Req(BaseModel):
    # standard 5-digit mean line positions: 0.05, 0.10, 0.15, 0.20, 0.25
    p_pos: float  # 0.05..0.25
    t: float      # thickness ratio (e.g., 0.12)
    n: int = 200
    closed_te: bool = True

@router.post("/naca5")
def naca5(req: Naca5Req):
    try:
        key, pts = naca5_standard_points(req.p_pos, req.t, req.n, req.closed_te)
        return {"id": key, "points": pts.tolist()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class Naca6Req(BaseModel):
    family: Literal["63", "63A", "64", "64A", "65", "65A", "66", "67"]
    t: float      # thickness ratio (e.g., 0.12)
    n: int = 200

@router.post("/naca6")
def naca6(req: Naca6Req):
    # symmetric only; camber lines for 6-series are advanced -> dataset approach
    try:
        key, pts = naca6_symmetric_points(req.family, req.t, req.n)
        return {"id": key, "points": pts.tolist()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))