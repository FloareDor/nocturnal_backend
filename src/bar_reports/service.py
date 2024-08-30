from sqlalchemy import UUID, insert, select

from src.bar_reports.models import BarReport_Table as BarReport
from src.database import fetch_all, fetch_one


async def create_bar_report(report_data: dict, user_id: UUID):
    insert_query = (
        insert(BarReport).values(**report_data, user_id=user_id).returning(BarReport)
    )
    return await fetch_one(insert_query, commit_after=True)


async def get_bar_reports(bar_id: int, limit: int = 10, offset: int = 0):
    select_query = (
        select(BarReport)
        .where(BarReport.bar_id == bar_id)
        .order_by(BarReport.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return await fetch_all(select_query)
