from src.bar_reports.constants import ErrorCode
from src.exceptions import PermissionDenied


class OWNBAR(PermissionDenied):
    DETAIL = ErrorCode.OWN_BAR
