from __future__ import annotations

import ipaddress

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import Settings

settings = Settings.from_env()
app = FastAPI(title="GhostShell Local API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def require_loopback(request: Request, call_next):
    peer = request.client.host if request.client else ""
    host = request.headers.get("host", "").split(":", 1)[0].strip("[]")
    try:
        is_local = ipaddress.ip_address(peer).is_loopback and host.casefold() in {
            "localhost", "127.0.0.1", "::1",
        }
    except ValueError:
        is_local = False
    if not is_local:
        return JSONResponse(status_code=403, content={"detail": "The local GhostShell API is loopback-only."})
    return await call_next(request)


app.include_router(router)
