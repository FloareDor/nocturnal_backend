class ErrorCode:
    FRIENDSHIP_NOT_FOUND = "Friendship not found."
    INVALID_FRIEND_REQUEST = "Invalid friend request."
    INVALID_POINT_TRANSFER = "Invalid point transfer."
    INSUFFICIENT_POINTS = "Insufficient points for transfer."
    UNAUTHORIZED_ACTION = "Unauthorized action on friendship."
    SELF_FRIEND_REQUEST = "You cannot send a friend request to yourself."
    EXISTING_FRIENDSHIP = "A friendship or request already exists between these users."
    SELF_POINT_TRANSFER = "You cannot transfer points to yourself."
    NON_FRIEND_TRANSFER = "You can only transfer points to accepted friends."
    INSUFFICIENT_POINTS_TRANSFER = "Insufficient points for this transfer."


class FriendRequestStatus:
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
