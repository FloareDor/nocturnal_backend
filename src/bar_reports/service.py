from datetime import datetime
from typing import Optional

from pytz import timezone
from sqlalchemy import UUID, and_, func, insert, select, update
from sqlalchemy.dialects.postgresql import array_agg
from sqlalchemy.ext.asyncio import AsyncConnection

from src.bar_reports.models import BarReport
from src.bar_reports.models import BarReport_Table as BarReport_T
from src.bars.models import Bars_Table as Bars
from src.database import execute, fetch_all, fetch_one


def get_est_date_range():
    est = timezone("US/Eastern")
    now = datetime.now(est)
    # Set the time to midnight (00:00:00) for the start of the day
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # Set the time to 23:59:59 for the end of the day
    end_of_day = start_of_day.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start_of_day, end_of_day


async def create_bar_report(
    report_data: dict, user_id: UUID, db: Optional[AsyncConnection] = None
):
    insert_query = (
        insert(BarReport).values(**report_data, user_id=user_id).returning(BarReport)
    )
    new_report = await fetch_one(insert_query, commit_after=True, connection=db)

    await update_bar_stats(new_report["bar_id"])

    return new_report


async def update_bar_stats(bar_id: int, db: Optional[AsyncConnection] = None):
    start_of_day, end_of_day = get_est_date_range()

    # Get current bar stats
    current_bar_stats = await fetch_one(
        select(Bars).where(Bars.c.id == bar_id), connection=db
    )

    # Convert UTC to EST in the database query
    est_created_at = func.timezone("America/New_York", BarReport_T.c.created_at)

    # Common WHERE clause for all queries
    where_clause = and_(
        BarReport_T.c.bar_id == bar_id,
        est_created_at >= start_of_day,
        est_created_at <= end_of_day,
    )

    # Average line length
    line_length = await fetch_one(
        select(func.avg(BarReport.line_length).label("avg_line_length")).where(
            where_clause
        ),
        connection=db,
    )
    print(line_length, line_length, line_length)
    new_line_length = (
        line_length["avg_line_length"]
        if line_length["avg_line_length"] is not None
        else current_bar_stats["line_length"]
    )

    # Line length category stats
    line_length_stats = await fetch_one(
        select(
            func.mode()
            .within_group(BarReport_T.c.line_length_category)
            .label("mode_line_length_category"),
            array_agg(BarReport_T.c.line_length_category).label(
                "line_length_distribution"
            ),
        ).where(where_clause),
        connection=db,
    )
    print(line_length_stats, line_length_stats, line_length_stats)
    new_line_length_category = (
        line_length_stats["mode_line_length_category"]
        if line_length_stats["mode_line_length_category"] is not None
        else current_bar_stats["line_length_category"]
    )
    new_line_length_distribution = (
        line_length_stats["line_length_distribution"]
        if line_length_stats["line_length_distribution"] is not None
        else current_bar_stats["line_length_distribution"]
    )

    # Cover category stats
    cover_category_stats = await fetch_one(
        select(
            func.mode()
            .within_group(BarReport_T.c.cover_category)
            .label("mode_cover_category"),
            array_agg(BarReport_T.c.cover_category).label(
                "cover_category_distribution"
            ),
        ).where(where_clause),
        connection=db,
    )
    print(cover_category_stats, cover_category_stats)
    new_cover_category = (
        cover_category_stats["mode_cover_category"]
        if cover_category_stats["mode_cover_category"] is not None
        else current_bar_stats["cover_category"]
    )
    new_cover_category_distribution = (
        cover_category_stats["cover_category_distribution"]
        if cover_category_stats["cover_category_distribution"] is not None
        else current_bar_stats["cover_category_distribution"]
    )

    # Average cover price
    cover_price = await fetch_one(
        select(func.avg(BarReport_T.c.cover_price).label("avg_cover_price")).where(
            where_clause
        ),
        connection=db,
    )
    print(cover_price, cover_price, cover_price)
    new_cover_price = (
        cover_price["avg_cover_price"]
        if cover_price["avg_cover_price"] is not None
        else current_bar_stats["cover_price"]
    )

    # Update the bar with the new stats
    update_query = (
        update(Bars)
        .where(Bars.c.id == bar_id)
        .values(
            line_length=new_line_length,
            line_length_category=new_line_length_category,
            line_length_distribution=new_line_length_distribution,
            cover_category=new_cover_category,
            cover_category_distribution=new_cover_category_distribution,
            cover_price=new_cover_price,
        )
    )
    await execute(update_query, commit_after=True, connection=db)


async def get_bar_reports(
    bar_id: int, limit: int = 10, offset: int = 0, db: Optional[AsyncConnection] = None
):
    select_query = (
        select(BarReport)
        .where(BarReport.bar_id == bar_id)
        .order_by(BarReport.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return await fetch_all(select_query)
