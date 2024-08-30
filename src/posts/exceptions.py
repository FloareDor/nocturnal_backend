from src.exceptions import NotFound, PermissionDenied
from src.posts.constants import ErrorCode


class PostNotFound(NotFound):
    DETAIL = ErrorCode.POST_NOT_FOUND


class UnauthorizedPostAction(PermissionDenied):
    DETAIL = ErrorCode.UNAUTHORIZED_POST_ACTION


class CommentNotFound(NotFound):
    DETAIL = ErrorCode.COMMENT_NOT_FOUND


class LikeAlreadyExists(PermissionDenied):
    DETAIL = ErrorCode.LIKE_ALREADY_EXISTS


class LikeNotFound(NotFound):
    DETAIL = ErrorCode.LIKE_NOT_FOUND
