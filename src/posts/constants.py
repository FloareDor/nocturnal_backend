class ErrorCode:
    POST_NOT_FOUND = "Post not found."
    UNAUTHORIZED_POST_ACTION = (
        "You are not authorized to perform this action on the post."
    )
    COMMENT_NOT_FOUND = "Comment not found."
    LIKE_ALREADY_EXISTS = "You have already liked this post."
    LIKE_NOT_FOUND = "Like not found. You haven't liked this post yet."


class PostLimits:
    MAX_CAPTION_LENGTH = 2200  # Instagram's current limit
    MAX_COMMENTS_PER_POST = 1000  # Arbitrary limit


class CommentLimits:
    MAX_CONTENT_LENGTH = 1000  # Arbitrary limit
