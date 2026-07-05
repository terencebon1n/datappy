import asyncio
import secrets
import time

from fastapi import Depends, HTTPException, Response, WebSocket, WebSocketDisconnect, status
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
async def logout() -> Response:
    # Called via fetch() from the admin frontend: a redirect here would be
    # followed cross-origin by the browser and fail CORS.
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("admin_session")
    return response


@admin_router.websocket("/status")
async def ws_status(websocket: WebSocket) -> None:
    token = websocket.cookies.get("admin_session")
    try:
        session = session_manager.decode(token) if token else None
    except ValueError:
        session = None
    if session is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    refresh = asyncio.Event()

    async def monitor_connection() -> None:
        try:
            while True:
                await websocket.receive_text()
                refresh.set()
        except WebSocketDisconnect:
            return

    async def produce_updates() -> None:
        last_data: list[ManagedProcess] | None = None
        last_sent_at = 0.0
        while True:
            data = await asyncio.to_thread(process_manager.get_all_status)

            now = time.monotonic()
            if (
                data != last_data
                or now - last_sent_at >= settings.admin.status_keepalive_seconds
            ):
                await websocket.send_json([process.model_dump() for process in data])
                last_data = data
                last_sent_at = now

            try:
                await asyncio.wait_for(
                    refresh.wait(),
                    timeout=settings.admin.status_poll_interval_seconds,
                )
            except asyncio.TimeoutError:
                pass
            refresh.clear()

    tasks = [
        asyncio.create_task(produce_updates()),
        asyncio.create_task(monitor_connection()),
    ]

    _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass


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
