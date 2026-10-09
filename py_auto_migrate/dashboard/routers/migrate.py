from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from py_auto_migrate.dashboard.api import execute_migration
from py_auto_migrate.migrate.mapping import ALL_DATABASES_LIST
from py_auto_migrate.migrate.mapping import SOURCE_ADAPTERS
from py_auto_migrate.cli import get_uri
from py_auto_migrate.dashboard.utils import build_connection
from py_auto_migrate.core.logging import get_logger
from py_auto_migrate.dashboard.jobs import get_job_status, submit_migration


logger = get_logger(__name__)



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


@router.post("/migrate/tables", response_class=JSONResponse)
async def list_source_tables(
    source: str = Form(...),
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
):
    """Fetch source table names for the dashboard picker."""
    try:
        source_data = {
            "host": source_host, "port": source_port, "db_name": source_db_name,
            "username": source_username, "password": source_password,
            "file_path": source_file_path, "service_name": source_service_name,
            "aws_access_key": source_aws_access_key,
            "aws_secret_key": source_aws_secret_key, "region": source_region,
        }
        source_uri = build_connection(source, source_data)
        source_type = get_uri(source_uri)
        adapter = SOURCE_ADAPTERS.get(source_type)
        if adapter is None:
            raise ValueError(f"Unsupported source database: {source}")
        tables = adapter(source_uri).get_tables()
        return JSONResponse({"success": True, "tables": tables})
    except Exception as exc:
        logger.exception("Dashboard could not load source tables")
        return JSONResponse({"success": False, "message": str(exc)}, status_code=400)





@router.post("/migrate", response_class=JSONResponse)
async def migration(
    request: Request,
    source: str = Form(...),
    target: str = Form(...),
    table: str = Form(""),
    ai_ask: str = Form(""),
    ai_model: str = Form(""),
    skip_existing: bool = Form(True),

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

        job_id = submit_migration(
            source=source_ui,
            target=target_ui,
            table=table or None,
            ai_ask=ai_ask or None,
            ai_model=ai_model or None,
            skip_existing=skip_existing,
        )

        return JSONResponse({"success": True, "job_id": job_id})

    except Exception as e:
        logger.exception("Dashboard migration failed")
        return JSONResponse(
            {"success": False, "message": str(e)},
            status_code=400,
        )


@router.get("/migrate/status/{job_id}", response_class=JSONResponse)
async def migration_status(job_id: str):
    status = get_job_status(job_id)
    if status is None:
        return JSONResponse({"message": "Migration job not found"}, status_code=404)
    return JSONResponse(status)
