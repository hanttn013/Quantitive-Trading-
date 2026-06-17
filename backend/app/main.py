from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .errors import install_error_handlers
from .routes import context, copilot, dashboard, data, market, operations, research, trading
from .settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin, "http://localhost:8080", "http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health", tags=["system"])
    def health() -> dict[str, object]:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "ok",
            "providers": {
                "deepseek": settings.deepseek_status,
                "mt5": "mock",
                "discord": "mock",
                "tradingview": "mock",
            },
        }

    install_error_handlers(app)

    app.include_router(context.router)
    app.include_router(dashboard.router)
    app.include_router(trading.router)
    app.include_router(research.router)
    app.include_router(market.router)
    app.include_router(operations.router)
    app.include_router(copilot.router)
    app.include_router(data.router)

    return app


app = create_app()
