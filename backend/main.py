from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import airfoil, reynolds

app = FastAPI(title="Airfoil Tools Enhanced API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(airfoil.router, prefix="/api/airfoil", tags=["airfoil"])
app.include_router(reynolds.router, prefix="/api/re", tags=["reynolds"])