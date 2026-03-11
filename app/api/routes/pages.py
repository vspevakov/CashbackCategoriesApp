from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.services.data_store import load_categories


router = APIRouter()


def build_page_routes(templates: Jinja2Templates) -> APIRouter:
    @router.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"categories": load_categories()},
        )

    @router.get("/summary", response_class=HTMLResponse)
    async def summary_page(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="summary.html",
            context={},
        )

    return router
