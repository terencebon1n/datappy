import secrets

from fastapi import Depends, HTTPException
from fastapi.responses import RedirectResponse

from src.api.dependencies import (
    auth_service,
    google_oauth,
    process_manager,
    require_admin_session,
    session_manager,
)
from src.api.v1.router import admin_router
from src.domain.admin.process import ManagedProcess, ManagedServiceType
from src.domain.admin.session import AdminSession
from src.domain.gtfs_rt.enums import City
from src.infrastructure.config import settings


@admin_router.get("/login")
async def login() -> RedirectResponse:
    return RedirectResponse(google_oauth.get_login_url(state=secrets.token_urlsafe(16)))


@admin_router.get("/callback")
async def callback(code: str) -> RedirectResponse:
    try:
        email = await google_oauth.exchange_code(code)
    except Exception:
        raise HTTPException(status_code=400, detail="OAuth exchange failed")

    try:
        session = auth_service.authorize(email)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")

    token = session_manager.encode(session)
    redirect = RedirectResponse(url=settings.admin.frontend_url)
    redirect.set_cookie("admin_session", token, httponly=True, samesite="lax")
    return redirect


@admin_router.get("/logout")
async def logout() -> RedirectResponse:
    response = RedirectResponse(url=settings.admin.frontend_url)
    response.delete_cookie("admin_session")
    return response


@admin_router.get("/status")
async def get_status(
    _: AdminSession = Depends(require_admin_session),
) -> list[ManagedProcess]:
    return process_manager.get_all_status()


@admin_router.post("/{service}/{city}/start")
async def start_service(
    service: ManagedServiceType,
    city: City,
    _: AdminSession = Depends(require_admin_session),
) -> ManagedProcess:
    try:
        return process_manager.start(service, city)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.post("/{service}/{city}/stop")
async def stop_service(
    service: ManagedServiceType,
    city: City,
    _: AdminSession = Depends(require_admin_session),
) -> None:
    try:
        process_manager.stop(service, city)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
