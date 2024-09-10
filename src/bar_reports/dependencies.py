from uuid import UUID

from fastapi import Depends

from src.auth.jwt import parse_jwt_user_id
from src.bar_reports.exceptions import OWNBAR
from src.bar_reports.schemas import BarReportCreate
from src.bars.service import get_bar_by_id


async def validate_bar_report(
    report: BarReportCreate,
    user_id: UUID = Depends(parse_jwt_user_id),
) -> UUID:
    bar = await get_bar_by_id(bar_id=report.bar_id)
    print(bar["admin_id"], user_id)
    if bar["admin_id"] == user_id:
        print(bar["admin_id"], user_id)
        raise OWNBAR()
    return user_id
