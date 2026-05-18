from fastapi import FastAPI

from procurement.adapters.persistence.sqlalchemy.db import init_db
from procurement.adapters.web.rest.routes import router
from procurement.config.logging import configure_logging

configure_logging()


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title='Procurement Service')
    app.include_router(router)
    return app


app = create_app()
