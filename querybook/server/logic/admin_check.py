from app.db import with_session
from models.user import UserRole
from const.user_roles import UserRoleType

@with_session
def is_admin(uid, session=None):
    return session.query(UserRole).filter(
        UserRole.uid == uid, UserRole.role == UserRoleType.ADMIN
    ).count() > 0
