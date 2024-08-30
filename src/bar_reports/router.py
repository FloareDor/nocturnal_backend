from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import parse_jwt_user_id
from src.bar_reports import service as bar_report_service
from src.bar_reports.schemas import BarReportCreate, BarReportResponse
from src.database import get_db_connection

router = APIRouter()


@router.post("/", response_model=BarReportResponse)
async def create_bar_report(
    report: BarReportCreate,
    user_id: dict = Depends(parse_jwt_user_id),
    db: AsyncSession = Depends(get_db_connection),
):
    return await bar_report_service.create_bar_report(
        report.model_dump(exclude_unset=True), user_id
    )


@router.get("/{bar_id}", response_model=list[BarReportResponse])
async def get_bar_reports(
    bar_id: int,
    limit: int = 10,
    offset: int = 0,
    user_id: dict = Depends(parse_jwt_user_id),
    db: AsyncSession = Depends(get_db_connection),
):
    return await bar_report_service.get_bar_reports(bar_id, limit, offset)
