from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes.cards import router as cards_router
from app.api.routes.cashback import router as cashback_router
from app.api.routes.categories import router as categories_router
from app.api.routes.ollama import router as ollama_router
from app.api.routes.pages import build_page_routes
from app.api.routes.state import router as state_router
from app.api.routes.users import router as users_router
from app.core.nats_client import nats_manager
from app.core.config import STATIC_DIR, TEMPLATES_DIR


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    finally:
        await nats_manager.close()


app = FastAPI(title="Cashback Categories", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.include_router(build_page_routes(templates))
app.include_router(state_router)
app.include_router(users_router)
app.include_router(cards_router)
app.include_router(categories_router)
app.include_router(cashback_router)
app.include_router(ollama_router)
