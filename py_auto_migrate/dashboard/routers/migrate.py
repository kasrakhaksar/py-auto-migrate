from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from py_auto_migrate.dashboard.api import execute_migration
from py_auto_migrate.migrate.mapping import ALL_DATABASES_LIST
from py_auto_migrate.dashboard.utils import build_connection



router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))



@router.get("/migrate", response_class=HTMLResponse)
async def migrate(request: Request):

    all_database = [database.replace('://' ,'') for database in ALL_DATABASES_LIST]
    
    return templates.TemplateResponse(
        request=request,
        name="migrate.html",
        context={
            "message": None,
            "databases": all_database,
        }
    )





@router.post("/migrate", response_class=HTMLResponse)
async def migration(
    request: Request,
    source: str = Form(...),
    target: str = Form(...),
    table: str = Form(""),
    ai_ask: str = Form(""),
    ai_model: str = Form(""),

    source_host: str = Form(""),
    source_port: str = Form(""),
    source_db_name: str = Form(""),
    source_username: str = Form(""),
    source_password: str = Form(""),
    source_file_path: str = Form(""),
    source_service_name: str = Form(""),
    source_aws_access_key: str = Form(""),
    source_aws_secret_key: str = Form(""),
    source_region: str = Form(""),

    target_host: str = Form(""),
    target_port: str = Form(""),
    target_db_name: str = Form(""),
    target_username: str = Form(""),
    target_password: str = Form(""),
    target_file_path: str = Form(""),
    target_service_name: str = Form(""),
    target_aws_access_key: str = Form(""),
    target_aws_secret_key: str = Form(""),
    target_region: str = Form(""),
    ):


    try:

        source_data = {
            "host": source_host,
            "port": source_port,
            "db_name": source_db_name,
            "username": source_username,
            "password": source_password,
            "file_path": source_file_path,
            "service_name": source_service_name,
            "aws_access_key": source_aws_access_key,
            "aws_secret_key": source_aws_secret_key,
            "region": source_region,
        }

        target_data = {
            "host": target_host,
            "port": target_port,
            "db_name": target_db_name,
            "username": target_username,
            "password": target_password,
            "file_path": target_file_path,
            "service_name": target_service_name,
            "aws_access_key": target_aws_access_key,
            "aws_secret_key": target_aws_secret_key,
            "region": target_region,
        }

        source_ui = build_connection(source, source_data)
        target_ui = build_connection(target, target_data)

        execute_migration(
            source=source_ui,
            target=target_ui,
            table=table or None,
            ai_ask=ai_ask or None,
            ai_model=ai_model or None,
        )

        message = "✅ Migration completed successfully"

    except Exception as e:
        message = f"❌ {str(e)}"

    return templates.TemplateResponse(
        request=request,
        name="migrate.html",
        context={"message": message},
    )